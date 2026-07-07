#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Antmicro <www.antmicro.com>
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

    # Take A channel only.
    ("ddr5", 0,
        Subsignal("ck_t",    Pins("AC9"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("ck_c",    Pins("AD9"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("A_ca",    Pins("V7 Y7 Y8 V8 W11 V11 Y10"), IOStandard("SSTL12_DCI")),
        Subsignal("B_ca",    Pins("AF8 AE8 AF9 AF10 AE10 AD10 AE13"), IOStandard("SSTL12_DCI")),
        Subsignal("A_cs_n",  Pins("AA2 AA3"), IOStandard("SSTL12_DCI")),
        Subsignal("B_cs_n",  Pins("AC11 AB11"), IOStandard("SSTL12_DCI")),
        Subsignal("A_par",   Pins("Y11"), IOStandard("SSTL12_DCI")),
        Subsignal("B_par",   Pins("AF13"), IOStandard("SSTL12_DCI")),
        Subsignal("alert_n", Pins("AF2"), IOStandard("SSTL12_DCI")),
        Subsignal("reset_n", Pins("AF3"), IOStandard("SSTL12_DCI")),
        Subsignal("A_dq",    Pins(
            "U6  U5  U7  V6",
            "V1  W1  V2  Y1",
            "Y5  AA4 Y6  AB4",
            "AE3 AE2 AD1 AE1"),
            IOStandard("SSTL12_T_DCI")),
        Subsignal("B_dq",    Pins(
            "AF14 AE15 AF15 AF17",
            "AC14 AA14 AD14 AA15",
            "AD18 AD19 AC17 AC18",
            "AB20 Y17  W15  W16"),
            IOStandard("SSTL12_T_DCI")),
        Subsignal("A_dqs_t", Pins("W6 AB1 AA5 AF5"),    IOStandard("DIFF_SSTL12_T_DCI")),
        Subsignal("B_dqs_t", Pins("AE18 Y15 AD20 W18"), IOStandard("DIFF_SSTL12_T_DCI")),
        Subsignal("A_dqs_c", Pins("W5 AC1 AB5 AF4"),    IOStandard("DIFF_SSTL12_T_DCI")),
        Subsignal("B_dqs_c", Pins("AF18 Y16 AE20 W19"), IOStandard("DIFF_SSTL12_T_DCI")),
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
        Subsignal("clk",   Pins("AD26")), # clk_n AE26
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
        Subsignal("clk_p",   Pins("B15"), IOStandard("TMDS_33")),
        Subsignal("clk_n",   Pins("A15"), IOStandard("TMDS_33")),
        Subsignal("data0_p", Pins("B14"), IOStandard("TMDS_33")),
        Subsignal("data0_n", Pins("A14"), IOStandard("TMDS_33")),
        Subsignal("data1_p", Pins("A13"), IOStandard("TMDS_33")),
        Subsignal("data1_n", Pins("A12"), IOStandard("TMDS_33")),
        Subsignal("data2_p", Pins("B10"), IOStandard("TMDS_33")),
        Subsignal("data2_n", Pins("A10"), IOStandard("TMDS_33")),
    ),
]

_io_bank = dict(
    ddr5 = dict(
        ck_t    = ["bank33"],
        ck_c    = ["bank33"],
        A_ca    = ["bank33" for _ in range(7)],
        B_ca    = ["bank33" for _ in range(7)],
        A_cs_n  = ["bank34" for _ in range(2)],
        B_cs_n  = ["bank33" for _ in range(2)],
        A_par   = ["bank33"],
        B_par   = ["bank33"],
        alert_n = ["bank34"],
        reset_n = ["bank34"],
        A_dq    = ["bank34" for _ in range(16)],
        B_dq    = ["bank32" for _ in range(16)],
        A_dqs_t = ["bank34" for _ in range(4)],
        A_dqs_c = ["bank34" for _ in range(4)],
        B_dqs_t = ["bank32" for _ in range(4)],
        B_dqs_c = ["bank32" for _ in range(4)],
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
