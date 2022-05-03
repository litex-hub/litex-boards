#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.lattice import LatticePlatform
from litex.build.lattice.programmer import OpenOCDJTAGProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk.
    ("clk40", 0, Pins("A9"), IOStandard("LVCMOS33")),

    # Leds.
    ("led_g_n", 0, Pins("R16"), IOStandard("LVCMOS33"), Misc("OPENDRAIN=ON")),
    ("led_g_n", 1, Pins("M18"), IOStandard("LVCMOS33"), Misc("OPENDRAIN=ON")), # Shared with FPGA_GPIO4.
    ("led_g_n", 2, Pins("T17"), IOStandard("LVCMOS33"), Misc("OPENDRAIN=ON")), # Shared with FPGA_GPIO6.
    ("led_r_n", 0, Pins("V17"), IOStandard("LVCMOS33"), Misc("OPENDRAIN=ON")),
    ("led_r_n", 1, Pins("R18"), IOStandard("LVCMOS33"), Misc("OPENDRAIN=ON")), # Shared with FPGA_GPIO5.
    ("led_r_n", 2, Pins("R17"), IOStandard("LVCMOS33"), Misc("OPENDRAIN=ON")), # Shared with FPGA_GPIO7.

    # Revision.
    ("revision", 0,
        Subsignal("hardware", Pins("D4 M2 N4 J3")),
        Subsignal("bom",      Pins("N1 M1 N2")),
        IOStandard("LVCMOS25")
    ),

    # GPIO.
    ("gpio",  0, Pins("N15 N18 N16 N17 M18 R18 T17 R17"), IOStandard("LVCMOS33")),
    ("egpio", 0, Pins("A10 A8"),                          IOStandard("LVCMOS33")),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("U17")),
        Subsignal("clk",  Pins("U16")),
        Subsignal("miso", Pins("U18")),
        Subsignal("mosi", Pins("T18")),
        IOStandard("LVCMOS33"),
    ),

    # I2C.
    ("i2c", 0,
        Subsignal("scl", Pins("C10"), Misc("OPENDRAIN=ON")),
        Subsignal("sda", Pins("B9"),  Misc("OPENDRAIN=ON")),
        IOStandard("LVCMOS33"),
    ),

    # SPI.
    ("spi", 0,
        # SPI.
        Subsignal("clk",      Pins("M3")),
        Subsignal("lms_cs_n", Pins("N3")),
        Subsignal("dac_cs_n", Pins("L4")),
        Subsignal("mosi",     Pins("L3")),
        Subsignal("miso",     Pins("K3")),
        IOStandard("LVCMOS25"),
    ),

    # Temperature Sensor.
    ("lms75_os", 0, Pins("K2"), IOStandard("LVCMOS25")),

    # USB-FIFO.
    ("usb_fifo_clk", 0, Pins("D17"), IOStandard("LVCMOS33")),
    ("usb_fifo", 0,
        Subsignal("rst_n", Pins("M17")),
        Subsignal("data", Pins(
            "A13 B12 B15 C12 A16 A12 D18 B17",
            "F15 D16 D15 C13 H18 B13 J18 A15",
            "B18 C18 A17 K18 C15 L18 F18 C16",
            "G16 D13 G18 F16 C17 F17 K15 K17")),
        Subsignal("be",    Pins("L15 J17 K16 H17")),
        Subsignal("rxf_n", Pins("H16")),
        Subsignal("txe_n", Pins("M16")),
        Subsignal("rd_n",  Pins("H15")),
        Subsignal("wr_n",  Pins("J16")),
        Subsignal("oe_n",  Pins("L16")),
        IOStandard("LVCMOS33"),
    ),

    # RF-IC / LMS7002M.
    ("lms7002m", 0,
        # Control.
        Subsignal("pwrdwn_n", Pins("C8")),
        Subsignal("rxen",     Pins("D6")),
        Subsignal("txen",     Pins("B7")),

        # RX-Interface (LMS -> FPGA).
        Subsignal("diq1",   Pins("J2 L1 K1 K4 G3 F4 J1 H1 G4 F2 G1 H2")),
        Subsignal("txnrx1", Pins("F1")),
        Subsignal("iqsel1", Pins("F3")),
        Subsignal("mclk1",  Pins("H4")),
        Subsignal("fclk1",  Pins("H3")),

        # RX-Interface (FPGA -> LMS).
        Subsignal("diq2",   Pins("A3 C2 A2 B4 C3 B2 D3 B1 A4 C1 C7 A6")),
        Subsignal("txnrx2", Pins("B6")),
        Subsignal("iqsel2", Pins("C4")),
        Subsignal("mclk2",  Pins("D2")),
        Subsignal("fclk2",  Pins("D1")),

        # IOStandard/Slew Rate.
        IOStandard("LVCMOS25"),
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticePlatform):
    default_clk_name   = "clk40"
    default_clk_period = 1e9/40e6

    def __init__(self, device="LFE5U", toolchain="trellis", **kwargs):
        assert device in ["LFE5U"]
        LatticePlatform.__init__(self, device + "-45F-8MG285C", _io, toolchain=toolchain, **kwargs)

    def create_programmer(self):
        return OpenOCDJTAGProgrammer("openocd_limesdr_mini_v2.cfg")

    def do_finalize(self, fragment):
        self.add_period_constraint(self.lookup_request("clk40", loose=True), 1e9/40e6)
