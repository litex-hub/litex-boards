#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Antmicro <www.antmicro.com>
# SPDX-License-Identifier: BSD-2-Clause

import os

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform
from litex.build.openfpgaloader import OpenFPGALoader
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    ("clk100", 0, Pins("L19"), IOStandard("LVCMOS33")),

    ("user_led", 0, Pins("F8"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("C8"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("A8"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("D9"), IOStandard("LVCMOS33")),
    ("user_led", 4, Pins("F9"), IOStandard("LVCMOS33")),

    ("user_btn", 0, Pins("E8"), IOStandard("LVCMOS33")),
    ("user_btn", 1, Pins("B8"), IOStandard("LVCMOS33")),
    ("user_btn", 2, Pins("C9"), IOStandard("LVCMOS33")),
    ("user_btn", 3, Pins("E9"), IOStandard("LVCMOS33")),

    ("serial", 0,
        Subsignal("tx", Pins("AB18")),
        Subsignal("rx", Pins("AA18")),
        IOStandard("LVCMOS33")
    ),
    ("serial", 1,
        Subsignal("tx", Pins("AA20")),
        Subsignal("rx", Pins("AB20")),
        IOStandard("LVCMOS33")
    ),

    # DDR5 (not 1.2V, uses 1.1V or 0.6V depending on J10 jumper)
    ("ddr5", 0,
        Subsignal("ck_t",    Pins("U2"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("ck_c",    Pins("V2"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("reset_n", Pins("L1"), IOStandard("SSTL12_DCI")),
        Subsignal("alert_n", Pins("AB3"), IOStandard("SSTL12_DCI")),
        Subsignal("cs_n",    Pins("AA4"), IOStandard("SSTL12_DCI")),
        Subsignal("ca",      Pins("T3 M3 W1 P1 U1 N2 W2 P2 Y1 R1 AA1 T1 AB1 R2"), IOStandard("SSTL12_DCI")),
        Subsignal("dq",      Pins("M5 N5 N4 N3 P4 T4 U5 R4"), IOStandard("SSTL12_T_DCI")),
        Subsignal("dqs_t",   Pins("M2"), IOStandard("DIFF_SSTL12_T_DCI")),
        Subsignal("dqs_c",   Pins("M1"), IOStandard("DIFF_SSTL12_T_DCI")),
        Subsignal("dm_n",    Pins("Y3"), IOStandard("SSTL12_T_DCI")),
        Subsignal("mir",     Pins("AA3"), IOStandard("SSTL12_DCI")),
        Subsignal("cai",     Pins("AB2"), IOStandard("SSTL12_DCI")),
        Subsignal("ca_odt",  Pins("L5"), IOStandard("SSTL12_DCI")),
        Misc("SLEW=FAST"),
    ),

    # RGMII Ethernet
    ("eth_ref_clk", 0, Pins("C12"), IOStandard("LVCMOS33")),
    ("eth_clocks", 0,
        Subsignal("tx", Pins("E17")),
        Subsignal("rx", Pins("C17")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("E16"), IOStandard("LVCMOS33")),
        Subsignal("mdio",    Pins("C14"), IOStandard("LVCMOS33")),
        Subsignal("mdc",     Pins("B17"), IOStandard("LVCMOS33")),
        Subsignal("rx_ctl",  Pins("A16"), IOStandard("LVCMOS33")),
        Subsignal("rx_data", Pins("B16 A15 B15 A14"), IOStandard("LVCMOS33")),
        Subsignal("tx_ctl",  Pins("A13"), IOStandard("LVCMOS33")),
        Subsignal("tx_data", Pins("B21 B20 A19 A18"), IOStandard("LVCMOS33")),
    ),

    # HyperRAM
    ("hyperram", 0,
        Subsignal("clk",   Pins("AB15")),  # clk_n AB16
        Subsignal("rst_n", Pins("V17")),
        Subsignal("dq",    Pins("W15 AA15 AA14 W14 Y14 V15 Y16 W17")),
        Subsignal("cs_n",  Pins("AA16")),
        Subsignal("rwds",  Pins("Y17")),
        IOStandard("LVCMOS33")
    ),

    # SD Card
    ("sdcard", 0,
        Subsignal("data", Pins("D20 D19 C22 D21"), Misc("PULLUP True")),
        Subsignal("cmd",  Pins("C20"), Misc("PULLUP True")),
        Subsignal("clk",  Pins("D22")),
        Subsignal("cd",   Pins("B22")),
        Misc("SLEW=FAST"),
        IOStandard("LVCMOS33"),
    ),
]

_io_bank = dict(
    ddr5 = dict(
        ck_t    = ["bank34"],
        ck_c    = ["bank34"],
        ca      = ["bank34" for _ in range(14)],
        cs_n    = ["bank34" for _ in range(1)],
        alert_n = ["bank34"],
        reset_n = ["bank34"],
        dq      = ["bank34" for _ in range(8)],
        dm_n    = ["bank34" for _ in range(1)],
        dqs_t   = ["bank34" for _ in range(1)],
        dqs_c   = ["bank34" for _ in range(1)],
    ),
)

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, device="xc7k70tfbg484-3", toolchain="vivado"):
        Xilinx7SeriesPlatform.__init__(self, device, _io, toolchain=toolchain)
        self.toolchain.bitstream_commands = \
            ["set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]"]
        self.toolchain.additional_commands = \
            ["write_cfgmem -force -format bin -interface spix4 -size 16 "
             "-loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]

    def pin_bank_mapping(self):
        return _io_bank

    def create_programmer(self, programmer="openfpgaloader", cable="ft4232"):
        if programmer == "openfpgaloader":
            return OpenFPGALoader(cable=cable, fpga_part=self.device.split("-")[0], freq=10e6)
        if programmer == "openocd":
            config = os.path.join(os.path.dirname(__file__), "..", "prog", "openocd_xc7_ft4232.cfg")
            return OpenOCD(config, "bscan_spi_xc7k70t.bit")
        raise ValueError(f"Unsupported programmer: {programmer}")

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100", loose=True), 1e9/100e6)
