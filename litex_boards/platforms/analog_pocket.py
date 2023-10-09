#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2020 Paul Sajna <sajattack@gmail.com>
# Copyright (c) 2022 Thomas Watson <twatson52@icloud.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.openfpgaloader import OpenFPGALoader

# IOs (LiteX) --------------------------------------------------------------------------------------

_io_physical_litex = [
    # Clk.
    ("clk74a", 0, Pins("V15"), IOStandard("3.3-V LVCMOS")),
    ("clk74b", 0, Pins("H16"), IOStandard("1.8 V")),

    # Serial.
    ("serial", 0,
        Subsignal("tx", Pins("K21")),
        Subsignal("rx", Pins("K22")),
        IOStandard("1.8V")
    ),

    # SDR SDRAM
    ("sdram_clock", 0, Pins("G12"),
        Misc("OUTPUT_TERMINATION \"SERIES 50 OHM WITHOUT CALIBRATION\""),
        IOStandard("1.8V")
    ),
    ("sdram", 0,
        Subsignal("a",     Pins(
            "D17 D12 F12 E14 F13 E16 E15 F14",
            "J18 G17 C13 F15 J17")),
        Subsignal("ba",    Pins("C16 E12")),
        #Subsignal("cs_n",  Pins("")),
        Subsignal("cke",   Pins("G18")),
        Subsignal("ras_n", Pins("B11")),
        Subsignal("cas_n", Pins("B16")),
        Subsignal("we_n",  Pins("C11")),
        Subsignal("dq",    Pins(
            "C15 B15 A15 B13 A14 B12 A13 A12",
            "J13 G15 G16 G13 H13 J19 G11 K20",
        )),
        Subsignal("dm", Pins("D13 H18")),
        Misc("CURRENT_STRENGTH_NEW \"4MA\""),
        IOStandard("1.8V"),
    ),
]

_io_fpga2fpga_litex = [
    # Video Scaler.
    ("video", 0,
        Subsignal("clk",   Pins("R17")),
        Subsignal("de",    Pins("N20")),
        Subsignal("skip",  Pins("N21")),
        Subsignal("hsync", Pins("P17")),
        Subsignal("vsync", Pins("T15")),
        Subsignal("data",  Pins(
            "R21 P22 N16 P18 P19 T20",
            "T19 T18 T22 R22 R15 R16"
        )),
        Misc("OUTPUT_TERMINATION \"SERIES 50 OHM WITHOUT CALIBRATION\""),
        IOStandard("1.8 V"),
    ),
]

# IOs (Analog) -------------------------------------------------------------------------------------

_io_physical_analog = [
    # Clk.
    ("clk_74a", 0, Pins("V15"), IOStandard("3.3-V LVCMOS")),
    ("clk_74b", 0, Pins("H16"), IOStandard("1.8 V")),

    # Cartbrige.
    ("cart",  0,
        Subsignal("tran_bank0",        Pins("AB7 AA8 AB8 AA9")),
        Subsignal("tran_bank0_dir",    Pins("AB6")),
        Subsignal("tran_bank1",        Pins("AB13 AA12 AB12 Y11 AB11 Y10 AB10 AA10")),
        Subsignal("tran_bank1_dir",    Pins("AA13")),
        Subsignal("tran_bank2",        Pins("AB20 AA19 AA18 AB18 AA17 AB17 AA15 AB15")),
        Subsignal("tran_bank2_dir",    Pins("AA14")),
        Subsignal("tran_bank3",        Pins("W22 W21 Y22 Y21 AA22 AB22 AB21 AA20")),
        Subsignal("tran_bank3_dir",    Pins("V21")),
        Subsignal("tran_pin30",        Pins("L8"),  IOStandard("1.8 V")),
        Subsignal("tran_pin30_dir",    Pins("AB5")),
        Subsignal("pin30_pwroff_reset",Pins("L17"), IOStandard("1.8 V")),
        Subsignal("tran_pin31",        Pins("K9"),  IOStandard("1.8 V")),
        Subsignal("tran_pin31_dir",    Pins("U22")),
        IOStandard("3.3-V LVCMOS"),
    ),

    # Infrared.
    ("port_ir", 0,
        Subsignal("rx",         Pins("H10")),
        Subsignal("tx",         Pins("H11")),
        Subsignal("rx_disable", Pins("L18")),
        IOStandard("1.8 V"),
    ),

    # GBA Link Port.
    ("port_tran", 0,
        Subsignal("si",      Pins("V10")),
        Subsignal("si_dir",  Pins("V9")),
        Subsignal("so",      Pins("J11"), IOStandard("1.8 V")),
        Subsignal("so_dir",  Pins("T13")),
        Subsignal("sck",     Pins("AA7")),
        Subsignal("sck_dir", Pins("Y9")),
        Subsignal("sd",      Pins("R9")),
        Subsignal("sd_dir",  Pins("T9")),
        IOStandard("3.3-V LVCMOS"),
    ),

    # PSRAM0 (AS1C8M16).
    ("cram0", 0,
        Subsignal("a",     Pins("H6 C6 B6 B7 H9 H8")),
        Subsignal("dq",    Pins("B10 C8 A9 D7 E9 F10 G6 J7 C9 A10 D9 A8 E7 F9 L7 J9")),
        Subsignal("wait",  Pins("K7")),
        Subsignal("clk",   Pins("G10")),
        Subsignal("adv_n", Pins("J8")),
        Subsignal("cre",   Pins("F7")),
        Subsignal("ce0_n", Pins("B5")),
        Subsignal("ce1_n", Pins("E10")),
        Subsignal("oe_n",  Pins("D6")),
        Subsignal("we_n",  Pins("G8")),
        Subsignal("ub_n",  Pins("A7")),
        Subsignal("lb_n",  Pins("A5")),
        IOStandard("1.8 V"),
    ),

    # PSRAM1 (AS1C8M16).
    ("cram1", 0,
        Subsignal("a",     Pins("U2 U1 N1 L2 AA2 Y3")),
        Subsignal("dq",    Pins("C1 G2 E2 P6 R5 M6 U7 V6 D3 C2 N6 P7 R6 R7 U6 W8")),
        Subsignal("wait",  Pins("W9")),
        Subsignal("clk",   Pins("W2")),
        Subsignal("adv_n", Pins("U8")),
        Subsignal("cre",   Pins("T7")),
        Subsignal("ce0_n", Pins("N2")),
        Subsignal("ce1_n", Pins("T8")),
        Subsignal("oe_n",  Pins("M7")),
        Subsignal("we_n",  Pins("AA1")),
        Subsignal("ub_n",  Pins("G1")),
        Subsignal("lb_n",  Pins("L1")),
        IOStandard("1.8 V"),
    ),

    # SDRAM (AS4C32M16).
    ("dram", 0,
        Subsignal("a",     Pins("D17 D12 F12 E14 F13 E16 E15 F14 J18 G17 C13 F15 J17")),
        Subsignal("ba",    Pins("C16 E12")),
        Subsignal("dq",    Pins("C15 B15 A15 B13 A14 B12 A13 A12 J13 G15 G16 G13 H13 J19 G11 K20")),
        Subsignal("dqm",   Pins("D13 H18")),
        Subsignal("clk",   Pins("G12")),
        Subsignal("cke",   Pins("G18")),
        Subsignal("ras_n", Pins("B11")),
        Subsignal("cas_n", Pins("B16")),
        Subsignal("we_n",  Pins("C11")),
        IOStandard("1.8 V"),
    ),

    # SRAM (AS6C2016).
    ("sram", 0,
        Subsignal("a",    Pins("T14 M9 M8 U21 N9 V19 P8 Y19 U13 Y14 U11 T10 V14 R10 U15 U12 V16")),
        Subsignal("dq",   Pins("N8 P9 P14 Y20 W19 T12 V13 R12 U16 U20 V18 V20 Y17 Y16 W16 Y15")),
        Subsignal("oe_n", Pins("R14")),
        Subsignal("we_n", Pins("R11")),
        Subsignal("ub_n", Pins("U17")),
        Subsignal("lb_n", Pins("P12")),
        IOStandard("3.3-V LVCMOS"),
    ),

    # Debug.
    ("dbg_tx", 0, Pins("K21"), IOStandard("1.8 V")),
    ("dbg_rx", 0, Pins("K22"), IOStandard("1.8 V")),
    ("user1",  0, Pins("M22"), IOStandard("1.8 V")),
    ("user2",  0, Pins("L22"), IOStandard("1.8 V")),

    # Aux I2C.
    ("aux_sda", 0, Pins("M18"), IOStandard("1.8 V")),
    ("aux_scl", 0, Pins("M16"), IOStandard("1.8 V")),

    # Others.
    ("vblank",    0, Pins("N19"), IOStandard("1.8 V")),
    ("bist",      0, Pins("U10"), IOStandard("3.3-V LVCMOS")),
    ("vpll_feed", 0, Pins("P16"), IOStandard("1.8 V")),
]

_io_fpga2fpga_analog = [
    # Scaler.
    ("scal", 0,
        Subsignal("vid",  Pins("R21 P22 N16 P18 P19 T20 T19 T18 T22 R22 R15 R16")),
        Subsignal("clk",  Pins("R17")),
        Subsignal("de",   Pins("N20")),
        Subsignal("skip", Pins("N21")),
        Subsignal("vs",   Pins("T15")),
        Subsignal("hs",   Pins("P17")),

        Subsignal("audmclk", Pins("K16")),
        Subsignal("audadc",  Pins("H15")),
        Subsignal("auddac",  Pins("K19")),
        Subsignal("audlrck", Pins("K17")),
        IOStandard("1.8 V"),
    ),

    # Bridge.
    ("bridge", 0,
        Subsignal("spimosi", Pins("M20")),
        Subsignal("spimiso", Pins("M21")),
        Subsignal("spiclk",  Pins("T17")),
        Subsignal("spiss",   Pins("H14")),
        Subsignal("lwire",   Pins("L19")),
        IOStandard("1.8 V"),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = []

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name   = "clk74a"
    default_clk_period = 1e9/74.25e6

    def __init__(self, ios="litex", toolchain="quartus"):
        _io = {
            "litex"  : _io_physical_litex  + _io_fpga2fpga_litex,
            "analog" : _io_physical_analog + _io_fpga2fpga_analog,
        }[ios]
        AlteraPlatform.__init__(self, "5CEBA4F23C8", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return OpenFPGALoader(cable="usb-blaster")

    def do_finalize(self, fragment):
        AlteraPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk74a", loose=True), 1e9/74.25e6)
        self.add_period_constraint(self.lookup_request("clk74b", loose=True), 1e9/74.25e6)
