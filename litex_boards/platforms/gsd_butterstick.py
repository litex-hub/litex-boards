#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021-2023 Greg Davill <greg.davill@gmail.com>
# Copyright (c) 2021 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause
 
from litex.build.generic_platform import *
from litex.build.lattice import LatticeECP5Platform
from litex.build.lattice.programmer import OpenOCDJTAGProgrammer
from litex.build.dfu import DFUProg

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
        Subsignal("cd",   Pins("B15"), Misc("PULLMODE=UP")),
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

    ("vccio_ctrl", 0, 
        Subsignal("pdm", Pins("V1 E11 T2")),
        Subsignal("en", Pins("E12"))
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

    # USB
    ("ulpi", 0,
        Subsignal("data",  Pins("B9 C6 A7 E9 A8 D9 C10 C7")),
        Subsignal("clk",   Pins("B6")),
        Subsignal("dir",   Pins("A6")),
        Subsignal("nxt",   Pins("B8")),
        Subsignal("stp",   Pins("C8")),
        Subsignal("rst",   Pins("C9")),
        IOStandard("LVCMOS18"),Misc("SLEWRATE=FAST")
    ), 
]

# Connectors ---------------------------------------------------------------------------------------

_connectors_r1_0 = [
    ("SYZYGY0", {
        # Single ended
        "S0": "G2", "S1": "J3",
        "S2": "F1", "S3": "K3",
        "S4": "J4", "S5": "K2",
        "S6": "J5", "S7": "J1",
        "S8": "N2", "S9": "L3",
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
        # Differential
        "D0P": "G2", "D1P": "J3",
        "D0N": "F1", "D1N": "K3",
        "D2P": "J4", "D3P": "K2",
        "D2N": "J5", "D3N": "J1",
        "D4P": "N2", "D5P": "L3",
        "D4N": "M1", "D5N": "L2",
        "D6P": "N3", "D7P": "N4",
        "D6N": "M3", "D7N": "P5",
        # Clks
        "P2C_CLKP": "H2", "C2P_CLKP": "P1",
        "P2C_CLKN": "G1", "C2P_CLKN": "P2",
        }
    ),
    ("SYZYGY1", {
        # Single ended
        "S0": "E4", "S1": "A4", 
        "S2": "D5", "S3": "A5",
        "S4": "C4", "S5": "B2", 
        "S6": "B4", "S7": "C2", 
        "S8": "A2", "S9": "C1", 
        "S10":"B1", "S11":"D1", 
        "S12":"F4", "S13":"D2", 
        "S14":"E3", "S15":"E1", 
        "S16":"B5", "S17":"E5", 
        "S18":"F5", "S19":"C5", 
        "S20":"B3", "S21":"A3", 
        "S22":"D3", "S23":"C3", 
        "S24":"H5", "S25":"G5", 
        "S26":"H3", "S27":"H4", 
        "S28":"G3", "S29":"F2", 
        "S30":"F3", "S31":"E2",
        # Differential
        "D0P": "E4", "D1P": "A4", 
        "D0N": "D5", "D1N": "A5",
        "D2P": "C4", "D3P": "B2", 
        "D2N": "B4", "D3N": "C2", 
        "D4P": "A2", "D5P": "C1", 
        "D4N": "B1", "D5N": "D1", 
        "D6P": "F4", "D7P": "D2", 
        "D6N": "E3", "D7N": "E1", 
        # Clocks
        "P2C_CLKP": "F2", "C2P_CLKP": "G3",
        "P2C_CLKN": "E2", "C2P_CLKN": "F3",
        }
    ),
    ("SYZYGY2", {
        # Single ended
        "S0": "C11", "S1": "B11", 
        "S2": "D6",  "S3": "D7", 
        "S4": "E6",  "S5": "E7", 
        "S6": "D8",  "S7": "E8", 
        "S8": "E10", "S9": "D10", 
        # Clocks
        "P2C_CLKP": "A10", "C2P_CLKP": "A9",
        "P2C_CLKN": "A11", "C2P_CLKN": "B10",

        # Gigabit Transceivers
        "RX0P": "Y5",  "RX1P": "Y7",
        "RX0N": "Y6",  "RX1N": "Y8", 
        "RX2P": "Y14", "RX3P": "Y16",
        "RX2N": "Y15", "RX3N": "Y17", 
        "TX0P": "W4",  "TX1P": "W8",
        "TX0N": "W5",  "TX1N": "W9",
        "TX2P": "W13", "TX3P": "W17",
        "TX2N": "W14", "TX3N": "W18",
        # Gigabit Transceivers reference clock
        "REFCLK0P": "Y11",
        "REFCLK0N": "Y12", 
        }
    ),
]

# SYZYGY -------------------------------------------------------------------------------------------

def raw_syzygy_io(syzygy, iostandard="LVCMOS33"):
    return [(syzygy, 0, Pins(" ".join([f"{syzygy}:S{i:d}" for i in range(32)])), IOStandard(iostandard))]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticeECP5Platform):
    default_clk_name   = "clk30"
    default_clk_period = 1e9/30e6

    def __init__(self, revision="1.0", device="85F", toolchain="trellis", **kwargs):
        assert revision in ["1.0"]
        assert device in ["25F", "45F", "85F"]
        self.revision = revision
        io         = {"1.0": _io_r1_0}[revision]
        connectors = {"1.0": _connectors_r1_0}[revision]
        LatticeECP5Platform.__init__(self, f"LFE5UM5G-{device}-8BG381C", io, connectors, toolchain=toolchain, **kwargs)

    def create_programmer(self, programmer="jtag"):
        if programmer == "jtag":
            return OpenOCDJTAGProgrammer("openocd_butterstick.cfg")
        elif programmer == "dfu":
            return DFUProg(vid="1209", pid="5af1", alt=0)
        else:
            print("Could not program board. " + programmer + " is not a valid argument. Please use 'jtag' or 'dfu'.")

    def do_finalize(self, fragment):
        LatticeECP5Platform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk30", loose=True), 1e9/30e6)
