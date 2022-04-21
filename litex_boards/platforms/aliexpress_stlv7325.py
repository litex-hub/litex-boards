#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Andrew Gillham <gillham@roadsign.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("cpu_reset_n", 0, Pins("AC16"), IOStandard("LVCMOS15")),
    ("clk100",      0, Pins("F17"), IOStandard("LVCMOS25")),
    ("clk200", 0,
        Subsignal("p", Pins("AB11"), IOStandard("DIFF_SSTL15")),
        Subsignal("n", Pins("AC11"), IOStandard("DIFF_SSTL15"))
    ),
    ("clk156", 0, # TODO verify / test (in docs)
        Subsignal("p", Pins("D6"), IOStandard("LVDS")),
        Subsignal("n", Pins("D5"), IOStandard("LVDS")),
    ),
    ("clk150", 0, # TODO verify / test (in docs)
        Subsignal("p", Pins("F6"), IOStandard("LVDS")),
        Subsignal("n", Pins("F5"), IOStandard("LVDS")),
    ),

    # Leds
    ("user_led_n", 0, Pins("AA2"),  IOStandard("LVCMOS15")),
    ("user_led_n", 1, Pins("AD5"),  IOStandard("LVCMOS15")),
    ("user_led_n", 2, Pins("W10"),  IOStandard("LVCMOS15")),
    ("user_led_n", 3, Pins("Y10"),  IOStandard("LVCMOS15")),
    ("user_led_n", 4, Pins("AE10"), IOStandard("LVCMOS15")),
    ("user_led_n", 5, Pins("W11"),  IOStandard("LVCMOS15")),
    ("user_led_n", 6, Pins("V11"),  IOStandard("LVCMOS15")),
    ("user_led_n", 7, Pins("Y12"),  IOStandard("LVCMOS15")),

    # Buttons
    ("user_btn_n", 0, Pins("AC16"), IOStandard("LVCMOS15")),
    ("user_btn_n", 0, Pins("C24"),  IOStandard("LVCMOS33")), # J4 jumper 2.5V or 3.3V

    # I2C / AT24C04
    ("i2c", 0,
        Subsignal("scl", Pins("U19")),
        Subsignal("sda", Pins("U20")),
        IOStandard("LVCMOS25")
    ),

    # Serial
    ("serial", 0,
        Subsignal("tx",  Pins("M25")),  # CH340_TX
        Subsignal("rx",  Pins("L25")),  # CH340_RX
        IOStandard("LVCMOS25")
    ),

    # DDR3 SDRAM
    ("ddram", 0,
        Subsignal("a",     Pins(
            "AB7  AD11 AA8 AF10  AC7 AE11  AC8 AD8",
            "AC13 AF12 AF9 AD10 AE13  AF7 AB12"),
            IOStandard("SSTL15")),
        Subsignal("ba",    Pins("AE8 AA7 AF13"), IOStandard("SSTL15")),
        Subsignal("ras_n", Pins("Y7"),  IOStandard("SSTL15")),
        Subsignal("cas_n", Pins("AE7"), IOStandard("SSTL15")),
        Subsignal("we_n",  Pins("AF8"),  IOStandard("SSTL15")),
        Subsignal("cs_n",  Pins("AA13"), IOStandard("SSTL15")),
        Subsignal("dm",      Pins(
            "AD16 AB16 AB19 V17 U1 AA3 AD6 AE1"),
            IOStandard("SSTL15")),
        Subsignal("dq",      Pins(
            "AF17 AE17 AF15 AF14 AE15 AD15 AF20 AF19",
            "AA15 AA14 AC14 AD14 AB14 AB15 AA18 AA17",
            "AC18 AD18 AC17 AB17 AA20 AA19 AD19 AC19",
            " W14  V14  V19  V18  V16  W15  W16  Y17",
            "  V4   U6   U5   U2   V3   W3   U7   V6",
            "  Y3   Y2   V2   V1   W1   Y1  AB2  AC2",
            " AA4  AB4  AC4  AC3  AC6  AB6   Y6   Y5",
            " AD4  AD1  AF2  AE2  AE6  AE5  AF3  AE3"),
            IOStandard("SSTL15_T_DCI")),
        Subsignal("dqs_p",   Pins("AE18 Y15 AD20 W18 W6 AB1 AA5 AF5"),
            IOStandard("DIFF_SSTL15")),
        Subsignal("dqs_n",   Pins("AF18 Y16 AE20 W19 W5 AC1 AB5 AF4"),
            IOStandard("DIFF_SSTL15")),
        Subsignal("clk_p",   Pins("AC9"),  IOStandard("DIFF_SSTL15")),
        Subsignal("clk_n",   Pins("AD9"),  IOStandard("DIFF_SSTL15")),
        Subsignal("cke",     Pins("AB9"),  IOStandard("SSTL15")),
        #Subsignal("odt",     Pins("AA12"), IOStandard("SSTL15")),
        Subsignal("reset_n", Pins("AB20"), IOStandard("LVCMOS15")),
        Misc("SLEW=FAST"),
        Misc("VCCAUX_IO=NORMAL")
    ),
    # 2 Rank Signals:
    # Subsignal("cs_n",  Pins("AD13"), IOStandard("SSTL15")),
    # Subsignal("clk_p", Pins("AA10"), IOStandard("DIFF_SSTL15")),
    # Subsignal("clk_n", Pins("AB10"), IOStandard("DIFF_SSTL15")),
    # Subsignal("cke",   Pins("AA9"), IOStandard("SSTL15")),
    # Subsignal("odt",   Pins("Y13"),  IOStandard("SSTL15")),

    ## TODO verify / test
    # # SPIFlash
    # ("spiflash", 0,
    #     Subsignal("cs_n", Pins("C23")),
    #     Subsignal("clk", Pins("C8")),
    #     Subsignal("dq",   Pins("B24 A25 B22 A22")),
    #     IOStandard("LVCMOS25")
    # ),

    # Sata
    ("sata", 0,
        Subsignal("rx_p", Pins("R4")),
        Subsignal("rx_n", Pins("R3")),
        Subsignal("tx_p", Pins("P2")),
        Subsignal("tx_n", Pins("P1")),
        IOStandard("LVCMOS33"),
    ),
    ("sata", 1,
        Subsignal("rx_p", Pins("N4")),
        Subsignal("rx_n", Pins("N3")),
        Subsignal("tx_p", Pins("M2")),
        Subsignal("tx_n", Pins("M1")),
        IOStandard("LVCMOS33"),
    ),

    # SDCard
    ("spisdcard", 0,
        Subsignal("clk",  Pins("N21")),
        Subsignal("cs_n", Pins("P19")),
        Subsignal("mosi", Pins("U21"), Misc("PULLUP")),
        Subsignal("miso", Pins("N16"), Misc("PULLUP")),
        Misc("SLEW=FAST"),
        IOStandard("LVCMOS25")
    ),
    ("sdcard", 0,
        Subsignal("clk", Pins("N21")),
        Subsignal("cmd", Pins("U21"), Misc("PULLUP True")),
        Subsignal("data", Pins("N16 U16 N22 P19"), Misc("PULLUP True")),
        Misc("SLEW=FAST"),
        IOStandard("LVCMOS25")
    ),

    # GMII Ethernet
    ("eth_clocks", 0,
        Subsignal("tx",  Pins("E12"), IOStandard("LVCMOS15")),
        Subsignal("gtx", Pins("F13"), IOStandard("LVCMOS15")),
        Subsignal("rx",  Pins("C12"), IOStandard("LVCMOS15"))
    ),
    ("eth_clocks", 1,
        Subsignal("tx",  Pins("C9"),  IOStandard("LVCMOS15")),
        Subsignal("gtx", Pins("D8"),  IOStandard("LVCMOS15")),
        Subsignal("rx",  Pins("E10"), IOStandard("LVCMOS15"))
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("D11")),
        # Subsignal("int_n",   Pins("")),
        Subsignal("mdio",    Pins("K15")),
        Subsignal("mdc",     Pins("M16")),
        Subsignal("rx_dv",   Pins("G14")),
        Subsignal("rx_er",   Pins("F14")),
        Subsignal("rx_data", Pins("H14 J14 J13 H13 B15 A15 B14 A14")),
        Subsignal("tx_en",   Pins("F12")),
        Subsignal("tx_er",   Pins("E13")),
        Subsignal("tx_data", Pins("G12 E11 G11 C14 D14 C13 C11 D13")),
        Subsignal("col",     Pins("W19")),
        Subsignal("crs",     Pins("R30")),
        IOStandard("LVCMOS15")
    ),
    ("eth", 1,
        Subsignal("rst_n",   Pins("J8")),
        # Subsignal("int_n",   Pins("")),
        Subsignal("mdio",    Pins("G9")),
        Subsignal("mdc",     Pins("H8")),
        Subsignal("rx_dv",   Pins("A12")),
        Subsignal("rx_er",   Pins("D10")),
        Subsignal("rx_data", Pins("A13 B12 B11 A10 B10 A9 B9 A8")),
        Subsignal("tx_en",   Pins("F8")),
        Subsignal("tx_er",   Pins("D9")),
        Subsignal("tx_data", Pins("H11 J11 H9 J10 H12 F10 G10 F9")),
        Subsignal("col",     Pins("W19")),
        Subsignal("crs",     Pins("R30")),
        IOStandard("LVCMOS15")
    ),

    # HDMI out
    ("hdmi_out", 0,
     Subsignal("clk_p", Pins("R21"), IOStandard("TMDS_33")),
     Subsignal("clk_n", Pins("P21"), IOStandard("TMDS_33")),
     Subsignal("data0_p", Pins("N18"), IOStandard("TMDS_33")),
     Subsignal("data0_n", Pins("M19"), IOStandard("TMDS_33")),
     Subsignal("data1_p", Pins("M21"), IOStandard("TMDS_33")),
     Subsignal("data1_n", Pins("M22"), IOStandard("TMDS_33")),
     Subsignal("data2_p", Pins("K25"), IOStandard("TMDS_33")),
     Subsignal("data2_n", Pins("K26"), IOStandard("TMDS_33")),
     Subsignal("scl", Pins("K21"), IOStandard("LVCMOS33")),
     Subsignal("sda", Pins("L23"), IOStandard("LVCMOS33")),
     Subsignal("hdp", Pins("N26"), IOStandard("LVCMOS33")),
     Subsignal("cec", Pins("M26"), IOStandard("LVCMOS33")),
     ),

    # PCIe
    ("pcie_x1", 0,
        Subsignal("rst_n", Pins("E17"), IOStandard("LVCMOS15")),
        Subsignal("clk_p", Pins("H6")),
        Subsignal("clk_n", Pins("H5")),
        Subsignal("rx_p",  Pins("B6")),
        Subsignal("rx_n",  Pins("B5")),
        Subsignal("tx_p",  Pins("A4")),
        Subsignal("tx_n",  Pins("A3"))
    ),
    ("pcie_x2", 0,
        Subsignal("rst_n", Pins("E17"), IOStandard("LVCMOS15")),
        Subsignal("clk_p", Pins("H6")),
        Subsignal("clk_n", Pins("H5")),
        Subsignal("rx_p",  Pins("B6 C4")),
        Subsignal("rx_n",  Pins("B5 C3")),
        Subsignal("tx_p",  Pins("A4 B2")),
        Subsignal("tx_n",  Pins("A3 B1"))
    ),
    ("pcie_x4", 0,
        Subsignal("rst_n", Pins("E17"), IOStandard("LVCMOS15")),
        Subsignal("clk_p", Pins("H6")),
        Subsignal("clk_n", Pins("H5")),
        Subsignal("rx_p",  Pins("B6 C4 E4 G4")),
        Subsignal("rx_n",  Pins("B5 C3 E3 G3")),
        Subsignal("tx_p",  Pins("A4 B2 D2 F2")),
        Subsignal("tx_n",  Pins("A3 B1 D1 F1"))
    ),

    # TODO find / test
    # # SGMII Clk
    # ("sgmii_clock", 0,
    #     Subsignal("p", Pins("")),
    #     Subsignal("n", Pins(""))
    # ),

    # SFP
    ("sfp_a", 0,  # SFP A
        Subsignal("txp", Pins("H2")),
        Subsignal("txn", Pins("H1")),
        Subsignal("rxp", Pins("J4")),
        Subsignal("rxn", Pins("J3")),
        Subsignal("sda", Pins("B21")),
        Subsignal("scl", Pins("C21")),
    ),
    ("sfp_a_tx", 0,  # SFP A
        Subsignal("p", Pins("H2")),
        Subsignal("n", Pins("H1"))
    ),
    ("sfp_a_rx", 0,  # SFP A
        Subsignal("p", Pins("J4")),
        Subsignal("n", Pins("J3"))
    ),
    ("sfp_b", 0,  # SFP B
        Subsignal("txp", Pins("K2")),
        Subsignal("txn", Pins("K1")),
        Subsignal("rxp", Pins("L4")),
        Subsignal("rxn", Pins("L3")),
        Subsignal("sda", Pins("D21")),
        Subsignal("scl", Pins("C22")),
     ),
    ("sfp_b_tx", 0,  # SFP B
        Subsignal("p", Pins("K2")),
        Subsignal("n", Pins("K1"))
    ),
    ("sfp_b_rx", 0,  # SFP B
        Subsignal("p", Pins("L4")),
        Subsignal("n", Pins("L3"))
    ),

    # SI5338 (optional part per seller?)
    ("si5338_i2c", 0,
        Subsignal("sck", Pins("U19"), IOStandard("LVCMOS25")),
        Subsignal("sda", Pins("U20"), IOStandard("LVCMOS25"))
    ),
    ("si5338_clkin", 0,  # CLK2A/B
        Subsignal("p", Pins("K6"), IOStandard("LVDS_25")),
        Subsignal("n", Pins("K5"), IOStandard("LVDS_25"))
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    # TODO; add FMC / BTB
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "clk200"
    default_clk_period = 1e9/200e6

    def __init__(self):
        XilinxPlatform.__init__(self, "xc7k325t-ffg676-2", _io, _connectors, toolchain="vivado")
        self.add_platform_command("""
set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 2.5 [current_design]
""")
        self.toolchain.bitstream_commands = ["set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]"]
        self.toolchain.additional_commands = ["write_cfgmem -force -format bin -interface spix4 -size 16 -loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]

    def create_programmer(self):
        return OpenOCD("openocd_xc7_ft232.cfg", "bscan_spi_xc7a325t.bit")

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk200",        loose=True), 1e9/200e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:rx", 0, loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:tx", 0, loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:rx", 1, loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:tx", 1, loose=True), 1e9/125e6)
        self.add_platform_command("set_property DCI_CASCADE {{32 34}} [get_iobanks 33]")
