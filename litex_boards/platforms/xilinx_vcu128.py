#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Fei Gao <feig@princeton.edu>
# Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2022 Jiajie Chen <c@jia.je>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxUSPPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk100_ddr4", 0,
        Subsignal("p", Pins("BH51"), IOStandard("LVDS")),
        Subsignal("n", Pins("BJ51"), IOStandard("LVDS")),
    ),
    ("clk100_qdr4", 0,
        Subsignal("p", Pins("BJ4"), IOStandard("LVDS")),
        Subsignal("n", Pins("BK3"), IOStandard("LVDS")),
    ),
    ("clk100_rld3", 0,
        Subsignal("p", Pins("F35"), IOStandard("LVDS")),
        Subsignal("n", Pins("F36"), IOStandard("LVDS")),
    ),
    ("cpu_reset", 0, Pins("BM29"), IOStandard("LVCMOS12")),

    # Leds
    ("user_led", 0, Pins("BH24"), IOStandard("LVCMOS18")),
    ("user_led", 1, Pins("BG24"), IOStandard("LVCMOS18")),
    ("user_led", 2, Pins("BG25"), IOStandard("LVCMOS18")),
    ("user_led", 3, Pins("BF25"), IOStandard("LVCMOS18")),
    ("user_led", 4, Pins("BF26"), IOStandard("LVCMOS18")),
    ("user_led", 5, Pins("BF27"), IOStandard("LVCMOS18")),
    ("user_led", 6, Pins("BG27"), IOStandard("LVCMOS18")),
    ("user_led", 7, Pins("BG28"), IOStandard("LVCMOS18")),

    # Serial
    ("serial", 0,
        Subsignal("rx",  Pins("BP26"), IOStandard("LVCMOS18")),
        Subsignal("rts", Pins("BP22"), IOStandard("LVCMOS18")),
        Subsignal("tx",  Pins("BN26"), IOStandard("LVCMOS18")),
        Subsignal("cts", Pins("BP23"), IOStandard("LVCMOS18")),
    ),
    ("serial", 1,
        Subsignal("rx",  Pins("BK28"), IOStandard("LVCMOS18")),
        Subsignal("rts", Pins("BL26"), IOStandard("LVCMOS18")),
        Subsignal("tx",  Pins("BJ28"), IOStandard("LVCMOS18")),
        Subsignal("cts", Pins("BL27"), IOStandard("LVCMOS18")),
    ),

    # DDR4 memory
    ("ddram", 0,
        Subsignal("a", Pins(
            "BF50 BD51 BG48 BE50 BE49 BE51 BF53 BG50",
            "BF51 BG47 BF47 BG49 BF48 BF52"),
            IOStandard("SSTL12_DCI")),
        Subsignal("ba",        Pins("BE54 BE53"), IOStandard("SSTL12_DCI")),
        Subsignal("bg",        Pins("BG54"), IOStandard("SSTL12_DCI")),
        Subsignal("ras_n",     Pins("BJ54"), IOStandard("SSTL12_DCI")),
        Subsignal("cas_n",     Pins("BH54"), IOStandard("SSTL12_DCI")),
        Subsignal("we_n",      Pins("BG53"), IOStandard("SSTL12_DCI")),
        Subsignal("cs_n",      Pins("BP49 BK48"), IOStandard("SSTL12_DCI")), # Clam-shell topology
        Subsignal("act_n",     Pins("BG52"), IOStandard("SSTL12_DCI")),
        #Subsignal("ten",       Pins("BJ53"), IOStandard("SSTL12_DCI")),
        #Subsignal("alert_n",   Pins("BJ52"), IOStandard("SSTL12_DCI")),
        #Subsignal("par",       Pins("BL48"), IOStandard("SSTL12_DCI")),
        Subsignal("dm",        Pins(
            "BN42 BL47 BH42 BD41 BM28 BM34 BH32 BG29"),
            IOStandard("POD12_DCI")),
        Subsignal("dq",        Pins(
            "BM45 BP44 BP47 BN45 BM44 BN44 BN47 BP43",
            "BL45 BK44 BL46 BK43 BL43 BJ44 BL42 BJ43",
            "BK41 BG44 BG42 BH44 BH45 BG45 BG43 BJ41",
            "BE43 BF42 BC42 BF43 BD42 BF45 BE44 BF46",
            "BP32 BP29 BP31 BP28 BN32 BM30 BN31 BL30",
            "BL32 BP34 BN34 BK33 BL31 BL33 BM33 BK31",
            "BJ34 BG35 BH34 BH35 BJ33 BF35 BG34 BF36",
            "BF31 BH30 BJ31 BG32 BH31 BF32 BH29 BF33"),
            IOStandard("POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_p",   Pins("BN46 BK45 BH46 BE45 BN29 BL35 BK34 BJ29"),
            IOStandard("DIFF_POD12"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_n",   Pins("BP46 BK46 BJ46 BE46 BN30 BM35 BK35 BK30"),
            IOStandard("DIFF_POD12"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("clk_p",   Pins("BK53"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("clk_n",   Pins("BK54"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("cke",     Pins("BH52"), IOStandard("SSTL12_DCI")),
        Subsignal("odt",     Pins("BH49"), IOStandard("SSTL12_DCI")),
        Subsignal("reset_n", Pins("BH50"), IOStandard("LVCMOS12")),
        Misc("SLEW=FAST"),
    ),

    # SGMII Clock
    ("eth_clocks", 0,
        Subsignal("p", Pins("BH27"), IOStandard("LVDS")),
        Subsignal("n", Pins("BJ27"), IOStandard("LVDS")),
    ),

    # SGMII Ethernet
    ("eth", 0,
        Subsignal("int_n", Pins("BF22"), IOStandard("LVCMOS18")),
        Subsignal("mdio",  Pins("BG23"), IOStandard("LVCMOS18")),
        Subsignal("mdc",   Pins("BN27"), IOStandard("LVCMOS18")),
        Subsignal("col",   Pins("BP27"), IOStandard("LVCMOS18")),
        Subsignal("clkout", Pins("BJ23"), IOStandard("LVCMOS18")),
        Subsignal("rx_p",  Pins("BJ22"), IOStandard("LVDS")),
        Subsignal("rx_n",  Pins("BK21"), IOStandard("LVDS")),
        Subsignal("tx_p",  Pins("BG22"), IOStandard("LVDS")),
        Subsignal("tx_n",  Pins("BH22"), IOStandard("LVDS")),
    ),

    # PCIe
    ("pcie_refclk", 0, # PCIE_CLK2, for GTY bank 227.
        Subsignal("p", Pins("AL15")),
        Subsignal("n", Pins("AL14")),
    ),
    ("pcie_refclk", 1, # PCIE_CLK1, for GTY bank 225.
        Subsignal("p", Pins("AR15")),
        Subsignal("n", Pins("AR14")),
    ),
    ("pcie_x1", 0,
        Subsignal("rst_n",  Pins("BF41"), IOStandard("LVCMOS12")),
        Subsignal("wake_n", Pins("BJ42"), IOStandard("LVCMOS12")),
        Subsignal("clk_p",  Pins("AL15")),
        Subsignal("clk_n",  Pins("AL14")),
        Subsignal("rx_p",   Pins("AL2")),
        Subsignal("rx_n",   Pins("AL1")),
        Subsignal("tx_p",   Pins("AL11")),
        Subsignal("tx_n",   Pins("AL10")),
    ),
    ("pcie_x2", 0,
        Subsignal("rst_n",  Pins("BF41"), IOStandard("LVCMOS12")),
        Subsignal("wake_n", Pins("BJ42"), IOStandard("LVCMOS12")),
        Subsignal("clk_p",  Pins("AL15")),
        Subsignal("clk_n",  Pins("AL14")),
        Subsignal("rx_p",   Pins("AL2 AM4")),
        Subsignal("rx_n",   Pins("AL1 AM3")),
        Subsignal("tx_p",   Pins("AL11 AM9")),
        Subsignal("tx_n",   Pins("AL10 AM8")),
    ),
    ("pcie_x4", 0,
        Subsignal("rst_n",  Pins("BF41"), IOStandard("LVCMOS12")),
        Subsignal("wake_n", Pins("BJ42"), IOStandard("LVCMOS12")),
        Subsignal("clk_p",  Pins("AL15")),
        Subsignal("clk_n",  Pins("AL14")),
        Subsignal("rx_p",   Pins("AL2 AM4 AN6 AN2")),
        Subsignal("rx_n",   Pins("AL1 AM3 AN5 AN1")),
        Subsignal("tx_p",   Pins("AL11 AM9 AN11 AP9")),
        Subsignal("tx_n",   Pins("AL10 AM8 AN10 AP8")),
    ),
    ("pcie_x8", 0,
        Subsignal("rst_n",  Pins("BF41"), IOStandard("LVCMOS12")),
        Subsignal("wake_n", Pins("BJ42"), IOStandard("LVCMOS12")),
        Subsignal("clk_p",  Pins("AL15")),
        Subsignal("clk_n",  Pins("AL14")),
        Subsignal("rx_p",   Pins(
            "AL2 AM4 AN6 AN2",
            "AP4 AR2 AT4 AU2")),
        Subsignal("rx_n",   Pins(
            "AL1 AM3 AN5 AN1",
            "AP3 AR1 AT3 AU1")),
        Subsignal("tx_p",   Pins(
            "AL11 AM9 AN11 AP9",
            "AR11 AR7 AT9 AU11")),
        Subsignal("tx_n",   Pins(
            "AL10 AM8 AN10 AP8",
            "AR10 AR6 AT8 AU10")),
    ),
    ("pcie_x16", 0,
        Subsignal("rst_n",  Pins("BF41"), IOStandard("LVCMOS12")),
        Subsignal("wake_n", Pins("BJ42"), IOStandard("LVCMOS12")),
        Subsignal("clk_p",  Pins("AL15")),
        Subsignal("clk_n",  Pins("AL14")),
        Subsignal("rx_p",   Pins(
            "AL2 AM4 AN6 AN2 AP4 AR2 AT4 AU2",
            "AV4 AW6 AW2 AY4 BA6 BA2 BB4 BC2")),
        Subsignal("rx_n",   Pins(
            "AL1 AM3 AN5 AN1 AP3 AR1 AT3 AU1",
            "AV3 AW5 AW1 AY3 BA5 BA1 BB3 BC1")),
        Subsignal("tx_p",   Pins(
            "AL11 AM9 AN11 AP9 AR11 AR7 AT9 AU11",
            "AU7 AV9 AW11 AY9 BA11 BB9 BC11 BC7")),
        Subsignal("tx_n",   Pins(
            "AL10 AM8 AN10 AP8 AR10 AR6 AT8 AU10",
            "AU6 AV8 AW10 AY8 BA10 BB8 BC10 BC6")),
    ),

    # QSFP28
    ("qsfp", 0,
        Subsignal("clk_p",   Pins("P42")),
        Subsignal("clk_n",   Pins("P43")),
        Subsignal("txp",     Pins("G48 E48 C48 A49")),
        Subsignal("txn",     Pins("G49 E49 C49 A50")),
        Subsignal("rxp",     Pins("G53 F51 E53 D51")),
        Subsignal("rxn",     Pins("G54 F52 E54 D52")),
        Subsignal("modsell", Pins("BM24"), IOStandard("LVCMOS18")),
        Subsignal("resetl",  Pins("BN25"), IOStandard("LVCMOS18")),
        Subsignal("modprsl", Pins("BM25"), IOStandard("LVCMOS18")),
        Subsignal("intl",    Pins("BP24"), IOStandard("LVCMOS18")),
        Subsignal("lpmode",  Pins("BN24"), IOStandard("LVCMOS18")),
    ),
    ("qsfp", 1,
        Subsignal("clk_p",   Pins("T42")),
        Subsignal("clk_n",   Pins("T43")),
        Subsignal("txp",     Pins("L48 L44 K46 J48")),
        Subsignal("txn",     Pins("L49 L45 K47 J49")),
        Subsignal("rxp",     Pins("L53 K51 J53 H51")),
        Subsignal("rxn",     Pins("L54 K52 J54 H52")),
        Subsignal("modsell", Pins("BN5"), IOStandard("LVCMOS12")),
        Subsignal("resetl",  Pins("BN6"), IOStandard("LVCMOS12")),
        Subsignal("modprsl", Pins("BN7"), IOStandard("LVCMOS12")),
        Subsignal("intl",    Pins("BP6"), IOStandard("LVCMOS12")),
        Subsignal("lpmode",  Pins("BP7"), IOStandard("LVCMOS12")),
    ),
    ("qsfp", 2,
        Subsignal("clk_p",   Pins("Y42")),
        Subsignal("clk_n",   Pins("Y43")),
        Subsignal("txp",     Pins("V46 U44 T46 R44")),
        Subsignal("txn",     Pins("V47 U45 T47 R45")),
        Subsignal("rxp",     Pins("U53 U49 T51 R53")),
        Subsignal("rxn",     Pins("U54 U50 T52 R54")),
        Subsignal("modsell", Pins("BM5"), IOStandard("LVCMOS12")),
        Subsignal("resetl",  Pins("BL6"), IOStandard("LVCMOS12")),
        Subsignal("modprsl", Pins("BM7"), IOStandard("LVCMOS12")),
        Subsignal("intl",    Pins("BL7"), IOStandard("LVCMOS12")),
        Subsignal("lpmode",  Pins("BN4"), IOStandard("LVCMOS12")),
    ),
    ("qsfp", 3,
        Subsignal("clk_p",   Pins("AB42")),
        Subsignal("clk_n",   Pins("AB43")),
        Subsignal("txp",     Pins("AA44 Y46 W48 W44")),
        Subsignal("txn",     Pins("AA45 Y47 W49 W45")),
        Subsignal("rxp",     Pins("AA53 Y51 W53 V51")),
        Subsignal("rxn",     Pins("AA54 Y52 W54 V52")),
        Subsignal("modsell", Pins("BK23"), IOStandard("LVCMOS18")),
        Subsignal("resetl",  Pins("BK24"), IOStandard("LVCMOS18")),
        Subsignal("modprsl", Pins("BL22"), IOStandard("LVCMOS18")),
        Subsignal("intl",    Pins("BH21"), IOStandard("LVCMOS18")),
        # UG1302 lists QSFP4_LPMODE_LS on BH21 too; omit until the schematic is checked.
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("FMCP_HSPC", {
        "A2":  "BB51", "A3":  "BB52", "A6":  "BA53", "A7":  "BA54",
        "A10": "BA49", "A11": "BA50", "A14": "AY51", "A15": "AY52",
        "A18": "AW53", "A19": "AW54", "A22": "BC44", "A23": "BC45",
        "A26": "BB46", "A27": "BB47", "A30": "BA44", "A31": "BA45",
        "A34": "AY46", "A35": "AY47", "A38": "AW44", "A39": "AW45",
        "B4":  "AT51", "B5":  "AT52", "B8":  "AU53", "B9":  "AU54",
        "B12": "AV51", "B13": "AV52", "B16": "AW49", "B17": "AW50",
        "B20": "AR40", "B21": "AR41", "B24": "AT46", "B25": "AT47",
        "B28": "AU48", "B29": "AU49", "B32": "AU44", "B33": "AU45",
        "B36": "AV46", "B37": "AV47",

        "C2":  "BC48", "C3":  "BC49", "C6":  "BC53", "C7":  "BC54",
        "C10": "E22",  "C11": "D22",  "C14": "B23",  "C15": "A23",
        "C18": "C23",  "C19": "B22",  "C22": "E19",  "C23": "E18",
        "C26": "E21",  "C27": "D21",
        "D4":  "AV42", "D5":  "AV43", "D8":  "F26",  "D9":  "F25",
        "D11": "H27",  "D12": "G27",  "D14": "E26",  "D15": "D26",
        "D17": "A25",  "D18": "A24",  "D20": "F18",  "D21": "E17",
        "D23": "B21",  "D24": "B20",  "D26": "D17",  "D27": "D16",

        "G2":  "G18",  "G3":  "G17",  "G6":  "E24",  "G7":  "E23",
        "G9":  "B27",  "G10": "A26",  "G12": "E27",  "G13": "D27",
        "G15": "J22",  "G16": "H22",  "G18": "K24",  "G19": "K23",
        "G21": "A21",  "G22": "A20",  "G24": "B16",  "G25": "A16",
        "G27": "D20",  "G28": "D19",  "G30": "H19",  "G31": "H18",
        "G33": "H17",  "G34": "G16",  "G36": "K21",  "G37": "J21",
        "H4":  "F24",  "H5":  "F23",  "H7":  "L23",  "H8":  "K22",
        "H10": "C25",  "H11": "C24",  "H13": "K27",  "H14": "J27",
        "H16": "B26",  "H17": "B25",  "H19": "J26",  "H20": "J25",
        "H22": "B18",  "H23": "B17",  "H25": "A19",  "H26": "A18",
        "H28": "C18",  "H29": "C17",  "H31": "G21",  "H32": "F21",
        "H34": "J20",  "H35": "J19",  "H37": "H20",  "H38": "G20",

        "L4":  "AJ40", "L5":  "AJ41", "L8":  "AL40", "L9":  "AL41",
        "L12": "AN40", "L13": "AN41", "L16": "D25",  "L17": "D24",
        "L20": "H24",  "L21": "H23",  "L24": "G26",  "L25": "G25",
        "L28": "G23",  "L29": "G22",
        "M2":  "AE49", "M3":  "AE50", "M6":  "AE53", "M7":  "AE54",
        "M10": "AF51", "M11": "AF52", "M14": "AG53", "M15": "AG54",
        "M18": "AM46", "M19": "AM47", "M22": "AL44", "M23": "AL45",
        "M26": "AK46", "M27": "AK47", "M30": "AJ48", "M31": "AJ49",
        "M34": "AJ44", "M35": "AJ45", "M38": "AH46", "M39": "AH47",

        "Y2":  "AE44", "Y3":  "AE45", "Y6":  "AG44", "Y7":  "AG45",
        "Y10": "AR53", "Y11": "AR54", "Y14": "AN53", "Y15": "AN54",
        "Y18": "AM51", "Y19": "AM52", "Y22": "AL53", "Y23": "AL54",
        "Y26": "AR44", "Y27": "AR45", "Y30": "AN44", "Y31": "AN45",
        "Y34": "AK51", "Y35": "AK52", "Y38": "AH51", "Y39": "AH52",
        "Z4":  "AF46", "Z5":  "AF47", "Z8":  "AG48", "Z9":  "AG49",
        "Z12": "AP51", "Z13": "AP52", "Z16": "AN49", "Z17": "AN50",
        "Z20": "AG40", "Z21": "AG41", "Z24": "AR48", "Z25": "AR49",
        "Z28": "AP46", "Z29": "AP47", "Z32": "AL49", "Z33": "AL50",
        "Z36": "AJ53", "Z37": "AJ54",
    }),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxUSPPlatform):
    default_clk_name   = "clk100_ddr4"
    default_clk_period = 1e9/100e6

    def __init__(self, toolchain="vivado"):
        XilinxUSPPlatform.__init__(self, "xcvu37p-fsvh2892-2L-e", _io, _connectors, toolchain="vivado")

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment):
        XilinxUSPPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100_ddr4", loose=True), 1e9/100e6)
        self.add_period_constraint(self.lookup_request("clk100_qdr4", loose=True), 1e9/100e6)
        self.add_period_constraint(self.lookup_request("clk100_rld3", loose=True), 1e9/100e6)

        # DDR4 memory Internal Vref
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 64]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 65]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 66]")

        # For HBM2 IP in Vivado 2019.2 (https://www.xilinx.com/support/answers/72607.html)
        self.add_platform_command("connect_debug_port dbg_hub/clk [get_nets apb_clk]")
