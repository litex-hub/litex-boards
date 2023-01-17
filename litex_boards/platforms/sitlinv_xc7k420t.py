#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Hans Baier <hansfbaier@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform
from litex.build.openocd import OpenOCD

# Board support for this chinese Kintex 420T board by "SITLINV FPGA Board Store"
# https://www.aliexpress.com/item/1005001631827738.html

# IOs ----------------------------------------------------------------------------------------------

def _get_io(io_standard):
    _io = [
        # Clk / Rst
        ("clk100",      0, Pins("U24"), io_standard),

        ("diffclk100",  0,
            Subsignal("p", Pins("U22"), IOStandard("LVDS_25")),
            Subsignal("n", Pins("U23"), IOStandard("LVDS_25"))
        ),

        # Leds
        ("user_led_n", 0, Pins("A27"),  IOStandard("LVCMOS15")),
        ("user_led_n", 1, Pins("E24"),  IOStandard("LVCMOS15")),
        ("user_led_n", 2, Pins("G24"),  IOStandard("LVCMOS15")),
        ("user_led_n", 3, Pins("H21"),  IOStandard("LVCMOS15")),
        ("user_led_n", 4, Pins("G27"),  IOStandard("LVCMOS15")),
        ("user_led_n", 5, Pins("H26"),  IOStandard("LVCMOS15")),
        ("user_led_n", 6, Pins("H25"),  IOStandard("LVCMOS15")),
        ("user_led_n", 7, Pins("H24"),  IOStandard("LVCMOS15")),

        # Buttons
        ("user_btn_n",  0, Pins("Y23"), IOStandard("LVCMOS15")),
        ("cpu_reset_n", 0, Pins("J24"), IOStandard("LVCMOS15")), # J4 jumper 2.5V or 3.3V

        # I2C / AT24C04
        ("i2c", 0,
            Subsignal("scl", Pins("C17")),
            Subsignal("sda", Pins("C16")),
            IOStandard("LVCMOS33")
        ),

        # Serial
        ("serial", 0,
            Subsignal("tx",  Pins("D16")),  # CH340_TX
            Subsignal("rx",  Pins("D17")),  # CH340_RX
            IOStandard("LVCMOS33")
        ),

        # DDR3 SDRAM near SFP ports
        ("ddram", 0,
            Subsignal("a",     Pins(
                "F28 E29 F26 D29 B29 C30 A30 B28 C29 B30 E30 E26 A28 H29 F25"),
                IOStandard("SSTL15")),
            Subsignal("ba",    Pins("F30 G28 E28"), IOStandard("SSTL15")),
            Subsignal("ras_n", Pins("H27"),  IOStandard("SSTL15")),
            Subsignal("cas_n", Pins("G30"),  IOStandard("SSTL15")),
            Subsignal("we_n",  Pins("G29"),  IOStandard("SSTL15")),
            Subsignal("cs_n",  Pins("H30"),  IOStandard("SSTL15")),
            Subsignal("dm",      Pins(
                "B22 E19 F22 K19 M23 P18 P26 N29"),
                IOStandard("SSTL15")),
            Subsignal("dq",      Pins(
                "A21 A22 A23 B23 B19 C19 A20 B20 C21 D21 C22 D22 E18 D18 E20 E21 " + \
                "G18 F18 G20 F20 H20 G22 G23 F23 L18 J18 J19 K20 J22 H22 K23 J23 " + \
                "N24 N22 P24 P23 L20 M22 M24 N25 M17 N19 N17 P17 N20 N21 P21 P19 " + \
                "K26 K25 L26 L25 M25 N26 P28 P27 L30 M29 P29 R29 K28 K29 K30 M28 "),
                IOStandard("SSTL15")),
            Subsignal("dqs_p",   Pins("B18 E23 H19 K21 L23 M18 N27 N30"),
                IOStandard("DIFF_SSTL15")),
            Subsignal("dqs_n",   Pins("A18 D23 G19 J21 K24 M19 M27 M30"),
                IOStandard("DIFF_SSTL15")),
            Subsignal("clk_p",   Pins("J26"),  IOStandard("DIFF_SSTL15"), Misc("IO_BUFFER_TYPE=NONE")),
            Subsignal("clk_n",   Pins("J27"),  IOStandard("DIFF_SSTL15"), Misc("IO_BUFFER_TYPE=NONE")),
            Subsignal("cke",     Pins("G25"),  IOStandard("SSTL15")),
            Subsignal("odt",     Pins("J28"),  IOStandard("SSTL15")),
            Subsignal("reset_n", Pins("F27"),  IOStandard("LVCMOS15")),
            Misc("SLEW=FAST"),
        ),

        # DDR3 SDRAM near power supply
        ("ddram", 1,
            Subsignal("a",     Pins(
                "AG22 AJ23 AF22 AJ26 AG23 AD23 AF23 AJ24 AE23 AB23 AJ22 AK25 AD21 AD22 AK24"),
                IOStandard("SSTL15")),
            Subsignal("ba",    Pins("AK23 AF21 AC21"), IOStandard("SSTL15")),
            Subsignal("ras_n", Pins("AF20"), IOStandard("SSTL15")),
            Subsignal("cas_n", Pins("AK21"), IOStandard("SSTL15")),
            Subsignal("we_n",  Pins("AJ21"), IOStandard("SSTL15")),
            Subsignal("cs_n",  Pins("AE21"), IOStandard("SSTL15")),
            Subsignal("dm",      Pins(
                "AA28 AA27 AE28 AH30 AB18 AJ19 AD14 AK16"),
                IOStandard("SSTL15")),
            Subsignal("dq",      Pins(
                "W29   Y29 AB30 AB29  W28  W26  Y28 AB28 AA25 AD27 AB24 AC24  Y26  Y25 AA26 AC26 " + \
                "AD29 AE30 AE29 AF30 AD28 AC27 AF28 AF27 AG30 AG29 AH29 AJ29 AK30 AK29 AK28 AG27 " + \
                "AD18 AD19 AA18  Y18 AE18  Y19 AB17 AA17 AH20 AH19 AG19 AF18 AJ18 AK18 AJ17 AJ16 " + \
                "AF16 AE16 AE15 AF15 AC15 AB15 AC14 AB14 AH17 AH16 AK14 AJ14 AF17 AG17 AH15 AH14 "),
                IOStandard("SSTL15")),
            Subsignal("dqs_p",   Pins("Y30 AB25 AC29 AJ27 AC17 AK19 AC16 AG14"),
                IOStandard("DIFF_SSTL15")),
            Subsignal("dqs_n",   Pins("AA30 AC25 AC30 AJ28 AD17 AK20 AD16 AG15"),
                IOStandard("DIFF_SSTL15")),
            Subsignal("clk_p",   Pins("AA22"),  IOStandard("DIFF_SSTL15")),
            Subsignal("clk_n",   Pins("AA23"),  IOStandard("DIFF_SSTL15")),
            Subsignal("cke",     Pins("AB22"),  IOStandard("SSTL15")),
            Subsignal("odt",     Pins("AG20"),  IOStandard("SSTL15")),
            Subsignal("reset_n", Pins("Y21"),   IOStandard("LVCMOS15")),
            Misc("SLEW=FAST"),
        ),

        # Sata
        ("sata", 0,
            Subsignal("rx_p", Pins("C12")),
            Subsignal("rx_n", Pins("C11")),
            Subsignal("tx_p", Pins("A12")),
            Subsignal("tx_n", Pins("A11")),
        ),
        ("sata", 1,
            Subsignal("rx_p", Pins("E12")),
            Subsignal("rx_n", Pins("E11")),
            Subsignal("tx_p", Pins("B10")),
            Subsignal("tx_n", Pins("B9")),
        ),

        # PCIe
        ("pcie_x1", 0,
            Subsignal("rst_n", Pins("W21"), io_standard),
            Subsignal("clk_p", Pins("T6")),
            Subsignal("clk_n", Pins("T5")),
            Subsignal("rx_p",  Pins("P6")),
            Subsignal("rx_n",  Pins("P5")),
            Subsignal("tx_p",  Pins("N4")),
            Subsignal("tx_n",  Pins("N3"))
        ),
        ("pcie_x2", 0,
            Subsignal("rst_n", Pins("W21"), io_standard),
            Subsignal("clk_p", Pins("T6")),
            Subsignal("clk_n", Pins("T5")),
            Subsignal("rx_p",  Pins("")),
            Subsignal("rx_p",  Pins("P6 R4")),
            Subsignal("rx_n",  Pins("P5 R3")),
            Subsignal("tx_p",  Pins("N4 P2")),
            Subsignal("tx_n",  Pins("N3 P1"))
        ),
        ("pcie_x4", 0,
            Subsignal("rst_n", Pins("W21"), io_standard),
            Subsignal("clk_p", Pins("T6")),
            Subsignal("clk_n", Pins("T5")),
            Subsignal("rx_p",  Pins("P6 R4 U4 V6")),
            Subsignal("rx_n",  Pins("P5 R3 U3 V5")),
            Subsignal("tx_p",  Pins("N4 P2 T2 V2")),
            Subsignal("tx_n",  Pins("N3 P1 T1 V1"))
        ),
        ("pcie_x8", 0,
            Subsignal("rst_n", Pins("W21"), io_standard),
            Subsignal("clk_p", Pins("T6")),
            Subsignal("clk_n", Pins("T5")),
            Subsignal("rx_p",  Pins("P6 R4 U4 V6 W4  Y6 AA4 AB6")),
            Subsignal("rx_n",  Pins("P5 R3 U3 V5 W3  Y5 AA3 AB5")),
            Subsignal("tx_p",  Pins("N4 P2 T2 V2 Y2 AB2 AD2 AF2")),
            Subsignal("tx_n",  Pins("N3 P1 T1 V1 Y1 AB1 AD1 AF1"))
        ),


        # SFP A
        ("sfp_a", 0,
            Subsignal("txp", Pins("A8")),
            Subsignal("txn", Pins("A7")),
            Subsignal("rxp", Pins("D10")),
            Subsignal("rxn", Pins("D9")),
            Subsignal("sda", Pins("C15"), io_standard),
            Subsignal("scl", Pins("A15"), io_standard),
        ),
        ("sfp_a_tx", 0,
            Subsignal("p", Pins("A8")),
            Subsignal("n", Pins("A7"))
        ),
        ("sfp_a_rx", 0,
            Subsignal("p", Pins("D10")),
            Subsignal("n", Pins("D9"))
        ),
        ("sfp_a_tx_disable_n", 0, Pins("Y20"), io_standard),

        # SFP B
        ("sfp_b", 0,
            Subsignal("txp", Pins("C8")),
            Subsignal("txn", Pins("C7")),
            Subsignal("rxp", Pins("F10")),
            Subsignal("rxn", Pins("F9")),
            Subsignal("sda", Pins("C14"), io_standard),
            Subsignal("scl", Pins("B14"), io_standard),
        ),
        ("sfp_b_tx", 0,
            Subsignal("p", Pins("C8")),
            Subsignal("n", Pins("C7"))
        ),
        ("sfp_b_rx", 0,
            Subsignal("p", Pins("F10")),
            Subsignal("n", Pins("F9"))
        ),
        ("sfp_b_tx_disable_n", 0, Pins("D14"), io_standard),
    ]

    return _io

# Connectors ---------------------------------------------------------------------------------------

#
#         Connector layout on the board
#   ┌────────────────────────────────────────┐
#   │    2                            80     │
#   │    ┌──────────────────────────────┐    │
#   └──┐ └──────────────────────────────┘ ┌──┘
#      │ 1                            79  │
#      └──────────────────────────────────┘
#
_connectors = [
        # Connector on the SFP side
        ("BTB_A", {
          # 1:  "GND",   2: "GND",
            3:  "A16",   4: "B24",
            5:  "B17",   6: "D24",
          # 7:  "GND",   8: "GND",
            9:  "E16",  10: "A14",
            11: "F16",  12: "B15",
            13: "R25",  14: "U30",
            15: "R24",  16: "U29",
          # 17: "GND",  18: "GND",
            19: "R21",  20: "T27",
            21: "R20",  22: "R26",
            23: "T23",  24: "U28",
            25: "R23",  26: "U27",
          # 27: "GND",  28: "GND",
            29: "T18",  30: "V25",
            31: "T17",  32: "V24",
            33: "V20",  34: "R19",
            35: "U20",  36: "R18",
          # 37: "GND",  38: "GND",
            39: "W23",  40: "T21",
            41: "W22",  42: "T20",
            43: "U18",  44: "V19",
            45: "U17",  46: "U19",
          # 47: "GND",  48: "GND",
            49: "T26",  50: "W17",
            51: "T25",  52: "V17",
            53: "V22",  54: "W19",
            55: "V21",  56: "W18",
          # 57: "GND",  58: "GND",
            59: "C24",  60: "T22",
            61: "D26",  62: "V30",
            63: "C27",  64: "U25",
            65: "B27",  66: "AF25",
          # 67: "GND",  68: "GND"x
            69: "Y24",  70: "AH26",
            71: "AE26", 72: "AG25",
            73: "AD26", 74: "AH25",
          # 75: "GND",  76: "GND"
          # 77: "NC",   78: "3V3"
          # 79: "NC",   80: "3V3"
        }),

        # Connector on the power side
        ("BTB_B", {
          # 1:  "GND",    2: "GND",
            3:  "AJ11",   4: "AK9",
            5:  "AJ12",   6: "AK10",
          # 7:  "GND",    8: "GND",
            9:  "AJ7",    10: "AG11",
            11: "AJ8",    12: "AG12",
          # 13: "GND",    14: "GND",
            15: "AF9",    16: "AG7",
            17: "AF10",   18: "AG8",
          # 19: "GND",    20: "GND",
            21: "AE11",   22: "AH9",
            23: "AE12",   24: "AH10",
          # 25: "GND",    26: "GND",
            27: "AE8",    28: "AF6",
            29: "AE7",    30: "AF5",
          # 31: "GND",    32: "GND",
            33: "AG3",    34: "AK5",
            35: "AG4",    36: "AK6",
          # 37: "GND",    38: "GND",
            39: "AE3",    40: "AH5",
            41: "AE4",    42: "AH6",
          # 43: "GND",    44: "GND",
            45: "AK1",    46: "AJ3",
            47: "AK2",    48: "AJ4",
         #  49: "GND",    50: "GND",
            51: "AC3",    52: "AH1",
            53: "AC4",    54: "AH2",
          # 55: "GND",    56: "GND",
                          58: "AC19",
            59: "L17",    60: "AB19",
          # 61: "GND",    62: "GND",
            63: "AC20",   64: "AB20",
            65: "AE20",   66: "AA20",
          # 67: "GND",    68: "GND",
            69: "W24",    70: "Y20",
                          72: "AA21",
          # 73: "GND",    74: "GND",
          # 75: "NC",     76: "GND",
          # 77: "VCC12V", 78: "VCC3.3V",
          # 79: "VCC12V", 80: "VCC3.3V",
        }),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, io_voltage="3.3V"):
        assert io_voltage in ["2.5V", "3.3V"], "io_voltage must be '2.5V' or '3.3V' acording to the board jumper"
        io_standard = IOStandard("LVCMOS33") if io_voltage == "3.3V" else IOStandard("LVCMOS25")
        _io = _get_io(io_standard)

        Xilinx7SeriesPlatform.__init__(self, "xc7k420t-ffg901-2", _io, _connectors, toolchain="vivado")
        self.add_platform_command("""
        set_property CONFIG_VOLTAGE 3.3 [current_design]
        set_property CFGBVS VCCO [current_design]""")
        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 11]")
        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 12]")
        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 13]")
        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 16]")
        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 17]")

        self.toolchain.bitstream_commands = [
            "set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]",
            "set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]",
            "set_property BITSTREAM.CONFIG.CCLK_TRISTATE TRUE [current_design]",
            "set_property BITSTREAM.CONFIG.CONFIGRATE 66 [current_design]",
            "set_property BITSTREAM.CONFIG.SPI_32BIT_ADDR YES [current_design]",
            "set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]",
            "set_property BITSTREAM.CONFIG.SPI_FALL_EDGE YES [current_design]",
            "set_property BITSTREAM.CONFIG.UNUSEDPIN PULLUP [current_design]",
            ]
        self.toolchain.additional_commands = ["write_cfgmem -force -format bin -interface spix4 -size 32 -loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]

    def create_programmer(self):
        return OpenOCD("openocd_xc7_ft232.cfg", "bscan_spi_xc7a420t.bit")

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100",           loose=True), 1e9/100e6)
        self.add_period_constraint(self.lookup_request("diffclk100",       loose=True), 1e9/100e6)
