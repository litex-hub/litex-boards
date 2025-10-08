#
# Custom Platform for Kintex-7 with FT232 JTAG and extended peripherals
#

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clock
    ("clk50", 0, Pins("G22"), IOStandard("LVCMOS33")),

    ("user_led", 0, Pins("A23"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("A24"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("D23"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("C24"), IOStandard("LVCMOS33")),
    ("user_led", 4, Pins("C26"), IOStandard("LVCMOS33")),
    ("user_led", 5, Pins("D24"), IOStandard("LVCMOS33")),
    ("user_led", 6, Pins("D25"), IOStandard("LVCMOS33")),
    ("user_led", 7, Pins("E25"), IOStandard("LVCMOS33")),


    ("user_btn", 0, Pins("D26"), IOStandard("LVCMOS33")),
    ("user_btn", 1, Pins("J26"), IOStandard("LVCMOS33")),
    ("user_btn", 2, Pins("E26"), IOStandard("LVCMOS33")),
    ("user_btn", 3, Pins("G26"), IOStandard("LVCMOS33")),
    ("user_btn", 4, Pins("H26"), IOStandard("LVCMOS33")),


    ("serial", 0,
        Subsignal("rx", Pins("B20")),
        Subsignal("tx", Pins("C22")),
        IOStandard("LVCMOS33")
    ),

    # I2C Display
    ("i2c_display", 0,
        Subsignal("scl", Pins("J24"), IOStandard("LVCMOS33")),
        Subsignal("sda", Pins("J25"), IOStandard("LVCMOS33")),
        Subsignal("rst", Pins("J21"), IOStandard("LVCMOS33")),
        Subsignal("dc",  Pins("H22"), IOStandard("LVCMOS33"))
    ),

    # HDMI Outputs
    ("hdmi_out", 0,
        Subsignal("clk_p", Pins("F17")),
        Subsignal("clk_n", Pins("E17")),
        Subsignal("data0_p", Pins("J15")),
        Subsignal("data0_n", Pins("J16")),
        Subsignal("data1_p", Pins("E15")),
        Subsignal("data1_n", Pins("E16")),
        Subsignal("data2_p", Pins("G17")),
        Subsignal("data2_n", Pins("F18")),
        IOStandard("TMDS_33")
    ),

        # HDMI Outputs
    ("hdmi_out", 1,
        Subsignal("clk_p", Pins("E18")),
        Subsignal("clk_n", Pins("D18")),
        Subsignal("data0_p", Pins("D19")),
        Subsignal("data0_n", Pins("D20")),
        Subsignal("data1_p", Pins("H17")),
        Subsignal("data1_n", Pins("H18")),
        Subsignal("data2_p", Pins("G19")),
        Subsignal("data2_n", Pins("F20")),
        IOStandard("TMDS_33")
    ),

    # EEPROM I2C
    ("i2c_eeprom", 0,
        Subsignal("scl", Pins("B21")),
        Subsignal("sda", Pins("C21")),
        IOStandard("LVCMOS33")
    ),

    # SDCard
    ("sdcard", 0,
        Subsignal("miso", Pins("F23")),
        Subsignal("mosi", Pins("G25")),
        Subsignal("sck",  Pins("G24")),
        Subsignal("cs",   Pins("F24")),
        IOStandard("LVCMOS33")
    ),

    # Ethernet 0
    ("eth_clocks", 0,
        Subsignal("tx", Pins("AE10")),
        Subsignal("rx", Pins("AG10")),
        IOStandard("LVCMOS15")
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("AH24"), IOStandard("LVCMOS33")),
        Subsignal("int_n",   Pins("AK16"), IOStandard("LVCMOS18")),
        Subsignal("mdio",    Pins("AG12"), IOStandard("LVCMOS15")),
        Subsignal("mdc",     Pins("AF12"), IOStandard("LVCMOS15")),
        Subsignal("rx_ctl",  Pins("AH11"), IOStandard("LVCMOS15")),
        Subsignal("rx_data", Pins("AJ14 AH14 AK13 AJ13"), IOStandard("LVCMOS15")),
        Subsignal("tx_ctl",  Pins("AK14"), IOStandard("LVCMOS15")),
        Subsignal("tx_data", Pins("AJ12 AK11 AJ11 AK10"), IOStandard("LVCMOS15")),
    ),

    # Ethernet 1 (dummy, example only — replace with real pins if available)
    ("eth", 1,
        Subsignal("rst_n",   Pins("M19"), IOStandard("LVCMOS33")),
        Subsignal("int_n",   Pins("M20"), IOStandard("LVCMOS18")),
        Subsignal("mdio",    Pins("N19"), IOStandard("LVCMOS15")),
        Subsignal("mdc",     Pins("P19"), IOStandard("LVCMOS15")),
        Subsignal("rx_ctl",  Pins("P26"), IOStandard("LVCMOS15")),
        Subsignal("rx_data", Pins("P27 T28 V19 U30"), IOStandard("LVCMOS15")),
        Subsignal("tx_ctl",  Pins("U29"), IOStandard("LVCMOS15")),
        Subsignal("tx_data", Pins("V20 V26 W24 W23"), IOStandard("LVCMOS15")),
    ),

    # PCIe
    ("pcie_x1", 0,
        Subsignal("rst_n", Pins("A12"), IOStandard("LVCMOS18")),
        Subsignal("clk_p", Pins("K6")),
        Subsignal("clk_n", Pins("K5")),
        Subsignal("rx_p",  Pins("J4")),
        Subsignal("rx_n",  Pins("J3")),
        Subsignal("tx_p",  Pins("H2")),
        Subsignal("tx_n",  Pins("H1")),
    ),
    ("pcie_x2", 0,
        Subsignal("rst_n", Pins("A12"), IOStandard("LVCMOS18")),
        Subsignal("clk_p", Pins("K6")),
        Subsignal("clk_n", Pins("K5")),
        Subsignal("rx_p",  Pins("J4 L4")),
        Subsignal("rx_n",  Pins("J3 L3")),
        Subsignal("tx_p",  Pins("H2 K2")),
        Subsignal("tx_n",  Pins("H1 K1")),
    ),
    ("pcie_x4", 0,
        Subsignal("rst_n", Pins("A12"), IOStandard("LVCMOS18")),
        Subsignal("clk_p", Pins("K6")),
        Subsignal("clk_n", Pins("K5")),
        Subsignal("rx_p",  Pins("J4 L4 N4 R4")),
        Subsignal("rx_n",  Pins("J3 L3 N3 R3")),
        Subsignal("tx_p",  Pins("H2 K2 M2 P2")),
        Subsignal("tx_n",  Pins("H1 K1 M1 P1")),
    ),

    ("spiflash4x", 0,  # clock needs to be accessed through STARTUPE2
        Subsignal("cs_n", Pins("C23")),
        Subsignal("clk",  Pins("C8")),
        Subsignal("dq",   Pins("B24", "A25", "B22", "A22")),
        IOStandard("LVCMOS33")
    ),

        # SFP
    ("sfp", 0,
        Subsignal("txp", Pins("D2")),
        Subsignal("txn", Pins("D1")),
        Subsignal("rxp", Pins("E4")),
        Subsignal("rxn", Pins("E3")),
    ),
    ("sfp_tx", 0,
        Subsignal("txp", Pins("D2")),
        Subsignal("txn", Pins("D1")),
    ),
    ("sfp_rx", 0,
        Subsignal("rxp", Pins("E4")),
        Subsignal("rxn", Pins("E3")),
    ),
    ("sfp_tx_disable_n", 0, Pins("H23"), IOStandard("LVCMOS33")),

    # SFP
    ("sfp", 1,
        Subsignal("txp", Pins("B2")),
        Subsignal("txn", Pins("B1")),
        Subsignal("rxp", Pins("C4")),
        Subsignal("rxn", Pins("C3")),
    ),
    ("sfp_tx", 1,
        Subsignal("txp", Pins("B2")),
        Subsignal("txn", Pins("B1")),
    ),
    ("sfp_rx", 1,
        Subsignal("rxp", Pins("C4")),
        Subsignal("rxn", Pins("C3")),
    ),
    ("sfp_tx_disable_n", 1, Pins("H24"), IOStandard("LVCMOS33")),

        # DDR3 SDRAM
    ("ddram", 0,
        Subsignal("a", Pins(
            "AF8 AB10 V9 Y7 AC9 W8 Y11 V8 AA8 AC11",
            "AD9 AA10 AF9 V7 Y8"),
            IOStandard("SSTL15")),
        Subsignal("ba",    Pins("AA7 AB11 AF7"), IOStandard("SSTL15")),
        Subsignal("ras_n", Pins("AD8"), IOStandard("SSTL15")),
        Subsignal("cas_n", Pins("W10"), IOStandard("SSTL15")),
        Subsignal("we_n",  Pins("W9"), IOStandard("SSTL15")),
        Subsignal("cs_n",  Pins("AB7"), IOStandard("SSTL15")),
        Subsignal("dm", Pins("AF15 AA15 AB19 V14"),
            IOStandard("SSTL15")),
        Subsignal("dq", Pins(
            "AF14 AF17 AE15 AE17 AD16 AF20 AD15 AF19",  # dq[0] - dq[7]
            "AB15 AC14 AA18 AA14 AB16 AB14 AA17 AD14",  # dq[8] - dq[15]
            "AD19 AC19 AD18 AA19 AC17 AA20 AC18 AB17",  # dq[16] - dq[23]
            "Y17 V16 V17 W14 V18 W15 V19 W16"           # dq[24] - dq[31]
        ), IOStandard("SSTL15_T_DCI")),
        Subsignal("dqs_p", Pins("AE18 Y15 AD20 W18"),
            IOStandard("DIFF_SSTL15")),
        Subsignal("dqs_n", Pins("AF18 Y16 AE20 W19"),
            IOStandard("DIFF_SSTL15")),
        Subsignal("clk_p", Pins("AA9"), IOStandard("DIFF_SSTL15")),
        Subsignal("clk_n", Pins("AB9"), IOStandard("DIFF_SSTL15")),
        Subsignal("cke",   Pins("AF10"), IOStandard("SSTL15")),
        Subsignal("odt",   Pins("AC8"), IOStandard("SSTL15")),
        Subsignal("reset_n", Pins("Y10"), IOStandard("LVCMOS15")),
        Misc("SLEW=FAST"),
        Misc("VCCAUX_IO=HIGH")
    ),
]

# Connectors ---------------------------------------------------------------------------------------
# GPIOs
_connectors = [
("J1", {
     0: "H14",
     1: "H12",
     2: "H11",
     3: "F14",
     4: "G14",
     5: "F13",
     6: "G12",
     7: "F12",
     8: "G11",
     9: "F10",
    10: "F8",
    11: "A8",
    12: "F9",
    13: "B9",
    14: "D8",
    15: "A9",
    16: "E13",
    17: "C9",
    18: "E10",
    19: "B11",
    20: "E11",
    21: "C11",
    22: "D10",
    23: "C13",
    24: "D9",
    25: "A14",
    26: "D11",
    27: "D14",
    28: "E12",
    29: "B12",
    30: "C12",
    31: "C14",
    32: "D13",
    33: "B14",
}),

]

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self, toolchain="vivado"):
        device = "xc7k325tffg676-2"
        Xilinx7SeriesPlatform.__init__(self, device, _io, _connectors, toolchain=toolchain)
        self.toolchain.bitstream_commands = [
            "set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]",
            "set_property CONFIG_MODE SPIx4 [current_design]",
            "set_property BITSTREAM.CONFIG.CONFIGRATE 50 [current_design]",
            "set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]",
            "set_property BITSTREAM.CONFIG.UNUSEDPIN Pullup [current_design]",
            "set_property CFGBVS VCCO [current_design]",
            "set_property CONFIG_VOLTAGE 3.3 [current_design]",
        ]

    def create_programmer(self):
        return OpenFPGALoader(board="opensourceSDRLabKintex7")

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50",        loose=True), 1e9/50e6)
