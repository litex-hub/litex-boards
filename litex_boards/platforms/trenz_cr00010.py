# This file is Copyright (c) 2019 (year 0 AG) Antti Lukats <antti.lukats@gmail.com>
# This file is Copyright (c) 2014-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# License: BSD

# info about the board http://trenz.org/max1000-info

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.altera.programmer import USBBlaster

# IOs ----------------------------------------------------------------------------------------------

_io = [
    ("clk12", 0, Pins("H6"), IOStandard("3.3-V LVTTL")),     # 12MHz clock
    ("user_led", 0, Pins("D13"), IOStandard("3.3-V LVTTL")), # RED LED2 inverted polarity

    ("sw", 0, Pins("D7"), IOStandard("3.3-V LVTTL")), # user button
    ("sw", 1, Pins("E7"), IOStandard("3.3-V LVTTL")), # nConfig use as reset by default?
# FTDI serial port
    ("serial", 0,
        Subsignal("tx", Pins("H4"), IOStandard("3.3-V LVTTL")),
        Subsignal("rx", Pins("J1"), IOStandard("3.3-V LVTTL"))
    ),

# main on-board SPI flash is only usable in X1 mode
    ("spiflash", 0,
        Subsignal("cs_n", Pins("A5")),
        Subsignal("clk",  Pins("B4")),
        Subsignal("mosi", Pins("B2")),
        Subsignal("miso", Pins("A2")),
        IOStandard("3.3-V LVTTL"),
    ),

# CRUVI LS module connnected SPI Flash
# tested with ISSI 8Mbyte Flash
    ("spiflash", 1,
        Subsignal("cs_n", Pins("M3")),
        Subsignal("clk",  Pins("M2")),
        Subsignal("mosi", Pins("K2")),
        Subsignal("miso", Pins("L2")),
        Subsignal("wp",   Pins("K1")),
        Subsignal("hold", Pins("J2")),
        IOStandard("3.3-V LVTTL"),
    ),

# CRUVI LS 4x mode not tested
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("M3")),
        Subsignal("clk",  Pins("M2")),
        Subsignal("dq",   Pins("K2", "L2", "K1", "J2")),
        IOStandard("3.3-V LVTTL")
    ),

# CRUVI HS
    ("hyperram", 0,
        Subsignal("clk", Pins("M12")),
        Subsignal("rst_n", Pins("N11")),
        Subsignal("dq", Pins("M5 M4 K8 J8 N8 N7 M7 N6")),
        Subsignal("cs_n", Pins("N5")), # CS1
        Subsignal("rwds", Pins("K5")),
        IOStandard("3.3-V LVTTL")
    ),




# 8MByte SDRAM as default
    ("sdram_clock", 0, Pins("L3"), IOStandard("3.3-V LVTTL")),
    ("sdram", 0,               # 0   1   2   3   4   5   6   7   8   9  10  11  12
#        Subsignal("a",     Pins("J9 J10 K10 K11 L12 K12 L13 J12 J13 G13 H9 H13 H10")), # for larger SDRAM one extra ADDR
        Subsignal("a",     Pins("J9 J10 K10 K11 L12 K12 L13 J12 J13 G13 H9 H13")), #0, 1, ...
        Subsignal("ba",    Pins("G12 H8")),
# CS and CKE are fixed on PCB, so not connected to FPGA
#        Subsignal("cs_n",  Pins("")),
#        Subsignal("cke",   Pins("")),
        Subsignal("ras_n", Pins("F8")),
        Subsignal("cas_n", Pins("G10")),
        Subsignal("we_n",  Pins("G9")),
        Subsignal("dq",    Pins("A12 B11 B12 C11 C12 D9 E9 E10 F13 F12 E13 E12 D12 C13 D11 B13")),
        Subsignal("dm",    Pins("F9 F10")),
        IOStandard("3.3-V LVTTL")
    ),
# EP53A7HQI power and VID control
# VID=000 3.3V
# VID=100 2.5V
# VID=111 1.8V
    ("power_control", 0,
        Subsignal("vid0",   Pins("H1")),
        Subsignal("vid1",   Pins("B7")),
        Subsignal("vid2",   Pins("L1")),
        Subsignal("enable", Pins("K13")),
        IOStandard("3.3-V LVTTL"),
    ),


    # all IO not connected to peripherals mapped to MFIO
    #                 <-        LEDS           -> <-         PMOD      -> <-                     D0..D14, D11R, D12R                  -> <-     AIN0..AIN7    -> JE [C O  I  S  i1 i2]sw
#    ("bbio", 0, Pins("A8 A9 A11 A10 B10 C9 C10 D8 M3 L3 M2 M1 N3 N2 K2 K1 H8 K10 H5 H4 J1 J2 L12 J12 J13 K11 K12 J10 H10 H13 G12 B11 G13 E1 C2 C1 D1 E3 F1 E4 B1 E5 J6 J7 K5 L5 J5 L4 E6"),
#        IOStandard("3.3-V LVTTL")),

]

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name = "clk12"
    default_clk_period = 83

    def __init__(self, device):
        AlteraPlatform.__init__(self, device, _io)
        self.add_platform_command("set_global_assignment -name FAMILY \"MAX 10\"")
        self.add_platform_command("set_global_assignment -name ENABLE_CONFIGURATION_PINS OFF")
        self.add_platform_command("set_global_assignment -name INTERNAL_FLASH_UPDATE_MODE \"SINGLE IMAGE WITH ERAM\"")

    def create_programmer(self):
        return USBBlaster()