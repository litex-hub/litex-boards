#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Greg Davill <greg.davill@gmail.com>
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.lattice import LatticePlatform
from litex.build.lattice.programmer import OpenOCDJTAGProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io_r1_0 = [
    # Clk
    ("clk30", 0, Pins("B12"),  IOStandard("LVCMOS33")),

    # Leds
    ("user_led",       0, Pins("C13"), IOStandard("LVCMOS33")),
    ("user_led",       1, Pins("D12"), IOStandard("LVCMOS33")),
    ("user_led",       2, Pins(" U2"), IOStandard("LVCMOS33")),
    ("user_led",       3, Pins(" T3"), IOStandard("LVCMOS33")),
    ("user_led",       4, Pins("D13"), IOStandard("LVCMOS33")),
    ("user_led",       5, Pins("E13"), IOStandard("LVCMOS33")),
    ("user_led",       6, Pins("C16"), IOStandard("LVCMOS33")),
    ("user_led_color", 0, Pins("T1 R1 U1"), IOStandard("LVCMOS33")),

    # Buttons
    ("user_btn", 0, Pins("U16"), IOStandard("SSTL135_I")),
    ("user_btn", 1, Pins("T17"), IOStandard("SSTL135_I")),

    # SPIFlash
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("R2")),
        #Subsignal("clk",  Pins("U3")),
        Subsignal("dq",   Pins("W2 V2 Y2 W1")),
        IOStandard("LVCMOS33")
    ),


    # SDCard
    ("spisdcard", 0,
        Subsignal("clk",  Pins(f"B15")),
        Subsignal("mosi", Pins(f"A13"), Misc("PULLMODE=UP")),
        Subsignal("cs_n", Pins(f"A14"), Misc("PULLMODE=UP")),
        Subsignal("miso", Pins(f"C12"), Misc("PULLMODE=UP")),
        Misc("SLEWRATE=FAST"),
        IOStandard("LVCMOS33"),
    ),
    ("sdcard", 0,
        Subsignal("data", Pins("C12 A12 D14 A14"), Misc("PULLMODE=UP")),
        Subsignal("cmd",  Pins("A13"), Misc("PULLMODE=UP")),
        Subsignal("clk",  Pins("B13")),
        Subsignal("cd",   Pins("B15")),
        Misc("SLEWRATE=FAST"),
        IOStandard("LVCMOS33"),
    ),

    # DDR3 SDRAM
    ("ddram", 0,
        Subsignal("a", Pins(
            "G16 E19 E20 F16 F19 E16 F17 L20 "
            "M20 E18 G18 D18 H18 C18 D17 G20 "),
            IOStandard("SSTL135_I")),
        Subsignal("ba",    Pins("H16 F20 H20"), IOStandard("SSTL135_I")),
        Subsignal("ras_n", Pins("K18"),     IOStandard("SSTL135_I")),
        Subsignal("cas_n", Pins("J17"),     IOStandard("SSTL135_I")),
        Subsignal("we_n",  Pins("G19"),     IOStandard("SSTL135_I")),
        Subsignal("cs_n",  Pins("J20 J16"), IOStandard("SSTL135_I")),
        Subsignal("dm", Pins("U20 L18"), IOStandard("SSTL135_I")),
        Subsignal("dq", Pins(
            "U19 T18 U18 R20 P18 P19 P20 N20",
            "L19 L17 L16 R16 N18 R17 N17 P17"),
            IOStandard("SSTL135_I"),
            Misc("TERMINATION=75")),
        Subsignal("dqs_p", Pins("T19 N16"), IOStandard("SSTL135D_I"),
            Misc("TERMINATION=OFF"),
            Misc("DIFFRESISTOR=100")),
        Subsignal("clk_p",   Pins("C20 J19"), IOStandard("SSTL135D_I")),
        Subsignal("cke",     Pins("F18 J18"), IOStandard("SSTL135_I")),
        Subsignal("odt",     Pins("K20 H17"), IOStandard("SSTL135_I")),
        Subsignal("reset_n", Pins("E17"), IOStandard("SSTL135_I")),
        Misc("SLEWRATE=FAST")
    ),

    # RGMII Ethernet
    ("eth_clocks", 0,
        Subsignal("tx", Pins("E15")),
        Subsignal("rx", Pins("D11")),
        IOStandard("LVCMOS33"),
        Misc("SLEWRATE=FAST"),
    ),

    ("eth", 0,
        Subsignal("rst_n",   Pins("B20")),
        Subsignal("mdio",    Pins("D16")),
        Subsignal("mdc",     Pins("A19")),
        Subsignal("rx_data", Pins("A16 C17 B17 A17")),
        Subsignal("tx_ctl",  Pins("D15")),
        Subsignal("rx_ctl",  Pins("B18")),
        Subsignal("tx_data", Pins("C15 B16 A18 B19")),
        IOStandard("LVCMOS33"),
        Misc("SLEWRATE=FAST")
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors_r1_0 = [
    ("SYZYGY0", {
        # Single ended IOs.
        "S0":"G2",  "S1":"J3",
        "S2":"F1",  "S3":"K3",
        "S4":"J4",  "S5":"K2",
        "S6":"J5",  "S7":"J1",
        "S8":"N2",  "S9":"L3",
        "S10":"M1", "S11":"L2",
        "S12":"N3", "S13":"N4",
        "S14":"M3", "S15":"P5",
        "S16":"H1", "S17":"K5",
        "S18":"K4", "S19":"K1",
        "S20":"L4", "S21":"L1",
        "S22":"L5", "S23":"M4",
        "S24":"N1", "S25":"N5",
        "S26":"P3", "S27":"P4",
        "S28":"H2", "S29":"P1",
        "S30":"G1", "S31":"P2",
        # Diff pairs IOs.
        }
    ),
    ("SYZYGY1", {
        # Single ended IOs.
        # Diff pairs IOs.
        "D0P":"E4", "D0N":"D5",
        "D1P":"A4", "D1N":"A5",
        "D2P":"C4", "D2N":"B4",
        "D3P":"B2", "D3N":"C2",
        "D4P":"A2", "D4N":"B1",
        "D5P":"C1", "D5N":"D1",
        "D6P":"F4", "D6N":"E3",
        "D7P":"D2", "D7N":"E1",
        }
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticePlatform):
    default_clk_name   = "clk30"
    default_clk_period = 1e9/30e6

    def __init__(self, revision="1.0", device="85F", toolchain="trellis", **kwargs):
        assert revision in ["1.0"]
        self.revision = revision
        io         = {"1.0": _io_r1_0}[revision]
        connectors = {"1.0": _connectors_r1_0}[revision]
        LatticePlatform.__init__(self, f"LFE5UM5G-{device}-8BG381C", io, connectors, toolchain=toolchain, **kwargs)

    def create_programmer(self):
        return OpenOCDJTAGProgrammer("openocd_butterstick.cfg")

    def do_finalize(self, fragment):
        LatticePlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk30", loose=True), 1e9/30e6)
