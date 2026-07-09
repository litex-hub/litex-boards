#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2024 Antmicro <www.antmicro.com>
# SPDX-License-Identifier: BSD-2-Clause

import os

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform
from litex.build.openfpgaloader import OpenFPGALoader
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    ("clk100", 0, Pins("C12"), IOStandard("LVCMOS33")),

    ("user_led", 0, Pins("D21"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("B20"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("B21"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("C22"), IOStandard("LVCMOS33")),
    ("user_led", 4, Pins("E22"), IOStandard("LVCMOS33")),

    ("serial", 0,
        Subsignal("tx", Pins("E26")),
        Subsignal("rx", Pins("F25")),
        IOStandard("LVCMOS33")
    ),

    # _IN  <=> FPGA -> MEM
    # _OUT <=> MEM -> FPGA
    ("lpddr5", 0,
        Subsignal("ck_p",    Pins("AB11"), IOStandard("DIFF_HSUL_12")),
        Subsignal("ck_n",    Pins("AC11"), IOStandard("DIFF_HSUL_12")),
        Subsignal("wck_p",   Pins("Y15"), IOStandard("DIFF_HSUL_12")),
        Subsignal("wck_n",   Pins("Y16"), IOStandard("DIFF_HSUL_12")),
        Subsignal("reset_n", Pins("AF9"), IOStandard("HSUL_12")),
        Subsignal("cs",      Pins("AA12 AB12"), IOStandard("HSUL_12")),
        Subsignal("ca",      Pins("AD11 AC12 AD10 AC13 AC9 AA9 AB9"), IOStandard("HSUL_12")),
        Subsignal("rdqs_p",  Pins("AE18"), IOStandard("DIFF_SSTL12_T_DCI")),
        Subsignal("rdqs_n",  Pins("AF18"), IOStandard("DIFF_SSTL12_T_DCI")),
        Subsignal("dq_in",   Pins(
            "AB15 AC14 AB14 AD14 AA17 AA18 AB16 AC16"),
            IOStandard("SSTL12")),
        Subsignal("dq_out",  Pins(
            "AF14 AE15 AF15 AD15 AD16 AF20 AF19 AE17"),
            IOStandard("SSTL12_T_DCI")),
        Subsignal("dmi_in",  Pins("AA15"), IOStandard("HSUL_12")),
        Subsignal("dmi_out", Pins("AF17"), IOStandard("SSTL12_DCI")),
    ),

    ("ddr5", 0,
        Subsignal("A_ck_t",  Pins("AB11 AE12"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("A_ck_c",  Pins("AC11 AF12"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("B_ck_t",  Pins("AA10 AE13"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("B_ck_c",  Pins("AB10 AF13"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("A_ca",    Pins(
            "AD11 AC12 AD10 AC13 AC9  AA9  AB9",
            "AD9  AC8  AA8  AC7  AB7  AA7"),
            IOStandard("SSTL12_DCI")),
        Subsignal("B_ca",    Pins(
            "V7  Y7  V8  V9  Y10 Y11 W9",
            "AA13 Y13 Y12 V11 W10 W11"),
            IOStandard("SSTL12_DCI")),
        Subsignal("A_cs_n",  Pins("AA12 AB12"), IOStandard("SSTL12_DCI")),
        Subsignal("B_cs_n",  Pins("Y8 AF10"), IOStandard("SSTL12_DCI")),
        Subsignal("alert_n", Pins("AD13"), IOStandard("SSTL12_DCI")),
        Subsignal("reset_n", Pins("AF9"), IOStandard("SSTL12_DCI")),
        Subsignal("A_dq",    Pins(
            "V14  V16  V17  V18  W15  W16  Y17  W14",
            "AA19 AB17 AB19 AA20 AC18 AD19 AC17 AD18",
            "AA18 AA17 AB16 AC16 AD14 AC14 AB14 AB15",
            "AF20 AD16 AF19 AE17 AD15 AE15 AF15 AF14"),
            IOStandard("SSTL12_T_DCI")),
        Subsignal("A_dm_n",  Pins("V19 AC19 AA15 AF17"), IOStandard("SSTL12_T_DCI")),
        Subsignal("B_dq",    Pins(
            "AE5 AD4 AF3 AE6 AF2 AE2 AE1 AD1",
            "AB6 Y6  Y5  AC6 AC3 AC4 AB4 AA4",
            "AB2 AA2 Y3  AC2 W1  Y2  V1  V2",
            "U2  W3  V4  V3  U6  U5  V6  U7"),
            IOStandard("SSTL12_T_DCI")),
        Subsignal("B_dm_n",  Pins("AE3 AD5 Y1 U1"), IOStandard("SSTL12_T_DCI")),
        Subsignal("A_dqs_t", Pins("W18 AD20 Y15 AE18"), IOStandard("DIFF_SSTL12_T_DCI")),
        Subsignal("B_dqs_t", Pins("AF5 AA5 AB1 W6"), IOStandard("DIFF_SSTL12_T_DCI")),
        Subsignal("A_dqs_c", Pins("W19 AE20 Y16 AF18"), IOStandard("DIFF_SSTL12_T_DCI")),
        Subsignal("B_dqs_c", Pins("AF4 AB5 AC1 W5"), IOStandard("DIFF_SSTL12_T_DCI")),
        Misc("SLEW=FAST"),
    ),

    ("spiflash4x", 0,  # clock needs to be accessed through STARTUPE2
        Subsignal("cs_n", Pins("C23")),
        Subsignal("dq",   Pins("B24", "A25", "B22", "A22")),
        IOStandard("LVCMOS33")
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
        Subsignal("clk_p", Pins("AD26")),
        Subsignal("clk_n", Pins("AE26")),
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
    ("i2c_ddr", 0,
        Subsignal("scl", Pins("E25")),
        Subsignal("sda", Pins("D26")),
        IOStandard("LVCMOS33"),
    ),
    ("i2c_platform", 0,
        Subsignal("scl", Pins("H22")),
        Subsignal("sda", Pins("G24")),
        IOStandard("LVCMOS33"),
    ),

    # SO-DIMM signals
    ("pwr_en",         0, Pins("AC21"), IOStandard("LVCMOS33")),
    ("pwr_good",      0, Pins("AD21"), Misc("PULLUP True"), IOStandard("LVCMOS33")),
    ("tb_detect",     0, Pins("AE21"), IOStandard("LVCMOS33")),
    ("ddr_presence_n", 0, Pins("AF22"), IOStandard("LVCMOS33")),
    ("LED_yellow",    0, Pins("A20"),  IOStandard("LVCMOS33")),
    ("LED_red",       0, Pins("E21"),  IOStandard("LVCMOS33")),
    ("LED_green",     0, Pins("D23"),  IOStandard("LVCMOS33")),

    # HDMI Out
    ("hdmi_out", 0,
        Subsignal("clk_p",   Pins("B15"), IOStandard("TMDS_33")),
        Subsignal("clk_n",   Pins("A15"), IOStandard("TMDS_33")),
        Subsignal("data0_p", Pins("B14"), IOStandard("TMDS_33")),
        Subsignal("data0_n", Pins("A14"), IOStandard("TMDS_33")),
        Subsignal("data1_p", Pins("A13"), IOStandard("TMDS_33")),
        Subsignal("data1_n", Pins("A12"), IOStandard("TMDS_33")),
        Subsignal("data2_p", Pins("B10"), IOStandard("TMDS_33")),
        Subsignal("data2_n", Pins("A10"), IOStandard("TMDS_33")),
    ),

    # PCIe
    ("pcie_x1", 0,
        Subsignal("rst_n", Pins("E21"), IOStandard("LVCMOS33")),
        Subsignal("clk_p", Pins("D6")),
        Subsignal("clk_n", Pins("D5")),
        Subsignal("rx_p",  Pins("G4")),
        Subsignal("rx_n",  Pins("G3")),
        Subsignal("tx_p",  Pins("F2")),
        Subsignal("tx_n",  Pins("F1"))
    ),
    ("pcie_x2", 0,
        Subsignal("rst_n", Pins("E21"), IOStandard("LVCMOS33")),
        Subsignal("clk_p", Pins("D6")),
        Subsignal("clk_n", Pins("D5")),
        Subsignal("rx_p",  Pins("G4 E4")),
        Subsignal("rx_n",  Pins("G3 E3")),
        Subsignal("tx_p",  Pins("F2 D2")),
        Subsignal("tx_n",  Pins("F1 D1"))
    ),
    ("pcie_x4", 0,
        Subsignal("rst_n", Pins("E21"), IOStandard("LVCMOS33")),
        Subsignal("clk_p", Pins("D6")),
        Subsignal("clk_n", Pins("D5")),
        Subsignal("rx_p",  Pins("G4 E4 C4 B6")),
        Subsignal("rx_n",  Pins("G3 E3 C3 B5")),
        Subsignal("tx_p",  Pins("F2 D2 B2 A4")),
        Subsignal("tx_n",  Pins("F1 D1 B1 A3"))
    ),
]

_io_bank = dict(
    ddr5 = dict(
        A_ck_t  = ["bank33" for _ in range(2)],
        A_ck_c  = ["bank33" for _ in range(2)],
        B_ck_t  = ["bank33" for _ in range(2)],
        B_ck_c  = ["bank33" for _ in range(2)],
        A_ca    = ["bank33" for _ in range(13)],
        B_ca    = ["bank33" for _ in range(13)],

        A_cs_n  = ["bank33" for _ in range(2)],
        B_cs_n  = ["bank33" for _ in range(2)],
        alert_n = ["bank33"],
        reset_n = ["bank33"],

        A_dq    = ["bank32" for _ in range(32)],
        A_dm_n  = ["bank32" for _ in range(4)],
        A_dqs_t = ["bank32" for _ in range(4)],
        A_dqs_c = ["bank32" for _ in range(4)],

        B_dq    = ["bank34" for _ in range(32)],
        B_dm_n  = ["bank34" for _ in range(4)],
        B_dqs_t = ["bank34" for _ in range(4)],
        B_dqs_c = ["bank34" for _ in range(4)],
    ),
)

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, device="xc7k160tffg676-3", toolchain="vivado"):
        Xilinx7SeriesPlatform.__init__(self, device, _io, toolchain=toolchain)
        self.toolchain.bitstream_commands = \
            ["set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]"]
        self.toolchain.additional_commands = \
            ["write_cfgmem -force -format bin -interface spix4 -size 16 "
             "-loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]
        self.add_platform_command("set_property DCI_CASCADE {{32 34}} [get_iobanks 33]")

    def pin_bank_mapping(self):
        return _io_bank

    def create_programmer(self, programmer="openfpgaloader", cable="ft4232"):
        if programmer == "openfpgaloader":
            return OpenFPGALoader(cable=cable, fpga_part=self.device.split("-")[0], freq=10e6)
        if programmer == "openocd":
            config = os.path.join(os.path.dirname(__file__), "..", "prog", "openocd_xc7_ft4232.cfg")
            bscan_spi = "bscan_spi_xc7k160t.bit" if "xc7k160t" in self.device else "bscan_spi_xc7k160t.bit"
            return OpenOCD(config, bscan_spi)
        raise ValueError(f"Unsupported programmer: {programmer}")

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100", loose=True), 1e9/100e6)
