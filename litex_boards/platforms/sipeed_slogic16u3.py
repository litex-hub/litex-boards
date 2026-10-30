#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025-2026 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# Sipeed SLogic16U3: 16 channels USB3 Logic Analyzer, Gowin GW5AT-LV15MG132C1/I0.
#
# https://wiki.sipeed.com/hardware/en/logic_analyzer/slogic16u3/index.html
#
# Hardware notes (pinout from https://github.com/radiolok/slogic16u3-trace and Gowin PnR dedicated pins
# checks):
# - No fabric clock input: the GW5AT internal oscillator (OSCA) clocks the fabric at power-up, the 125MHz
#   oscillator (enabled by clk125_oe) feeds the GTR12 Q0 REFCLK0 (dedicated A8/A7 pads).
# - USB3: GTR12 Q0 lane 0 (RX A2/A1, TX B3/C3, dedicated pads) through a VL162 Type-C mux (orientation
#   handled by the mux), no USB2 PHY.
# - Inputs: CH0-CH15 through ~0.47 dividers (LVCMOS15UD33: ~0.75V threshold at the pins, ~1.6V at the
#   connector), CH12 (N9) is a global clock input.
# - Configuration SPI Flash (16MB) on the MSPI pins (K13/K14/L14/L13/M14/M13, functions to be identified):
#   application at 0x000000, Sipeed DFU loader (golden image) at 0x800000. The MODE button reconfigures
#   the FPGA from the multiboot address of the running image (0x800000: DFU loader, see add_multiboot).
# - JTAG and UART (F14/E14) on the 8-pin JST SH connector.

from migen import *

from litex.build.generic_platform import *
from litex.build.gowin.platform   import GowinPlatform
from litex.build.gowin.programmer import GowinProgrammer
from litex.build.openfpgaloader   import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Leds.
    ("user_led", 0, Pins("G14"), IOStandard("LVCMOS33")), # Red.

    # Serial (JTAG connector).
    ("serial", 0,
        Subsignal("tx", Pins("F14")),
        Subsignal("rx", Pins("E14")),
        IOStandard("LVCMOS33")
    ),

    # 125MHz Oscillator Enable (GTR12 Q0 REFCLK0).
    ("clk125_oe", 0, Pins("D14"), IOStandard("LVCMOS33")),

    # USB2 D+ Pull-up (to keep disabled: SuperSpeed only).
    ("usb_pullup", 0, Pins("C14"), IOStandard("LVCMOS33")),

    # Logic Analyzer Channels (CH0-CH15).
    ("la", 0,
        Subsignal("ch", Pins(
            "J14 J13 N14 P14 N13 P13 N12 P12 " # CH0-CH7.
            "N11 P11 N10 P10 N9 P9 N8 P8"      # CH8-CH15.
        )),
        IOStandard("LVCMOS15UD33"),
    ),
]

_connectors = [
    ("LA", "J14 J13 N14 P14 N13 P13 N12 P12 N11 P11 N10 P10 N9 P9 N8 P8"),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(GowinPlatform):
    def __init__(self, device_version="B", toolchain="gowin"):
        assert device_version in ["A", "B"] # B: Gowin >= 1.9.12.
        GowinPlatform.__init__(self,
            device     = "GW5AT-LV15MG132C1/I0",
            io         = _io,
            connectors = _connectors,
            toolchain  = toolchain,
            devicename = f"GW5AT-15{device_version}",
        )

        # Bitstream generation options.
        self.toolchain.options["bit_security"] = 0
        self.toolchain.options["bit_encrypt"]  = 0
        self.toolchain.options["bit_compress"] = 0

        # Pin repurposing options (MSPI: Configuration SPI Flash accesses from the fabric).
        self.toolchain.options["use_ready_as_gpio"] = 1
        self.toolchain.options["use_done_as_gpio"]  = 1
        self.toolchain.options["use_mspi_as_gpio"]  = 1
        self.toolchain.options["use_sspi_as_gpio"]  = 1
        self.toolchain.options["use_cpu_as_gpio"]   = 1
        self.toolchain.options["use_i2c_as_gpio"]   = 1

        # Multiboot: MODE button (RECONFIG_N) reloads the Sipeed DFU loader (recovery).
        self.add_multiboot(address=0x800000)

    def add_multiboot(self, address):
        self.toolchain.options["multi_boot"]                  = 1
        self.toolchain.options["multiboot_spi_flash_address"] = f"{address:x}"
        self.toolchain.options["multiboot_address_width"]     = 24

    def create_programmer(self, kit="openfpgaloader"):
        if kit == "gowin":
            return GowinProgrammer(self.devicename, cable=3)
        elif kit == "openfpgaloader":
            return OpenFPGALoader(cable="ft2232")
        else:
            raise ValueError(f"Unsupported programmer kit: {kit}")

    def do_finalize(self, fragment):
        GowinPlatform.do_finalize(self, fragment)
