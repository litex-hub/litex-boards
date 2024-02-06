#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023 Kazumoto Kojima
# Copyright (c) 2023 Hans Baier <hansfbaier@gmail.com>
# Copyright (c) 2023 Ruurd Keizer <ruurdk@hotmail.com>
#
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import Pins, Subsignal, IOStandard, Misc
from litex.build.xilinx import XilinxPlatform
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk50", 0, Pins("F22"), IOStandard("LVCMOS33")),
    ("cpu_reset", 0, Pins("U26"), IOStandard("LVCMOS33")),

    # Switches
    ("sw2", 0, Pins("U26"), IOStandard("LVCMOS33")), # cpu_reset
    ("sw3", 0, Pins("V26"), IOStandard("LVCMOS33")), 

    # Leds
    ("user_led", 0, Pins("R26"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("P26"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("N26"), IOStandard("LVCMOS33")),

    # The board does not have a USB serial connected to the FPGA,
    # so you will have to either connect through the rpi uart through gpio pins (and use serial uart hw or software),
    # or attach an USB to serial adapter on JP5 pins (default)
    ("JP5_serial", 0,
        Subsignal("tx", Pins("JP5:7")),
        Subsignal("rx", Pins("JP5:8")),
        IOStandard("LVCMOS33")
    ),
    #("gpio_serial", 0,
    #    Subsignal("tx", Pins("GPIO:14")),
    #    Subsignal("rx", Pins("GPIO:15")),
    #    IOStandard("LVCMOS33")
    # )

    # SPIFlash
    # S25FL128L
    ("spiflash4x", 0,  # clock needs to be accessed through STARTUPE2
        Subsignal("cs_n", Pins("C23")),
        Subsignal("clk",  Pins("C8")),
        Subsignal("dq",   Pins("B24", "A25", "B22", "A22")),
        IOStandard("LVCMOS33")
    ),

    # DDR3 SDRAM
    # MT41J128M16JT-125K
    ("ddram", 0,
        Subsignal("a", Pins("AF5 AF2 AD6 AC6 AD4 AB6 AE2 Y5 AA4 AE6 AE3 AD5 AB4 Y6"),
            IOStandard("SSTL15")),
        Subsignal("ba", Pins("AD3 AE1 AE5"), IOStandard("SSTL15")),
        Subsignal("ras_n", Pins("AC3"),      IOStandard("SSTL15")),
        Subsignal("cas_n", Pins("AC4"),      IOStandard("SSTL15")),
        Subsignal("we_n",  Pins("AF4"),      IOStandard("SSTL15")),
        #Subsignal("cs_n", Pins("--"),       IOStandard("SSTL15")),
        Subsignal("dm", Pins("V1 V3"),       IOStandard("SSTL15")),
        Subsignal("dq", Pins(
            "W1 V2 Y1 Y3 AC2 Y2 AB2 AA3",
            "U1 V4 U6 W3 V6 U2 U7 U5"),
            IOStandard("SSTL15")), # _T_DCI")),

        Subsignal("dqs_p", Pins("AB1 W6"), IOStandard("DIFF_SSTL15")), # _T_DCI")),
        Subsignal("dqs_n", Pins("AC1 W5"), IOStandard("DIFF_SSTL15")), # _T_DCI")),

        Subsignal("clk_p", Pins("AA5"),    IOStandard("DIFF_SSTL15")),
        Subsignal("clk_n", Pins("AB5"),    IOStandard("DIFF_SSTL15")),

        Subsignal("cke",   Pins("AD1"),    IOStandard("SSTL15")),
        Subsignal("odt",   Pins("AF3"),    IOStandard("SSTL15")),
        Subsignal("reset_n", Pins("W4"),   IOStandard("LVCMOS15")),
        Misc("SLEW=FAST"),
    ),

#    ("csi", 0,  
#        Subsignal("csi", Pins("")),
#        IOStandard("LVCMOS33")
#    ),
]

_connectors = [
    # 25x2 header
    ("JP5", {
          # odd row  even row
          5: "AD21", 6: "AE21",
          7: "AE22", 8: "AF22",
          9: "AE23", 10: "AF23",
         11: "V21",  12: "W21",
         13: "Y22",  14: "AA22",
         15: "AF24", 16: "AF25",
         17: "AB21", 18: "AC21",
         19: "AB22", 20: "AC22",
         21: "AD23", 22: "AD24",
         23: "AC23", 24: "AC24",
         25: "AD25", 26: "AE25",
         27: "AA23", 28: "AB24",
         29: "AA25", 30: "AB25",
         31: "Y23",  32: "AA24",
         33: "AD26", 34: "AE26",
         35: "AB26", 36: "AC26",
         37: "W23",  38: "W24",
         39: "Y25",  40: "Y26",
         41: "W25",  42: "W26",
         43: "V23",  44: "V24",
         45: "U24",  46: "U25",
    }),
    # PMOD_1
    ("J11", {
      1: "C16", 7: "B16",
      2: "A17", 8: "B17",
      3: "A18", 9: "A19",
      4: "A20", 10: "B20", 
    }),
    # PMOD_2
    ("J12", {
       1: "E21", 7: "E22",
       2: "D23", 8: "D24",
       3: "D25", 9: "E25",
       4: "F23", 10: "F24",
    }),
    # PMOD_3
    ("J13", {
       1: "A24", 7: "A23",
       2: "B26", 8: "B25",
       3: "D26", 9: "C26",
       4: "F25", 10: "E26",
    }),
    # defining the pins to the rpi's GPIO as virtual connector - signals will still depend on gpio functions
    ("GPIO", {
        0: "C12", 1: "B11", 2: "C18", 3: "D18", 4: "E18", 5: "C11", 6: "D10", 7: "B12", 8: "A12", 9: "D14",
        10: "C13", 11: "D13", 12: "A10", 13: "E10", 14: "C17", 15: "A15", 16: "B10", 17: "D16", 18: "B15", 19: "B9",
        20: "A9", 21: "A8", 22: "C14", 23: "A14", 24: "B14", 25: "A13", 26: "C9", 27: "D15",
    })
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self, toolchain="vivado"):
        device = "xc7k325tffg676-1"
        io = _io
        connectors = _connectors

        XilinxPlatform.__init__(self, device, io, connectors, toolchain=toolchain)

        self.toolchain.bitstream_commands = \
            ["set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]"]
        self.toolchain.additional_commands = \
            ["write_cfgmem -force -format bin -interface spix4 -size 16 "
            "-loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]

        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 34]")
        self.add_platform_command("set_property INTERNAL_VREF 0.90  [get_iobanks 33]")

    def create_programmer(self):
        bscan_spi = "bscan_spi_xc7k325t.bit"
        return OpenOCD("openocd_xc7_ft2232.cfg", bscan_spi)


    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
