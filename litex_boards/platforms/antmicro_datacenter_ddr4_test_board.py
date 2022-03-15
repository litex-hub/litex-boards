#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Antmicro <www.antmicro.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    ("clk100", 0, Pins("C12"), IOStandard("LVCMOS33")),

    ("user_led", 0, Pins("D21"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("B20"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("B21"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("C22"), IOStandard("LVCMOS33")),
    ("user_led", 4, Pins("E22"), IOStandard("LVCMOS33")),

    ("user_btn", 0, Pins("C21"), IOStandard("LVCMOS33")),
    ("user_btn", 1, Pins("A20"), IOStandard("LVCMOS33")),
    ("user_btn", 2, Pins("E21"), IOStandard("LVCMOS33")),
    ("user_btn", 3, Pins("D23"), IOStandard("LVCMOS33")),

    ("serial", 0,
        Subsignal("tx", Pins("E26")),
        Subsignal("rx", Pins("F25")),
        IOStandard("LVCMOS33")
    ),

    ("spiflash4x", 0,  # clock needs to be accessed through STARTUPE2
        Subsignal("cs_n", Pins("C23")),
        Subsignal("dq",   Pins("B24", "A25", "B22", "A22")),
        IOStandard("LVCMOS33")
    ),

    # DDR4
    ("ddr4", 0,
        Subsignal("a",       Pins(
            "AF10 AC11 AD11 AD10 AC9  AD9  AB9  AF7  AE8",
            "AE7  Y12  AC7  AB7  AD13"),
            IOStandard("SSTL12_DCI")),
        Subsignal("ba",      Pins("AB11 AB10"), IOStandard("SSTL12_DCI")),
        Subsignal("bg",      Pins("AA9 AF9"), IOStandard("SSTL12_DCI")),
        Subsignal("ras_n",   Pins("AA12"), IOStandard("SSTL12_DCI")), # A16
        Subsignal("cas_n",   Pins("AF13"), IOStandard("SSTL12_DCI")), # A15
        Subsignal("we_n",    Pins("AA13"), IOStandard("SSTL12_DCI")), # A14
        Subsignal("cs_n",    Pins("W13"), IOStandard("SSTL12_DCI")),
        Subsignal("act_n",   Pins("Y8"), IOStandard("SSTL12_DCI")),
        Subsignal("alert_n", Pins("AE10"), IOStandard("SSTL12_DCI")),
        Subsignal("par",     Pins("AE13"), IOStandard("SSTL12_DCI")),
        Subsignal("dm",      Pins("AF3 AE5 AD6 AC6 AF2 AE3 AE6 AD5"),
            IOStandard("SSTL12_DCI")),
        Subsignal("dq",      Pins(
                "W11  Y11  V7   Y7   V11  V9   V8   W8",
                "U2   V6   Y2   Y3   U5   U4   W3   Y1",
                "AA2  AB2  AE1  AE2  V2   W1   AD1  AC2",
                "W4   AA3  AD3  AC4  V3   V4   AB4  AC3",
                "AC16 AC17 AB16 AA19 AB15 AD16 AC18 AC19",
                "AF17 AE17 AF20 AD19 AE15 AE16 AF19 AD18",
                "Y18  Y17  W14  V14  AA20 AA15 V18  W16",
                "AA18 AB19 V16  W15  AB17 AA17 V19  V17"),
            IOStandard("SSTL12_T_DCI")),
        Subsignal("dqs_p",   Pins(
                "W10  B17 W6   D19 AB1 L19 AA5 J15",
                "AD20 T24 AE18 P19 W18 R16 Y15 M25"),
            IOStandard("DIFF_HSUL_12")),
        Subsignal("dqs_n",   Pins(
                "W9   A17 W5   D20 AC1 L20 AB5 J16",
                "AE20 T25 AF18 P20 W19 R17 Y16 L25"),
            IOStandard("DIFF_HSUL_12")),
        Subsignal("clk_p",   Pins("AE12"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("clk_n",   Pins("AF12"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("cke",     Pins("AA8"), IOStandard("SSTL12_DCI")), # also AM15 for larger SODIMMs
        Subsignal("odt",     Pins("Y13"), IOStandard("SSTL12_DCI")), # also AM16 for larger SODIMMs
        Subsignal("reset_n", Pins("AB6"), IOStandard("SSTL12")),
        Misc("SLEW=FAST"),
    ),

    # RGMII Ethernet
    ("eth_ref_clk", 0, Pins("AA23"), IOStandard("LVCMOS33")),
    ("eth_clocks", 0,
        Subsignal("rx", Pins("Y23")),
        Subsignal("tx", Pins("AA24")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("AA22")),
        Subsignal("mdio",    Pins("AB26")),
        Subsignal("mdc",     Pins("AA25")),
        Subsignal("rx_ctl",  Pins("Y25")),
        Subsignal("rx_data", Pins("W26 W25 V26 U25")),
        Subsignal("tx_ctl",  Pins("U26")),
        Subsignal("tx_data", Pins("W24 Y26 Y22 Y21")),
        IOStandard("LVCMOS33")
    ),

    # HyperRAM
    ("hyperram", 0,
        Subsignal("clk", Pins("AD26")), # clk_n AE26
        Subsignal("rst_n", Pins("AC24")),
        Subsignal("cs_n",  Pins("AC26")),
        Subsignal("dq",    Pins("AE23 AD25 AF24 AE22 AF23 AF25 AE25 AD24")),
        Subsignal("rwds",  Pins("AD23")),
        IOStandard("LVCMOS33")
    ),

    # SD Card
    ("sdcard", 0,
        Subsignal("data", Pins("E10 F8 C9 D9"), Misc("PULLUP True")),
        Subsignal("cmd",  Pins("D8"), Misc("PULLUP True")),
        Subsignal("clk",  Pins("D10")),
        Subsignal("cd",   Pins("F9")),
        Misc("SLEW=FAST"),
        IOStandard("LVCMOS33"),
    ),

    # I2C
    ("i2c", 0,
        Subsignal("scl", Pins("E25")),
        Subsignal("sda", Pins("D26")),
        IOStandard("LVCMOS33"),
    ),

    # HDMI Out
    ("hdmi_out", 0,
        Subsignal("clk_p",   Pins("B15"),   IOStandard("TMDS_33")),
        Subsignal("clk_n",   Pins("A15"),   IOStandard("TMDS_33")),
        Subsignal("data0_p", Pins("B14"),   IOStandard("TMDS_33")),
        Subsignal("data0_n", Pins("A14"),   IOStandard("TMDS_33")),
        Subsignal("data1_p", Pins("A13"),  IOStandard("TMDS_33")),
        Subsignal("data1_n", Pins("A12"),  IOStandard("TMDS_33")),
        Subsignal("data2_p", Pins("B10"),  IOStandard("TMDS_33")),
        Subsignal("data2_n", Pins("A10"),  IOStandard("TMDS_33")),
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, device="xc7k160tffg676-1", toolchain="vivado"):
        XilinxPlatform.__init__(self, device, _io, toolchain=toolchain)
        self.toolchain.bitstream_commands = \
            ["set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]"]
        self.toolchain.additional_commands = \
            ["write_cfgmem -force -format bin -interface spix4 -size 16 "
             "-loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]
        self.add_platform_command("set_property INTERNAL_VREF 0.6 [get_iobanks 32]")
        self.add_platform_command("set_property INTERNAL_VREF 0.6 [get_iobanks 33]")
        self.add_platform_command("set_property INTERNAL_VREF 0.6 [get_iobanks 34]")
        self.add_platform_command("set_property DCI_CASCADE {{32 34}} [get_iobanks 33]")

    def create_programmer(self):
        bscan_spi = "bscan_spi_xc7k160t.bit" if "xc7k160t" in self.device else "bscan_spi_xc7k160t.bit"
        return OpenOCD("openocd_xc7_ft4232.cfg", bscan_spi)

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100", loose=True), 1e9/100e6)
