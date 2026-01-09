#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause
#
# Pinout extracted from the official FPGA repository:
#   https://github.com/ModRetro/chromatic_fpga
#
# Handheld overview:
# - FPGA (Gowin GW5A-25 family), clocks: 33.55432MHz (CLK_FPGA), 24MHz, 27MHz.
# - Display interface: 6-bit parallel (DB[5:0]) + DOTCLK/HSYNC/VSYNC/ENABLE + SPI control + TE + PWM backlight.
# - External memory buses: QSPI + PS_* (CE_N/CLK/DQ[7:0]/DQS).
# - I/O: Game Boy cartridge bus, link port, IR, USB FS PHY pins, I2C, audio codec pins, ESP32 control/UART pins.
#

from migen import *

from litex.build.generic_platform import *
from litex.build.gowin.platform import GowinPlatform

from litex.build.gowin.programmer import GowinProgrammer
from litex.build.openfpgaloader   import OpenFPGALoader


# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clocks.
    ("clk_fpga", 0, Pins("M2"),  IOStandard("LVCMOS18")),  # 33.55432MHz
    ("clk_24",   0, Pins("D12"), IOStandard("LVCMOS33")),  # 24MHz
    ("clk_27",   0, Pins("T2"),  IOStandard("LVCMOS33")),  # 27MHz

    # Buttons.
    ("buttons", 0,
        Subsignal("a",          Pins("B8"),  IOStandard("LVCMOS33"), Misc("PULL_MODE=NONE")),
        Subsignal("b",          Pins("A8"),  IOStandard("LVCMOS33"), Misc("PULL_MODE=NONE")),
        Subsignal("dpad_down",  Pins("D11"), IOStandard("LVCMOS33")),
        Subsignal("dpad_left",  Pins("D14"), IOStandard("LVCMOS33")),
        Subsignal("dpad_right", Pins("B16"), IOStandard("LVCMOS33"), Misc("PULL_MODE=NONE")),
        Subsignal("dpad_up",    Pins("L12"), IOStandard("LVCMOS33"), Misc("PULL_MODE=NONE")),
        Subsignal("menu",       Pins("A5"),  IOStandard("LVCMOS33"), Misc("PULL_MODE=NONE")),
        Subsignal("sel",        Pins("C14"), IOStandard("LVCMOS33")),
        Subsignal("start",      Pins("D9"),  IOStandard("LVCMOS33")),
    ),

    # RGB LED.
    ("rgb_led", 0,
        Subsignal("en", Pins("B5"), IOStandard("LVCMOS33")),
        Subsignal("r",  Pins("A6"), IOStandard("LVCMOS33"), Misc("DRIVE=16")),
        Subsignal("g",  Pins("A7"), IOStandard("LVCMOS33"), Misc("DRIVE=16")),
        Subsignal("b",  Pins("B6"), IOStandard("LVCMOS33"), Misc("DRIVE=16")),
    ),

    # Power / USB-C detect.
    ("power", 0,
        Subsignal("on_fpga",   Pins("N8"),  IOStandard("LVCMOS33")),
        Subsignal("down_io",   Pins("P11"), IOStandard("LVCMOS33")),
        Subsignal("vbus_det",  Pins("G15"), IOStandard("LVCMOS33")),
        Subsignal("usbc_flip", Pins("A14"), IOStandard("LVCMOS33")),
    ),

    # ESP32 control.
    ("esp32_ctrl", 0,
        Subsignal("en",  Pins("J3"), IOStandard("LVCMOS33"), Misc("DRIVE=8")),
        Subsignal("io0", Pins("E1"), IOStandard("LVCMOS33"), Misc("DRIVE=8")),
    ),

    # Serial (FPGA <-> ESP32).
    ("serial", 0,
        Subsignal("tx", Pins("D1"), IOStandard("LVCMOS33")),
        Subsignal("rx", Pins("F3"), IOStandard("LVCMOS33")),
    ),

    # Additional ESP32 GPIO UART pair.
    ("esp32_uart0", 0,
        Subsignal("tx", Pins("B4"), IOStandard("LVCMOS33")),
        Subsignal("rx", Pins("A4"), IOStandard("LVCMOS33"), Misc("DRIVE=8")),
    ),

    # QSPI.
    ("qspi", 0,
        Subsignal("cs_n", Pins("C2"), IOStandard("LVCMOS33"), Misc("PULL_MODE=NONE")),
        Subsignal("clk",  Pins("B1"), IOStandard("LVCMOS33"), Misc("PULL_MODE=NONE")),
        Subsignal("mosi", Pins("A2"), IOStandard("LVCMOS33"), Misc("PULL_MODE=NONE")),
        Subsignal("miso", Pins("C3"), IOStandard("LVCMOS33"), Misc("PULL_MODE=NONE")),
        Subsignal("wp_n", Pins("A3"), IOStandard("LVCMOS33"), Misc("PULL_MODE=NONE")),
        Subsignal("hd",   Pins("B3"), IOStandard("LVCMOS33"), Misc("PULL_MODE=NONE")),
    ),

    # External memory interface (PS_*).
    ("ps", 0,
        Subsignal("ce_n", Pins("R1"), IOStandard("SSTL18_I")),
        Subsignal("clk",  Pins("P2"), IOStandard("SSTL18_I")),
        Subsignal("dq",   Pins("L2 N2 J1 L1 K2 M1 N1 P1"), IOStandard("SSTL18_I")),
        Subsignal("dqs",  Pins("K1"), IOStandard("SSTL18_I")),
    ),

    # Cartridge interface.
    ("cart", 0,
        Subsignal("a", Pins(
            "K15 L16 L15 M16 M15 N16 N15 P16 P15 R16 T15 R14 T14 R13 T13 R12"
        ), IOStandard("LVCMOS33"), Misc("DRIVE=4"), Misc("PULL_MODE=NONE")),
        Subsignal("d", Pins(
            "T12 R11 T11 R10 T10 R9 T9 R8"
        ), IOStandard("LVCMOS33"), Misc("DRIVE=8"), Misc("PULL_MODE=NONE")),
        Subsignal("clk",        Pins("J15"), IOStandard("LVCMOS33"), Misc("DRIVE=8"), Misc("PULL_MODE=UP")),
        Subsignal("cs",         Pins("K12"), IOStandard("LVCMOS33"), Misc("DRIVE=8"), Misc("PULL_MODE=NONE")),
        Subsignal("rd",         Pins("J13"), IOStandard("LVCMOS33"), Misc("DRIVE=8"), Misc("PULL_MODE=UP")),
        Subsignal("wr",         Pins("K16"), IOStandard("LVCMOS33"), Misc("DRIVE=8"), Misc("PULL_MODE=UP")),
        Subsignal("rst",        Pins("J16"), IOStandard("LVCMOS33"), Misc("PULL_MODE=UP")),
        Subsignal("data_dir_e", Pins("L7"),  IOStandard("LVCMOS33"), Misc("DRIVE=8"), Misc("PULL_MODE=NONE")),
        Subsignal("det",        Pins("N3"),  IOStandard("LVCMOS33"), Misc("PULL_MODE=UP"), Misc("PULL_STRENGTH=WEAK")),
        Subsignal("audin",      Pins("N14"), IOStandard("LVCMOS33")),
    ),

    # LCD interface.
    ("lcd", 0,
        Subsignal("pwm",     Pins("P3"), IOStandard("LVCMOS33")),
        Subsignal("db",      Pins("M9 R5 M11 T5 N12 T6"), IOStandard("LVCMOS33"), Misc("PULL_MODE=NONE")),
        Subsignal("dotclk",  Pins("P9"),  IOStandard("LVCMOS33"), Misc("PULL_MODE=NONE")),
        Subsignal("enable",  Pins("R4"),  IOStandard("LVCMOS33"), Misc("PULL_MODE=NONE")),
        Subsignal("hsync",   Pins("P8"),  IOStandard("LVCMOS33"), Misc("PULL_MODE=NONE")),
        Subsignal("vsync",   Pins("T3"),  IOStandard("LVCMOS33"), Misc("PULL_MODE=NONE")),
        Subsignal("reset",   Pins("M6"),  IOStandard("LVCMOS33"), Misc("PULL_MODE=NONE")),
        Subsignal("te",      Pins("T7"),  IOStandard("LVCMOS33"), Misc("PULL_MODE=NONE")),
        Subsignal("spi_csx",  Pins("R3"), IOStandard("LVCMOS33"), Misc("PULL_MODE=NONE")),
        Subsignal("spi_sclk", Pins("M7"), IOStandard("LVCMOS33"), Misc("PULL_MODE=NONE")),
        Subsignal("spi_sda",  Pins("T4"), IOStandard("LVCMOS33"), Misc("PULL_MODE=NONE")),
    ),

    # Audio codec pins.
    ("audio_codec", 0,
        Subsignal("bclk",    Pins("B7"),  IOStandard("LVCMOS33"), Misc("DRIVE=16")),
        Subsignal("din",     Pins("C6"),  IOStandard("LVCMOS33"), Misc("DRIVE=16")),
        Subsignal("mclk",    Pins("C8"),  IOStandard("LVCMOS33"), Misc("DRIVE=16"), Misc("PULL_MODE=NONE")),
        Subsignal("reset",   Pins("B9"),  IOStandard("LVCMOS33")),
        Subsignal("wclk",    Pins("D6"),  IOStandard("LVCMOS33"), Misc("DRIVE=16"), Misc("PULL_MODE=NONE")),
        Subsignal("adc_sel", Pins("N13"), IOStandard("LVCMOS33")),
    ),

    # ESP32-facing I2S pins.
    ("i2s", 0,
        Subsignal("bclk", Pins("G1"), IOStandard("LVCMOS33")),
        Subsignal("ws",   Pins("G2"), IOStandard("LVCMOS33")),
        Subsignal("din",  Pins("F1"), IOStandard("LVCMOS33")),
        Subsignal("dout", Pins("F2"), IOStandard("LVCMOS33")),
    ),

    # IR.
    ("ir", 0,
        Subsignal("rx",  Pins("D3"), IOStandard("LVCMOS33")),
        Subsignal("led", Pins("D4"), IOStandard("LVCMOS33"), Misc("DRIVE=16"), Misc("PULL_MODE=NONE")),
    ),

    # Link port.
    ("link", 0,
        Subsignal("clk", Pins("R6"), IOStandard("LVCMOS33")),
        Subsignal("in",  Pins("T8"), IOStandard("LVCMOS33"), Misc("PULL_MODE=NONE")),
        Subsignal("out", Pins("P6"), IOStandard("LVCMOS33"), Misc("PULL_MODE=NONE"), Misc("DRIVE=8")),
        Subsignal("sd",  Pins("R7"), IOStandard("LVCMOS33")),
    ),

    # I2C.
    ("i2c", 0,
        Subsignal("scl", Pins("A15"), IOStandard("LVCMOS33"), Misc("PULL_MODE=UP")),
        Subsignal("sda", Pins("B14"), IOStandard("LVCMOS33"), Misc("PULL_MODE=UP")),
    ),

    # USB FS PHY pins.
    ("usb", 0,
        Subsignal("dxp",     Pins("B11"), IOStandard("LVCMOS33D"), Misc("PULL_MODE=NONE"), Misc("DRIVE=2")),
        Subsignal("dxn",     Pins("A11"), IOStandard("LVCMOS33D"), Misc("PULL_MODE=NONE"), Misc("DRIVE=2")),
        Subsignal("rxdp",    Pins("B12"), IOStandard("LVDS25"),    Misc("PULL_MODE=NONE"), Misc("DRIVE=OFF")),
        Subsignal("rxdn",    Pins("B10"), IOStandard("LVDS25"),    Misc("PULL_MODE=NONE"), Misc("DRIVE=OFF")),
        Subsignal("pullup",  Pins("B13"), IOStandard("LVCMOS33"),  Misc("PULL_MODE=NONE"), Misc("DRIVE=4")),
        Subsignal("term_dp", Pins("A13"), IOStandard("LVCMOS33"),  Misc("PULL_MODE=NONE"), Misc("DRIVE=4")),
        Subsignal("term_dn", Pins("A9"),  IOStandard("LVCMOS33"),  Misc("PULL_MODE=NONE"), Misc("DRIVE=4")),
    ),

    # HDMI pins.
    ("hdmi", 0,
        Subsignal("clk_p", Pins("C15"), IOStandard("LVCMOS33"), Misc("PULL_MODE=NONE")),
        Subsignal("clk_n", Pins("C16"), IOStandard("LVCMOS33"), Misc("PULL_MODE=NONE")),
        Subsignal("d_p",   Pins("D16 E16 F15"), IOStandard("LVCMOS33"), Misc("PULL_MODE=NONE")),
        Subsignal("d_n",   Pins("D15 E15 F16"), IOStandard("LVCMOS33"), Misc("PULL_MODE=NONE")),
        Subsignal("hpd",   Pins("J14"), IOStandard("LVCMOS33"), Misc("PULL_MODE=DOWN")),
        Subsignal("cec",   Pins("G16"), IOStandard("LVCMOS33")),
    ),

    # Battery ADC pins.
    ("vbat_adc", 0,
        Subsignal("p", Pins("P14"), IOStandard("LVCMOS33")),
        Subsignal("n", Pins("L11"), IOStandard("LVCMOS33")),
    ),
]

_connectors = []

# Platform -----------------------------------------------------------------------------------------

class Platform(GowinPlatform):
    default_clk_name   = "clk_fpga"
    default_clk_period = 1e9/33.55432e6  # ns

    def __init__(self, toolchain="gowin", device="GW5A-LV25PG256C1/I0"):
        GowinPlatform.__init__(
            self,
            device     = device,
            io         = _io,
            connectors = _connectors,
            toolchain  = toolchain,
            devicename = "GW5A-25",
        )

        # Bitstream generation options.
        self.toolchain.options["bit_security"] = 0
        self.toolchain.options["bit_encrypt"]  = 0
        self.toolchain.options["bit_compress"] = 0

        # Pin repurposing options.
        self.toolchain.options["use_ready_as_gpio"] = 1
        self.toolchain.options["use_done_as_gpio"]  = 1
        self.toolchain.options["use_mspi_as_gpio"]  = 1
        self.toolchain.options["use_sspi_as_gpio"]  = 1
        self.toolchain.options["use_cpu_as_gpio"]   = 1
        self.toolchain.options["use_i2c_as_gpio"]   = 1

    def create_programmer(self, programmer="openfpgaloader"):
        if programmer == "gowin":
            return GowinProgrammer(self.devicename)
        elif programmer == "openfpgaloader":
            return OpenFPGALoader(cable="gwu2x")
        else:
            raise ValueError(f"Unsupported programmer: {programmer}")

    def do_finalize(self, fragment):
        GowinPlatform.do_finalize(self, fragment)

        self.add_period_constraint(self.lookup_request("clk_fpga", 0), 1e9/33.55432e6)
        self.add_period_constraint(self.lookup_request("clk_24",   0), 1e9/24e6)
        self.add_period_constraint(self.lookup_request("clk_27",   0), 1e9/27e6)
