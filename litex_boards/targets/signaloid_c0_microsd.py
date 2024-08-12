#!/usr/bin/env python3

# Copyright (c) 2024, Signaloid.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

# This target file provides a LiteX SoC for the Signaloid C0-microSD card.
# For a more complete example with more features, automation scripts,
# documentation, and C based firmware compilation, refer to:
# https://github.com/signaloid/C0-microSD-litex


import argparse

from litespi.modules.generated_modules import AT25SL128A
from litespi.opcodes import SpiNorFlashOpCodes
from litex.soc import doc as docs_builder
from litex.soc.cores.ram import Up5kSPRAM
from litex.soc.integration.builder import (
    Builder,
    builder_argdict,
    builder_args,
)
from litex.soc.integration.doc import AutoDoc, ModuleDoc
from litex.soc.integration.soc import (
    ClockDomain,
    Instance,
    Module,
    Signal,
    SoCRegion,
    log2_int,
)
from litex.soc.integration.soc_core import (
    SoCCore,
    soc_core_argdict,
    soc_core_args,
)
from litex.soc.interconnect.csr import AutoCSR, CSRField, CSRStorage
from migen import If
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex_boards.platforms import signaloid_c0_microsd


kB = 1024
MB = 1024 * kB

# USER_DATA_OFFSET is the SPI Flash address of the first byte of the firmware
# binary. It is used as a boot address for the Signaloid C0-microSD card SoC.
#
# The SPI Flash is connected to the Core through the SoC's memory mapped bus.
# Hence, the CPU Reset Address is set to:
# SPI_FLASH_BUS_ADDRESS + USER_DATA_OFFSET
#
# As described on the official Signaloid C0-microSD documentation, the
# USER_DATA_OFFSET defines the start of a 14MiB address space where the
# firmware binary and data can be stored.
#
# More info:
# https://c0-microsd-docs.signaloid.io/hardware-overview/bootloader-addresssing.html
USER_DATA_OFFSET = "0x200000"


class _CRG(Module, AutoDoc):
    """Clock Resource Generator"""

    SYS_FREQ = {
        "48MHz": {
            "sys_clk_freq": 48e6,
            "p_CLKHF_DIV": "0b00",
        },
        "24MHz": {
            "sys_clk_freq": 24e6,
            "p_CLKHF_DIV": "0b01",
        },
        "12MHz": {
            "sys_clk_freq": 12e6,
            "p_CLKHF_DIV": "0b10",
        },
        "6MHz": {
            "sys_clk_freq": 6e6,
            "p_CLKHF_DIV": "0b11",
        },
    }

    def __init__(
        self, sys_clk_cfg: str, platform: signaloid_c0_microsd.Platform
    ) -> None:
        self.clock_domains.cd_sys = ClockDomain(name="sys")
        self.clock_domains.cd_por = ClockDomain(name="por")
        self.clock_domains.cd_clk10khz = ClockDomain(name="clk10khz")

        TARGET_SYS_FREQ = self.SYS_FREQ[sys_clk_cfg]

        # High frequency oscillator (HFSOC) up to 48MHz
        self.specials += Instance(
            "SB_HFOSC",
            p_CLKHF_DIV=TARGET_SYS_FREQ["p_CLKHF_DIV"],
            i_CLKHFEN=0b1,
            i_CLKHFPU=0b1,
            o_CLKHF=self.cd_sys.clk,
        )
        sys_clk_freq = TARGET_SYS_FREQ["sys_clk_freq"]
        platform.add_period_constraint(self.cd_sys.clk, 1e9 / sys_clk_freq)

        # Low frequency oscillator (LFOSC) at 10kHz
        self.specials += Instance(
            "SB_LFOSC",
            i_CLKLFEN=0b1,
            i_CLKLFPU=0b1,
            o_CLKLF=self.cd_clk10khz.clk,
        )

        # Power-on reset: Keep reset active for a few cycles after power on.
        self.reset = Signal()
        por_cycles = 4096
        por_counter = Signal(log2_int(por_cycles), reset=por_cycles - 1)
        self.comb += self.cd_por.clk.eq(self.cd_sys.clk)
        platform.add_period_constraint(self.cd_por.clk, 1e9 / sys_clk_freq)
        self.sync.por += If(
            por_counter != 0,
            por_counter.eq(por_counter - 1),
        )
        self.comb += self.cd_sys.rst.eq(por_counter != 0)
        self.specials += AsyncResetSynchronizer(self.cd_por, self.reset)


class Leds(Module, AutoCSR, AutoDoc):
    """Signaloid C0-microSD LED control"""

    def __init__(self, platform: signaloid_c0_microsd.Platform) -> None:
        self.intro = ModuleDoc(
            """Signaloid C0-microSD LED control.
            Set the LED bit to 1 to turn it on and 0 to turn it off.
            """
        )

        self._out = CSRStorage(
            size=2,
            fields=[
                CSRField(
                    name="red",
                    description="""The Red LED on the Signaloid C0-microSD.
                    On when 1, off when 0.""",
                ),
                CSRField(
                    name="green",
                    description="""The Green LED on the Signaloid C0-microSD.
                    On when 1, off when 0.""",
                ),
            ],
        )

        # Drive the LEDs directly.
        #
        # Driving the LEDs directly from the FPGA is SAFE on
        # the Signaloid C0-microSD, since the LEDs are hard-wired to external
        # current limiting resistors.
        # Hence, for simplicity, the SB_RGBA_DRV hard IP can be omitted.
        #
        # In general, direct drive can lead to overvoltage, and damage to the
        # LEDs and/or the board. Lattice iCE40 mitigates this issue by
        # incorporating the SB_RGBA_DRV hard IP on LEDs without external
        # current limiting resistors.
        #
        # LED driver pins are in an open-drain configuration so they should
        # be inverted to be intuitively controlled through software.
        #
        self.comb += platform.request("led_red").eq(~self._out.storage[0])
        self.comb += platform.request("led_green").eq(~self._out.storage[1])


class BaseSoC(SoCCore):
    """Base SoC for Signaloid C0-microSD"""

    # Statically define the memory map, to prevent it from shifting
    # across various litex versions.
    SoCCore.mem_map = {
        "sram": 0x10000000,
        "spiflash": 0x20000000,
        "csr": 0xF0000000,
        "vexriscv_debug": 0xF00F0000,
    }

    def __init__(
        self,
        platform: signaloid_c0_microsd.Platform,
        sys_clk_cfg: str,
        flash_offset: int,
        add_uart: bool,
        **kwargs
    ) -> None:
        """Extends the SoCCore class to create a BaseSoC with configuration
        for the Signaloid C0-microSD.

        :param sys_clk_cfg: The system clock frequency to use.
        Possible values are defined on the _CRG.SYS_FREQ dict:
        ["48MHz", "24MHz", "12MHz", "6MHz"]
        :type sys_clk_cfg: str

        :param flash_offset: The offset on the SPI Flash's address space where
        the first byte of the firmware binary can be found.
        :type flash_offset: int

        :param add_uart: If set, creates a UART interface on the Signaloid
        C0-microSD's platform serial pins.
        :type add_uart: bool
        """

        self.platform = platform

        # Set cpu name and variant defaults when none are provided
        if "cpu_variant" not in kwargs:
            kwargs["cpu_variant"] = "lite"

        # Force the SRAM size to 0, because we add our own SRAM with SPRAM
        kwargs["integrated_sram_size"] = 0
        kwargs["integrated_rom_size"] = 0

        kwargs["csr_data_width"] = 32

        # Set CPU reset address
        kwargs["cpu_reset_address"] = self.mem_map["spiflash"] + flash_offset

        # If debug is enabled, add a serial port on the Signaloid C0-microSD's
        # platform serial pins.
        if add_uart:
            kwargs["uart_name"] = "serial"

        # SoCCore
        SoCCore.__init__(
            self,
            platform=self.platform,
            clk_freq=_CRG.SYS_FREQ[sys_clk_cfg]["sys_clk_freq"],
            **kwargs
        )

        self.submodules.crg = _CRG(
            sys_clk_cfg=sys_clk_cfg,
            platform=self.platform
        )

        # iCE40-UP5K has a single port RAM, which is a dedicated 128kB block.
        # Use this as CPU RAM.
        spram_size = 128 * kB
        self.submodules.spram = Up5kSPRAM(size=spram_size)
        self.bus.add_slave(
            name="sram",
            slave=self.spram.bus,
            region=SoCRegion(
                origin=self.mem_map["sram"],
                size=spram_size,
                linker=True,
            ),
        )

        # SPI Flash
        # Signaloid C0-microSD uses the AT25QL128A SPI flash with the QPI mode
        # disabled. Hence, the AT25SL128A module is used instead, which is
        # compatible with Signaloid C0-microSD's AT25QL128A with the QPI mode
        # disabled.
        self.add_spi_flash(
            mode="1x",
            module=AT25SL128A(SpiNorFlashOpCodes.READ_1_1_1),
            with_master=False,
        )

        # Add ROM linker region
        self.bus.add_region(
            name="rom",
            region=SoCRegion(
                origin=self.mem_map["spiflash"] + flash_offset,
                size=8 * MB,
                linker=True,
            ),
        )

        # Peripherals
        self.submodules.leds = Leds(self.platform)
        self.add_csr("leds")


class SignaloidC0MicroSDBuilder:
    def __init__(self, platform: signaloid_c0_microsd.Platform) -> None:
        self.platform = platform

        self.parser = argparse.ArgumentParser(
            description="LiteX SoC on Signaloid C0-microSD"
        )

        builder_args(self.parser)
        soc_core_args(self.parser)

        self.parser_target_group = self.parser.add_argument_group(
            title="Target options"
        )
        self.parser_target_group.add_argument(
            "--build", action="store_true", help="Build design."
        )
        self.parser_target_group.add_argument(
            "--sys-clk-cfg",
            default=list(_CRG.SYS_FREQ.keys())[0],
            help="The system clock frequency to use. Possible values are:\n"
            + ", ".join(_CRG.SYS_FREQ.keys()),
        )
        self.parser_target_group.add_argument(
            "--flash-offset",
            default=USER_DATA_OFFSET,
            help="Boot offset in SPI Flash.",
        )
        self.parser_target_group.add_argument(
            "--add-uart",
            action="store_true",
            help="Enable UART interface.",
        )

    @property
    def args(self) -> argparse.Namespace:
        return self.parser.parse_args()

    @property
    def builder_kwargs(self) -> dict:
        return builder_argdict(self.args)

    def get_base_soc(self) -> BaseSoC:
        return BaseSoC(
            platform=self.platform,
            sys_clk_cfg=self.args.sys_clk_cfg,
            flash_offset=int(self.args.flash_offset, 0),
            add_uart=self.args.add_uart,
            **soc_core_argdict(self.args)
        )

    def build(self, soc: BaseSoC) -> None:
        # Create and run the builder
        builder = Builder(soc, **self.builder_kwargs)
        if self.args.build:
            builder.build()

        docs_builder.generate_docs(
            soc,
            "build/documentation/",
            project_name="Signaloid C0-microSD LiteX RISC-V Example SoC",
            author="Signaloid",
        )


def main() -> None:
    builder = SignaloidC0MicroSDBuilder(
        platform=signaloid_c0_microsd.Platform()
    )

    soc = builder.get_base_soc()

    builder.build(soc)


if __name__ == "__main__":
    main()
