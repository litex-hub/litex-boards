#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Paul Sajna <sajattack@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.altera.programmer import USBBlaster

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk50", 0, Pins("V11"), IOStandard("3.3-V LVTTL")),
    ("clk50", 1, Pins("Y13"), IOStandard("3.3-V LVTTL")),
    ("clk50", 2, Pins("E11"), IOStandard("3.3-V LVTTL")),

    # Leds
    ("user_led", 0, Pins("W15"),  IOStandard("3.3-V LVTTL")),
    ("user_led", 1, Pins("AA24"), IOStandard("3.3-V LVTTL")),
    ("user_led", 2, Pins("V16"),  IOStandard("3.3-V LVTTL")),
    ("user_led", 3, Pins("V15"),  IOStandard("3.3-V LVTTL")),
    ("user_led", 4, Pins("AF26"), IOStandard("3.3-V LVTTL")),
    ("user_led", 5, Pins("AE26"), IOStandard("3.3-V LVTTL")),
    ("user_led", 6, Pins("Y16"),  IOStandard("3.3-V LVTTL")),
    ("user_led", 7, Pins("AA23"), IOStandard("3.3-V LVTTL")),

    # Buttons
    ("key", 0, Pins("AH17"), IOStandard("3.3-V LVTTL")),
    ("key", 1, Pins("AH16"), IOStandard("3.3-V LVTTL")),

    # Switches
    ("user_sw", 0, Pins("Y24"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 1, Pins("W24"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 2, Pins("W21"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 3, Pins("W20"), IOStandard("3.3-V LVTTL")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("AH9"),  IOStandard("3.3-V LVTTL")), # User I/O port on Mister
        Subsignal("rx", Pins("AG11"), IOStandard("3.3-V LVTTL"))  # User I/O port on Mister
    ),

    # Serial
    ("serial", 1,
        Subsignal("tx", Pins("AF13"), IOStandard("3.3-V LVTTL")),  # Arduino_IO1
        Subsignal("rx", Pins("AG13"), IOStandard("3.3-V LVTTL"))   # Arduino_IO0
    ),

    # Accelerometer
    ("acc", 0,
        Subsignal("int",  Pins("A17")),
        Subsignal("sclk", Pins("C18")),
        Subsignal("sdat", Pins("A19")),
        IOStandard("3.3-V LVTTL")
    ),

    # ADC
    ("adc", 0,
        Subsignal("convst", Pins("U9")),
        Subsignal("sclk",   Pins("V10")),
        Subsignal("sdi",    Pins("AC4")),
        Subsignal("sdo",    Pins("AD4")),
        IOStandard("3.3-V LVTTL")
    ),

    # HDMI
    ("hdmi", 0,
        Subsignal("tx_d_r", Pins("AS12 AE12 W8 Y8 AD11 AD10 AE11 Y5")),
        Subsignal("tx_d_g", Pins("AF10 Y4 AE9 AB4 AE7 AF6 AF8 AF5")),
        Subsignal("tx_d_b", Pins("AE4 AH2 AH4 AH5 AH6 AG6 AF9 AE8")),
        Subsignal("tx_clk", Pins("AG5")),
        Subsignal("tx_de",  Pins("AD19")),
        Subsignal("tx_hs",  Pins("T8")),
        Subsignal("tx_vs",  Pins("V13")),
        Subsignal("tx_int", Pins("AF11")),
        Misc("FAST_OUTPUT_REGISTER ON"),
        IOStandard("3.3-V LVTTL")
    ),

    # I2C
    ("i2c", 0,
        Subsignal("scl",    Pins("U10")),
        Subsignal("sda",    Pins("AA4")),
        IOStandard("3.3-V LVTTL")
    ),

    # I2S
    ("i2s", 0,
        Subsignal("i2s",   Pins("T13")),
        Subsignal("mclk",   Pins("U11")),
        Subsignal("lrclk",  Pins("T11")),
        Subsignal("sclk",   Pins("T12")),
        IOStandard("3.3-V LVTTL")
    ),
]

# MiSTer extension board (https://github.com/MiSTer-devel/Main_MiSTer/wiki) ------------------------

_mister_sdram_module_io = [
    # SDR SDRAM
    ("sdram_clock", 0, Pins("AD20"), IOStandard("3.3-V LVTTL")),
    ("sdram", 0,
        Subsignal("cke", Pins("AG10")),
        Subsignal("a",   Pins(
            "Y11 AA26 AA13 AA11 W11 Y19 AB23 AC23",
            "AC22 C12 AB26 AD17 D12")),
        Subsignal("dq",  Pins(
            "E8    V12 D11  W12 AH13  D8 AH14 AF7",
            "AE24 AD23 AE6 AE23 AG14 AD5  AF4 AH3"),
            Misc("FAST_OUTPUT_ENABLE_REGISTER ON"),
            Misc("FAST_INPUT_REGISTER ON")),
        Subsignal("ba",    Pins("Y17 AB25")),
        Subsignal("cas_n", Pins("AA18")),
        Subsignal("cs_n",  Pins("Y18")),
        Subsignal("ras_n", Pins("W14")),
        Subsignal("we_n",  Pins("AA19")),
        Misc("CURRENT_STRENGTH_NEW \"MAXIMUM CURRENT\""),
        Misc("FAST_OUTPUT_REGISTER ON"),
        Misc("ALLOW_SYNCH_CTRL_USAGE OFF"),
        IOStandard("3.3-V LVTTL"),
    ),

    # SDCard
    ("spisdcard", 0,
        Subsignal("clk",  Pins("AH26")),
        Subsignal("cs_n", Pins("AF28")),
        Subsignal("mosi", Pins("AF27"), Misc("WEAK_PULL_UP_RESISTOR ON")),
        Subsignal("miso", Pins("AF25"), Misc("WEAK_PULL_UP_RESISTOR ON")),
        IOStandard("3.3-V LVTTL")
    ),

    ("sdcard", 0,
        Subsignal("data", Pins("AF25 AF23 AD26 AF28"), Misc("WEAK_PULL_UP_RESISTOR ON")),
        Subsignal("cmd", Pins("AF27"), Misc("WEAK_PULL_UP_RESISTOR ON")),
        Subsignal("clk", Pins("AH26")),
        Subsignal("cd", Pins("AH7")),
        Misc("FAST_OUTPUT_REGISTER ON"),
        IOStandard("3.3-V LVTTL"),
    ),

    # Outputs
    ("mister_outputs", 0,
        Subsignal("led_user",  Pins("Y15")),
        Subsignal("led_hdd",   Pins("AA15")),
        Subsignal("led_power", Pins("AG28")),
        IOStandard("3.3-V LVTTL")
    ),

    # VGA
    ("vga", 0,
        Subsignal("en",      Pins("AH27")),
        Subsignal("hsync_n", Pins("AH22")),
        Subsignal("vsync_n", Pins("AG24")),
        Subsignal("r", Pins("AE17 AE20 AF20 AH18 AH19 AF21")),
        Subsignal("g", Pins("AE19 AG15 AF18 AG18 AG19 AG20")),
        Subsignal("b", Pins("AG21 AA20 AE22 AF22 AH23 AH21")),
        IOStandard("3.3-V LVTTL")
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self, toolchain="quartus"):
        AlteraPlatform.__init__(self, "5CSEBA6U23I7", _io, toolchain=toolchain)
        self.add_extension(_mister_sdram_module_io)

    def create_programmer(self):
        return USBBlaster(cable_name="DE-SoC", device_id=2)

    def do_finalize(self, fragment):
        AlteraPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", 0, loose=True), 1e9/50e6)
        self.add_period_constraint(self.lookup_request("clk50", 1, loose=True), 1e9/50e6)
        self.add_period_constraint(self.lookup_request("clk50", 2, loose=True), 1e9/50e6)
