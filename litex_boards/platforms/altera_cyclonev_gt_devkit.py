#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2014-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.altera.programmer import USBBlaster

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk
    ("ddr3a_refclk", 0, Pins("AF18"), IOStandard("LVDS")),
    ("ddr_refclk", 0, Pins("W26"), IOStandard("LVDS")),
    ("clk50", 0, Pins("V28"), IOStandard("1.5-V")),
    ("clk125", 0, Subsignal("p", Pins("U31")), Subsignal("n", Pins("U30")), IOStandard("LVDS")),

    # 100MHz programmable between 10-810MHz
    ("clktop", 0, Pins("H19 H18"), IOStandard("LVDS")),
    ("clkbot", 0, Pins("AF18 AG18"), IOStandard("LVDS")),
    ("clkright", 0, Pins("W26 W27"), IOStandard("LVDS")),
    ("refclk_ql1", 0, Pins("AA11 AB10"), IOStandard("LVDS")),
    ("refclk_ql3", 0, Pins("R10 P10"), IOStandard("LVDS")),

    # 148.5MHz programmable between 10-810MHz
    ("refclk_ql2", 0, Pins("U11 T10"), IOStandard("LVDS")),

    ("clkout_sma", 0, Pins("AF33"), IOStandard("2.5-V")),

    ("pcie_refclk", 0, Pins("W11 V10"), IOStandard("LVDS")),

    # PCIe edge connector J16. Quartus assigns the negative transceiver pins
    # implicitly; their package pins are listed in lane order for reference.
    # The clk_p pin is shared with the standalone pcie_refclk resource.
    ("pcie_x4", 0,
        # clk_n: V10
        Subsignal("clk_p",   Pins("W11"), IOStandard("1.4-V PCML")),
        Subsignal("perst_n", Pins("AA22"), IOStandard("1.8 V")),
        # rx_n: AJ1 AG1 AE1 AC1
        Subsignal("rx_p", Pins("AJ2 AG2 AE2 AC2"), IOStandard("1.5-V PCML")),
        # tx_n: AH3 AF3 AD3 AB3
        Subsignal("tx_p", Pins("AH4 AF4 AD4 AB4"), IOStandard("1.5-V PCML")),
    ),
    ("pcie_smbus", 0,
        Subsignal("scl", Pins("AP5")),
        Subsignal("sda", Pins("AJ12")),
        IOStandard("2.5 V"),
    ),
    ("pcie_wake_n", 0, Pins("AP6"), IOStandard("2.5 V")),

    # Leds
    ("user_led", 0, Pins("AM23"), IOStandard("1.5-V")),
    ("user_led", 1, Pins("AE25"), IOStandard("1.5-V")),
    ("user_led", 2, Pins("AK29"), IOStandard("1.5-V")),
    ("user_led", 3, Pins("AL31"), IOStandard("1.5-V")),
    ("user_led", 4, Pins("AF25"), IOStandard("1.5-V")),
    ("user_led", 5, Pins("AJ27"), IOStandard("1.5-V")),
    ("user_led", 6, Pins("AC22"), IOStandard("1.5-V")),
    ("user_led", 7, Pins("AH27"), IOStandard("1.5-V")),

    ("hsma_led", 0, Pins("D12"), IOStandard("2.5-V")),
    ("hsma_led", 1, Pins("B3"), IOStandard("2.5-V")),
    ("hsmb_led", 0, Pins("B30"), IOStandard("2.5-V")),
    ("hsmb_led", 1, Pins("C24"), IOStandard("2.5-V")),

    # PCIe x1 LED
    ("pcie_led", 0, Pins("AK19"), IOStandard("2.5-V")),
    # PCIe x4 LED
    ("pcie_led", 1, Pins("AD22"), IOStandard("2.5-V")),

    # Buttons
    ("key", 0, Pins("AK13"), IOStandard("2.5-V")),
    ("key", 1, Pins("AA15"),  IOStandard("2.5-V")),
    ("key", 2, Pins("AN8"),  IOStandard("2.5-V")),

    # DIP Switches
    ("sw", 0, Pins("H12"),  IOStandard("2.5-V")),
    ("sw", 1, Pins("A2"),  IOStandard("2.5-V")),
    ("sw", 2, Pins("E10"),  IOStandard("2.5-V")),
    ("sw", 3, Pins("D9"),  IOStandard("2.5-V")),
    ("sw", 4, Pins("E9"),  IOStandard("2.5-V")),
    ("sw", 5, Pins("D7"),  IOStandard("2.5-V")),
    ("sw", 6, Pins("E8"),  IOStandard("2.5-V")),
    ("sw", 7, Pins("E7"),  IOStandard("2.5-V")),

    # 2x16 character LCD I2C
    ("lcd", 0,
        Subsignal("scl", Pins("AL6")),
        Subsignal("sda", Pins("AJ10")),
        IOStandard("2.5-V")
    ),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("HSMA:0"), IOStandard("2.5-V")),
        Subsignal("rx", Pins("HSMA:1"),  IOStandard("2.5-V"))
    ),

    # Shared DDR termination reference for DDR3A-only builds.
    ("ddr_rzq", 0, Pins("AP19"), IOStandard("SSTL-15")),

    # DDR3B - four x16 devices on a shared address and command bus
    ("ddram", 0,
        Subsignal("a", Pins(
            "H29 K28 K34 L32 R32 R33 N32 G33 "
            "AE34 L27 V33 U33 T31 T30"
        ), IOStandard("SSTL-15 CLASS I")),

        Subsignal("ba", Pins("J31 N29 P27"), IOStandard("SSTL-15 CLASS I")),
        Subsignal("ras_n",   Pins("Y32"),   IOStandard("SSTL-15 CLASS I")),
        Subsignal("cas_n",   Pins("N27"),   IOStandard("SSTL-15 CLASS I")),
        Subsignal("we_n",    Pins("AM34"),  IOStandard("SSTL-15 CLASS I")),
        Subsignal("cs_n",    Pins("V27"),   IOStandard("SSTL-15 CLASS I")),
        Subsignal("cke",     Pins("AF32"),  IOStandard("SSTL-15 CLASS I")),
        Subsignal("odt",     Pins("AA32"),  IOStandard("SSTL-15 CLASS I")),
        Subsignal("reset_n", Pins("AG31"),  IOStandard("1.5-V")),

        Subsignal("dm", Pins(
            "AE30 AE32 AC34 W34 M33 K32 L31 H28"
        ), IOStandard("SSTL-15 CLASS I")),

        Subsignal("dq", Pins(
            "AF31 AD30 AJ32 AC31 AH32 Y28 AN34 Y27 "
            "AD32 AH33 AB31 AJ34 AA31 AK34 W31 AG33 "
            "AD34 AC33 AG34 AB33 AE33 V32 AH34 W32 "
            "U29 V34 U34 AA33 R34 Y33 P34 U28 "
            "T32 N33 T33 L33 T28 J34 T27 M34 "
            "K33 N31 G34 R28 H33 P32 H34 R27 "
            "N28 L30 P30 K30 J32 H32 M31 H31 "
            "G30 K29 G31 M30 J30 M29 J29 L28"
        ), IOStandard("SSTL-15 CLASS I")),

        Subsignal("dqs_p", Pins("Y29 W29 V24 U24 U23 T25 R23 P24"),
            IOStandard("DIFFERENTIAL 1.5-V SSTL CLASS I")),
        Subsignal("dqs_n", Pins("Y30 W30 V23 U25 T23 R25 R24 P25"),
            IOStandard("DIFFERENTIAL 1.5-V SSTL CLASS I")),

        Subsignal("clk_p", Pins("R30"), IOStandard("DIFFERENTIAL 1.5-V SSTL CLASS I")),
        Subsignal("clk_n", Pins("R29"), IOStandard("DIFFERENTIAL 1.5-V SSTL CLASS I")),
        Subsignal("rzq", Pins("AP19"), IOStandard("SSTL-15")),
    ),

    # DDR3A - 32 data bits plus 8 ECC bits, wired to the hard controller.
    # The reference design shares the AP19 RZQ pin exposed by ddram:0.
    ("ddram", 1,
        Subsignal("a", Pins(
            "AK18 AL18 AM18 AN18 AH17 AJ17 AK17 AL17 "
            "AH16 AJ16 AL16 AM16 AM13 AN13"
        ), IOStandard("SSTL-15 CLASS I")),

        Subsignal("ba",      Pins("AN16 AN17 AP17"), IOStandard("SSTL-15 CLASS I")),
        Subsignal("ras_n",   Pins("AP14"),           IOStandard("SSTL-15 CLASS I")),
        Subsignal("cas_n",   Pins("AP15"),           IOStandard("SSTL-15 CLASS I")),
        Subsignal("we_n",    Pins("AN12"),           IOStandard("SSTL-15 CLASS I")),
        Subsignal("cs_n",    Pins("AA16"),           IOStandard("SSTL-15 CLASS I")),
        Subsignal("cke",     Pins("AP26"),           IOStandard("SSTL-15 CLASS I")),
        Subsignal("odt",     Pins("AN21"),           IOStandard("SSTL-15 CLASS I")),
        Subsignal("reset_n", Pins("AJ22"),           IOStandard("1.5-V")),

        Subsignal("dm", Pins("AL21 AM24 AM28 AL27 AL30"), IOStandard("SSTL-15 CLASS I")),
        Subsignal("dq", Pins(
            "AN19 AM19 AP20 AP21 AH19 AG19 AJ19 AM21 "
            "AM20 AL20 AN22 AN23 AP24 AP25 AN26 AN24 "
            "AP27 AN27 AK22 AJ21 AH21 AH22 AP30 AN28 "
            "AL23 AK23 AL25 AM26 AK24 AJ24 AN31 AL28 "
            "AH23 AG23 AN32 AN29 AK25 AJ25 AK28 AM30"
        ), IOStandard("SSTL-15 CLASS I")),

        Subsignal("dqs_p", Pins("AB19 AD19 AJ20 Y20 AC21"),
            IOStandard("DIFFERENTIAL 1.5-V SSTL CLASS I")),
        Subsignal("dqs_n", Pins("AC19 AE19 AK20 AA20 AD21"),
            IOStandard("DIFFERENTIAL 1.5-V SSTL CLASS I")),

        Subsignal("clk_p", Pins("AA18"), IOStandard("DIFFERENTIAL 1.5-V SSTL CLASS I")),
        Subsignal("clk_n", Pins("AA17"), IOStandard("DIFFERENTIAL 1.5-V SSTL CLASS I")),
    ),

    # Parallel NOR flash on the shared FPGA/MAX V flash bus (Table 2-30).
    # Word address bit 0 corresponds to the board's FSM_A1 net.
    ("parallel_flash", 0,
        Subsignal("a", Pins(
            "AK33 AC27 AB24 AB23 AC28 Y24 Y25 AF27 "
            "AF26 AB28 AE28 AB29 AF28 AH28 AB30 AG29 "
            "AA30 AK30 AJ30 AG30 AN33 AF30 AM33 AK32 "
            "AH31 AD24"
        )),
        Subsignal("dq", Pins(
            "AJ31 AA23 Y23 Y22 W24 AC29 AB25 AA25 "
            "AG28 AH29 AA27 AA28 AL32 AC24 AC23 AL33"
        )),
        Subsignal("adv_n",   Pins("AB34")),
        Subsignal("ce_n",    Pins("AA21")),
        Subsignal("clk",     Pins("AE29")),
        Subsignal("oe_n",    Pins("AG16")),
        Subsignal("rdy_bsy_n", Pins("AD20")),
        Subsignal("reset_n", Pins("AB16")),
        Subsignal("we_n",    Pins("AM14")),
        IOStandard("2.5-V"),
    ),

    # The power-monitor ADC's SPI bus terminates at the MAX V system controller.

    # Optional SDI (Tables 2-25 and 2-27). The board resistor routing selects
    # SDI or HSMA transceiver lane 3. Quartus assigns the negative pins.
    ("sdi", 0,
        Subsignal("tx_p",     Pins("HSMA:17"), IOStandard("1.5-V PCML")),  # tx_n: HSMA:19
        Subsignal("rx_p",     Pins("HSMA:18"), IOStandard("1.5-V PCML")),  # rx_n: HSMA:20
        Subsignal("tx_en",    Pins("AM6"), IOStandard("2.5-V")),
        Subsignal("tx_sd_hdn", Pins("AN5"), IOStandard("2.5-V")),
        Subsignal("rx_bypass", Pins("AM9"), IOStandard("2.5-V")),
        Subsignal("rx_en",    Pins("AN4"), IOStandard("2.5-V")),
    ),

    # Marvell 88E1111 RGMII
    ("eth_clocks", 0,
        Subsignal("tx", Pins("AP7")),
        Subsignal("rx", Pins("AM10")),
        IOStandard("2.5-V"),
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("AN9")),
        Subsignal("mdio",    Pins("AG14")),
        Subsignal("mdc",     Pins("AM8")),
        Subsignal("rx_dv",   Pins("AH14")),
        Subsignal("rx_data", Pins("AK14 AL10 AJ14 AK12")),
        Subsignal("tx_en",   Pins("AC14")),
        Subsignal("tx_data", Pins("AB14 AD15 AB15 AB13")),
        IOStandard("2.5-V"),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

# Table 2-22 uses physical HSMC contact numbers. Select the I/O standard
# for the daughtercard when defining a resource on either connector.
_connectors = [
    ("HSMA", {
        # Preserve the existing debug-header aliases.
        0: "HSMA:39", 1: "HSMA:40", 2: "HSMA:41", 3: "HSMA:42", 4: "HSMA:43", 5: "HSMA:44",
        17: "P4", 18: "R2", 19: "P3", 20: "R1", 21: "T4", 22: "U2",
        23: "T3", 24: "U1", 25: "V4", 26: "W2", 27: "V3", 28: "W1",
        29: "Y4", 30: "AA2", 31: "Y3", 32: "AA1", 33: "K13", 34: "E12",
        39: "F10", 40: "G11", 41: "L12", 42: "F11", 43: "F12", 44: "K12",
        47: "B4", 48: "P14", 49: "A3", 50: "N14", 53: "C9", 54: "M15",
        55: "B9", 56: "M14", 59: "B5", 60: "M13", 61: "A5", 62: "L13",
        65: "A12", 66: "N13", 67: "A11", 68: "N12", 71: "C6", 72: "M16",
        73: "B6", 74: "L17", 77: "C13", 78: "B8", 79: "C12", 80: "A8",
        83: "A7", 84: "J15", 85: "A6", 86: "K14", 89: "C8", 90: "H14",
        91: "C7", 92: "G14", 95: "C1", 96: "G18", 97: "B1", 98: "F18",
        101: "D11", 102: "E15", 103: "D10", 104: "D15", 107: "B10", 108: "F15",
        109: "A10", 110: "G15", 113: "B13", 114: "E18", 115: "A13", 116: "E17",
        119: "C11", 120: "G13", 121: "B11", 122: "H13", 125: "C14", 126: "E14",
        127: "B14", 128: "D14", 131: "F13", 132: "C16", 133: "E13", 134: "B16",
        137: "A17", 138: "D17", 139: "A16", 140: "D16", 143: "B15", 144: "L16",
        145: "A15", 146: "L15", 149: "C18", 150: "F17", 151: "C17", 152: "F16",
        155: "B18", 156: "H17", 157: "A18", 158: "H16", 160: "L11",
    }),
    ("HSMB", {
        17: "F4", 18: "G2", 19: "F3", 20: "G1", 21: "H4", 22: "J2",
        23: "H3", 24: "J1", 25: "K4", 26: "L2", 27: "K3", 28: "L1",
        29: "M4", 30: "N2", 31: "M3", 32: "N1", 33: "L20", 34: "E27",
        39: "D25", 40: "A22", 41: "B24", 42: "A23", 43: "L18", 44: "C21",
        47: "E22", 48: "C27", 49: "G20", 50: "E23", 53: "F20", 54: "B25",
        55: "D24", 56: "A28", 59: "C26", 60: "A26", 61: "G21", 62: "D21",
        65: "F21", 66: "N22", 67: "D27", 68: "M21", 71: "F23", 72: "C28",
        73: "C29", 74: "C23", 77: "E24", 78: "E29", 79: "H21", 80: "D22",
        83: "H22", 84: "D19", 85: "B28", 86: "B21", 89: "D26", 90: "M23",
        91: "F22", 92: "N23", 95: "L22", 96: "K25", 97: "K22", 98: "J25",
        101: "F27", 102: "C31", 103: "G23", 104: "E20", 107: "H23", 108: "B23",
        109: "B31", 110: "L25", 113: "E28", 114: "B19", 115: "D29", 116: "B20",
        119: "D30", 120: "L23", 121: "C32", 122: "K23", 125: "H26", 126: "H27",
        127: "G25", 128: "A21", 131: "G28", 132: "B26", 133: "F25", 134: "A27",
        137: "G29", 138: "D20", 139: "H24", 140: "M19", 143: "G24", 144: "M24",
        145: "F30", 146: "N24", 149: "M18", 150: "C22", 151: "E19", 152: "M25",
        155: "F26", 156: "J20", 157: "G26", 158: "K19", 160: "M20",
    }),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self, toolchain="quartus"):
        AlteraPlatform.__init__(self, "5CGTFD9E5F35C7", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return USBBlaster()

    def do_finalize(self, fragment):
        AlteraPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
        tck = self.lookup_request("altera_reserved_tck", loose=True)
        if tck is not None:
            self.add_period_constraint(tck, 1e9/24e6)
            self.toolchain.additional_sdc_commands.append(
                "set_clock_groups -asynchronous -group [get_clocks altera_reserved_tck]"
            )
