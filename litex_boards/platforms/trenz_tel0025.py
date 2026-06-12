#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.lattice import LatticeNexusPlatform
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk25",      0, Pins("G1"), IOStandard("LVCMOS33")), # CLK1_25M.
    ("user_btn_n", 0, Pins("C8"), IOStandard("LVCMOS33"), Misc("PULLMODE=UP")),

    # Leds (RGB LED, active-low).
    ("user_led", 0, Pins("A7"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("A8"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("B8"), IOStandard("LVCMOS33")),
    ("rgb_led", 0,
        Subsignal("r", Pins("A7")),
        Subsignal("g", Pins("A8")),
        Subsignal("b", Pins("B8")),
        IOStandard("LVCMOS33"),
    ),

    # Serial (FT2232H channel A).
    ("serial", 0,
        Subsignal("rx", Pins("D2"), IOStandard("LVCMOS33")), # ADBUS0 / FTDI TXD.
        Subsignal("tx", Pins("B1"), IOStandard("LVCMOS33")), # ADBUS1 / FTDI RXD.
    ),

    # SPI Flash.
    ("spiflash", 0,
        Subsignal("cs_n", Pins("B4")),
        Subsignal("clk",  Pins("B3")),
        Subsignal("mosi", Pins("A4")),
        Subsignal("miso", Pins("A5")),
        Subsignal("wp",   Pins("A6")),
        Subsignal("hold", Pins("B7")),
        IOStandard("LVCMOS33"),
        Misc("SLEWRATE=FAST"),
    ),
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("B4")),
        Subsignal("clk",  Pins("B3")),
        Subsignal("dq",   Pins("A4 A5 A6 B7")),
        IOStandard("LVCMOS33"),
        Misc("SLEWRATE=FAST"),
    ),

    # SDCard.
    ("spisdcard", 0,
        Subsignal("clk",  Pins("A10")),
        Subsignal("mosi", Pins("A12"), Misc("PULLMODE=UP")),
        Subsignal("cs_n", Pins("B12"), Misc("PULLMODE=UP")),
        Subsignal("miso", Pins("B9"),  Misc("PULLMODE=UP")),
        IOStandard("LVCMOS33"),
        Misc("SLEWRATE=FAST"),
    ),
    ("sdcard", 0,
        Subsignal("data", Pins("B9 A9 B13 B12"), Misc("PULLMODE=UP")),
        Subsignal("cmd",  Pins("A12"),           Misc("PULLMODE=UP")),
        Subsignal("clk",  Pins("A10")),
        Subsignal("cd",   Pins("B14"),           Misc("PULLMODE=UP")),
        IOStandard("LVCMOS33"),
        Misc("SLEWRATE=FAST"),
    ),

    # HyperRAM.
    ("hyperram", 0,
        Subsignal("dq",    Pins("M4 K5 N4 K6 L7 P7 N7 M7"), IOStandard("LVCMOS18H")),
        Subsignal("rwds",  Pins("N5"),                      IOStandard("LVCMOS18H")),
        Subsignal("cs_n",  Pins("K4"),                      IOStandard("LVCMOS18H")),
        Subsignal("rst_n", Pins("L4"),                      IOStandard("LVCMOS18H")),
        Subsignal("clk_p", Pins("N6"),                      IOStandard("LVDS")),
        Subsignal("clk_n", Pins("P6"),                      IOStandard("LVDS")),
        Misc("SLEWRATE=FAST"),
    ),

    # CSI control GPIOs / I2C.
    ("csi_i2c", 0,
        Subsignal("sda", Pins("E2"), IOStandard("LVCMOS33"), Misc("PULLMODE=UP")),
        Subsignal("scl", Pins("E1"), IOStandard("LVCMOS33"), Misc("PULLMODE=UP")),
    ),
    ("csi_i2c", 1,
        Subsignal("scl", Pins("G5"), IOStandard("LVCMOS33"), Misc("PULLMODE=UP")),
        Subsignal("sda", Pins("G6"), IOStandard("LVCMOS33"), Misc("PULLMODE=UP")),
    ),
    ("csi_gpio", 0,
        Subsignal("gpio0", Pins("J6")),
        Subsignal("gpio1", Pins("J5")),
        IOStandard("LVCMOS33"),
    ),
    ("csi_gpio", 1,
        Subsignal("gpio0", Pins("H5")),
        Subsignal("gpio1", Pins("H6")),
        IOStandard("LVCMOS33"),
    ),

    # CSI differential lanes, exposed for future video work.
    # Use MIPI_DPHY on P lanes and LVCMOS12H on N lanes, as in Lattice examples.
    ("csi", 0,
        Subsignal("clk_p",  Pins("P11"),             IOStandard("MIPI_DPHY")),
        Subsignal("clk_n",  Pins("N11"),             IOStandard("LVCMOS12H")),
        Subsignal("data_p", Pins("N13 P12 P10 P8"),  IOStandard("MIPI_DPHY")),
        Subsignal("data_n", Pins("N14 P13 N10 N8"),  IOStandard("LVCMOS12H")),
    ),
    ("csi", 1,
        Subsignal("clk_p",  Pins("P9"),             IOStandard("MIPI_DPHY")),
        Subsignal("clk_n",  Pins("N9"),             IOStandard("LVCMOS12H")),
        Subsignal("data_p", Pins("M9 K9 M14 L13"),  IOStandard("MIPI_DPHY")),
        Subsignal("data_n", Pins("L9 K10 M13 L14"), IOStandard("LVCMOS12H")),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    # 2.54mm placeholder headers.
    ("x", "C11 E10 E9 G10 F11 D11 D12 E11 B10 G13 G14 F13 F14 E13 E14 E12 D14 C14 G12 F10"),
    ("y", "D13 C13 C10 C9"),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticeNexusPlatform):
    default_clk_name   = "clk25"
    default_clk_period = 1e9/25e6

    def __init__(self, toolchain="radiant", **kwargs):
        LatticeNexusPlatform.__init__(
            self,
            "LFD2NX-40-7BG196I",
            _io,
            _connectors,
            toolchain=toolchain,
            **kwargs)

        # SPI pins are reused by the LiteSPI core after configuration.
        self.add_platform_command("ldc_set_sysconfig {{MASTER_SPI_PORT=DISABLE}}")

        # Evaluation mode with the free Radiant license.
        if hasattr(self.toolchain, "set_prj_strategy_opts"):
            self.toolchain.set_prj_strategy_opts({"bit_ip_eval": "true"})

    def create_programmer(self, cable="ft2232"):
        return OpenFPGALoader(cable=cable)

    def do_finalize(self, fragment):
        LatticeNexusPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk25", loose=True), 1e9/25e6)
