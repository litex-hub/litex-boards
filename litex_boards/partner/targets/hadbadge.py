#!/usr/bin/env python3

# This file is Copyright (c) 2018-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# This file is Copyright (c) 2018 David Shah <dave@ds0.me>
# License: BSD

import argparse
import sys

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex_boards.platforms import hadbadge

from litex.soc.cores.clock import *
from litex.soc.integration.soc_sdram import *
#from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

#from .spi_ram_dual import SpiRamDualQuad

from litedram import modules as litedram_modules
from litedram.phy import GENSDRPHY

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    """Clock Resource Generator"

    Input: 8 MHz
    Output: 48 MHz
    """
    def __init__(self, platform, sys_clk_freq):
        self.clock_domains.cd_por = ClockDomain(reset_less=True)
        self.clock_domains.cd_sys = ClockDomain()
        self.clock_domains.cd_clk12 = ClockDomain()
        self.clock_domains.cd_clk48 = ClockDomain()
        self.clock_domains.cd_sys_ps = ClockDomain(reset_less=True)

        # # #

        self.cd_sys.clk.attr.add("keep")
        self.cd_por.clk.attr.add("keep")
        self.cd_clk12.clk.attr.add("keep")
        self.cd_clk48.clk.attr.add("keep")
        self.cd_sys_ps.clk.attr.add("keep")

        self.stop = Signal()

        # clk / rst
        clk8 = platform.request("clk8")
        # rst_n = platform.request("rst_n")
        platform.add_period_constraint(clk8, 1e9/8e6)
        platform.add_period_constraint(self.cd_sys.clk, 1e9/48e6)
        platform.add_period_constraint(self.cd_clk12.clk, 1e9/12e6)
        platform.add_period_constraint(self.cd_clk48.clk, 1e9/48e6)

        # power on reset
        por_count = Signal(16, reset=2**16-1)
        por_done = Signal()
        self.comb += self.cd_por.clk.eq(clk8)
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # pll
        self.submodules.pll = pll = ECP5PLL()
        pll.register_clkin(clk8, 8e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq, phase=0, margin=1e-9)
        pll.create_clkout(self.cd_clk12, 12e6, phase=39, margin=1e-9)
        pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=20)
        self.comb += self.cd_clk48.clk.eq(self.cd_sys.clk)
        # pll.create_clkout(self.cd_sys, 48e6, phase=0, margin=1e-9)
        # pll.create_clkout(self.cd_clk12, 12e6, phase=132, margin=1e-9)

        # sdram clock
        self.comb += platform.request("sdram_clock").eq(self.cd_sys_ps.clk)

        # Synchronize USB48 and USB12, and drive USB12 from USB48
        self.specials += [
            # Instance("ECLKSYNCB",
            #     i_ECLKI=self.cd_usb48_i.clk,
            #     i_STOP=self.stop,
            #     o_ECLKO=self.cd_usb48.clk),
            # Instance("CLKDIVF",
            #     p_DIV="2.0",
            #     i_ALIGNWD=0,
            #     i_CLKI=self.cd_usb48.clk,
            #     i_RST=self.cd_usb48.rst,
            #     o_CDIVX=self.cd_usb12.clk),
            AsyncResetSynchronizer(self.cd_sys, ~por_done | ~pll.locked),# | ~rst_n),
            AsyncResetSynchronizer(self.cd_clk12, ~por_done | ~pll.locked),# | ~rst_n),
            # AsyncResetSynchronizer(self.cd_usb48, ~por_done | ~pll.locked),# | ~rst_n)
        ]

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCSDRAM):
#    SoCCore.csr_map = {
#        "ctrl":           0,  # provided by default (optional)
#        "crg":            1,  # user
#        "uart_phy":       2,  # provided by default (optional)
#        "uart":           3,  # provided by default (optional)
#        "identifier_mem": 4,  # provided by default (optional)
#        "timer0":         5,  # provided by default (optional)
#        "picorvspi":      7,
#        "lcdif":          8,
#        "usb":            9,
#        "reboot":         12,
#        "rgb":            13,
#        "version":        14,
#        "lxspi":          15,
#        "messible":       16,
#    }

    # We must define memory offsets here rather than using the litex
    # defaults.  This is because the mmu only allows for certain
    # regions to be unbuffered:
    # https://github.com/m-labs/VexRiscv-verilog/blob/master/src/main/scala/vexriscv/GenCoreDefault.scala#L139-L143
    SoCSDRAM.mem_map = {
        "rom":          0x00000000,
        "sram":         0x10000000,
        "emulator_ram": 0x20000000,
        "ethmac":       0x30000000,
        "spiflash":     0x50000000,
        "main_ram":     0xc0000000,
        "csr":          0xe0000000,
    }

    def __init__(self, debug=True, sdram_module_cls="AS4C32M8", **kwargs):
        platform = hadbadge.Platform()
        clk_freq = int(48e6)
        SoCSDRAM.__init__(self, platform, clk_freq,
                         integrated_rom_size=16384,
                         integrated_sram_size=65536,
                         wishbone_timeout_cycles=1e9,
                         **kwargs)

        self.submodules.crg = _CRG(self.platform, sys_clk_freq=clk_freq)

        # Add a "Version" module so we can see what version of the board this is.
#        self.submodules.version = Version("proto2", [
#            (0x02, "proto2", "Prototype Version 2 (red)")
#        ], 0)

        # Add a "USB" module to let us debug the device.
#        usb_pads = platform.request("usb")
#        usb_iobuf = usbio.IoBuf(usb_pads.d_p, usb_pads.d_n, usb_pads.pullup)
#        self.submodules.usb = ClockDomainsRenamer({
#            "usb_48": "clk48",
#            "usb_12": "clk12",
#        })(DummyUsb(usb_iobuf, debug=debug, product="Hackaday Supercon Badge", cdc=True))
#
#        if debug:
#            self.add_wb_master(self.usb.debug_bridge.wishbone)
#
#            if self.cpu_type is not None:
#                self.register_mem("vexriscv_debug", 0xb00f0000, self.cpu.debug_bus, 0x200)
#                self.cpu.use_external_variant("rtl/VexRiscv_HaD_Debug.v")
#        elif self.cpu_type is not None:
#            self.cpu.use_external_variant("rtl/VexRiscv_HaD.v")

        # Add the 16 MB SPI flash as XIP memory at address 0x03000000
#        if not is_sim:
#            # flash = SpiFlashDualQuad(platform.request("spiflash4x"), dummy=5)
#            # flash.add_clk_primitive(self.platform.device)
#            # self.submodules.lxspi = flash
#            # self.register_mem("spiflash", 0x03000000, self.lxspi.bus, size=16 * 1024 * 1024)
#            self.submodules.picorvspi = flash = PicoRVSpi(self.platform, pads=platform.request("spiflash"), size=16 * 1024 * 1024)
#            self.register_mem("spiflash", self.mem_map["spiflash"], self.picorvspi.bus, size=self.picorvspi.size)

        # # Add the 16 MB SPI RAM at address 0x40000000 # Value at 40010000: afbfcfef
#        reset_cycles = 2**14-1
#        ram = SpiRamDualQuad(platform.request("spiram4x", 0), platform.request("spiram4x", 1), dummy=5, reset_cycles=reset_cycles, qpi=True)
#        self.submodules.ram = ram
#        self.register_mem("main_ram", self.mem_map["main_ram"], self.ram.bus, size=16 * 1024 * 1024)
        self.submodules.sdrphy = GENSDRPHY(platform.request("sdram"), cl=2)
        sdram_module = getattr(litedram_modules, sdram_module_cls)(clk_freq, "1:1")
        self.register_sdram(self.sdrphy,
                            sdram_module.geom_settings,
                            sdram_module.timing_settings)

        # Let us reboot the device
#        self.submodules.reboot = Reboot(platform.request("programn"))

        # Add a Messible for sending messages to the host
#        self.submodules.messible = Messible()

        # Add an LCD so we can see what's up
#        self.submodules.lcdif = LCDIF(platform.request("lcd"))

        # Ensure timing is correctly set up
        self.platform.toolchain.build_template[1] += " --speed 8" # Add "speed grade 8" to nextpnr-ecp5

        # SAO
#        self.submodules.sao0 = ShittyAddOn(self.platform, self.platform.request("sao", 0),  disable_i2c=kwargs["sao0_disable_i2c"]);
#        self.add_csr("sao0")
#        self.submodules.sao1 = ShittyAddOn(self.platform, self.platform.request("sao", 1),  disable_i2c=kwargs["sao1_disable_i2c"]);
#        self.add_csr("sao1")
#        # PMOD
#        platform.add_extension(_pmod_gpio)
#        self.submodules.pmod = GPIOBidirectional(self.platform.request("pmod_gpio"))
#        self.add_csr("pmod")
#        # GENIO
#        platform.add_extension(_genio_gpio)
#        self.submodules.genio = GPIOBidirectional(self.platform.request("genio_gpio"))
#        self.add_csr("genio")
#        # LEDs
#        self.submodules.led0 = gpio.GPIOOut(self.platform.request("led", 0))
#        self.add_csr("led0")
#        self.submodules.led1 = gpio.GPIOOut(self.platform.request("led", 1))
#        self.add_csr("led1")
#        # Keypad
#        self.submodules.keypad = gpio.GPIOIn(Cat(self.platform.request("keypad", 0).flatten()))
#        self.add_csr("keypad")


# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on Hackaday Badge")
    parser.add_argument("--gateware-toolchain", dest="toolchain", default="trellis",
        help='gateware toolchain to use, diamond or trellis (default)')
    parser.add_argument("--device", dest="device", default="LFE5U-45F",
        help='FPGA device, Hackaday badge is populated with LFE5U-45F')
    parser.add_argument("--sys-clk-freq", default=48e6,
                        help="system clock frequency (default=48MHz)")
    parser.add_argument("--sdram-module", default="MT48LC16M16",
                        help="SDRAM module: MT48LC16M16, AS4C32M16 or AS4C16M16 (default=MT48LC16M16)")
    builder_args(parser)
    soc_sdram_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

#    soc = BaseSoC(device=args.device,
#        sys_clk_freq=int(float(args.sys_clk_freq)),
#        **soc_core_argdict(args))
    soc = BaseSoC(device=args.device, toolchain=args.toolchain,
        sys_clk_freq=int(float(args.sys_clk_freq)),
        sdram_module_cls=args.sdram_module,
        **soc_sdram_argdict(args))

    builder = Builder(soc, **builder_argdict(args))
    builder.build()

if __name__ == "__main__":
    main()
