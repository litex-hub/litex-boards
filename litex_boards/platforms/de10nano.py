# This file is Copyright (c) 2020 Paul Sajna <sajattack@gmail.com>
# License: BSD

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.altera.programmer import USBBlaster

# IOs ----------------------------------------------------------------------------------------------

_io = [
    ("clk50", 0, Pins("V11"), IOStandard("3.3-V LVTTL")),
    ("clk50", 1, Pins("Y13"), IOStandard("3.3-V LVTTL")),
    ("clk50", 2, Pins("E11"), IOStandard("3.3-V LVTTL")),

    ("user_led", 0, Pins("W15"), IOStandard("3.3-V LVTTL")),
    ("user_led", 1, Pins("AA24"), IOStandard("3.3-V LVTTL")),
    ("user_led", 2, Pins("V16"), IOStandard("3.3-V LVTTL")),
    ("user_led", 3, Pins("V15"), IOStandard("3.3-V LVTTL")),
    ("user_led", 4, Pins("AF26"), IOStandard("3.3-V LVTTL")),
    ("user_led", 5, Pins("AE26"), IOStandard("3.3-V LVTTL")),

    ("key", 0, Pins("AH17"), IOStandard("3.3-V LVTTL")),
    ("key", 1, Pins("AH16"), IOStandard("3.3-V LVTTL")),

    ("user_sw", 0, Pins("Y24"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 1, Pins("W24"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 2, Pins("W21"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 3, Pins("W20"), IOStandard("3.3-V LVTTL")),

    ("serial", 0,
        Subsignal("tx", Pins("AF13"), IOStandard("3.3-V LVTTL")), # Arduino_IO1
        Subsignal("rx", Pins("AG13"), IOStandard("3.3-V LVTTL"))  # Arduino_IO0
    ),

    ("g_sensor", 0,
        Subsignal("int", Pins("A17")),
        Subsignal("sclk", Pins("C18")),
        Subsignal("sdat", Pins("A19")),
        IOStandard("3.3-V LVTTL")
    ),

    ("adc", 0,
        Subsignal("convst", Pins("U9")),
        Subsignal("sclk", Pins("V10")),
        Subsignal("sdi", Pins("AC4")),
        Subsignal("sdo", Pins("AD4")),
        IOStandard("3.3-V LVTTL")
    ),

    ("hdmi", 0,
        Subsignal("tx_d_r", Pins("AS12 AE12 W8 Y8 AD11 AD10 AE11 Y5")),
        Subsignal("tx_d_g", Pins("AF10 Y4 AE9 AB4 AE7 AF6 AF8 AF5")),
        Subsignal("tx_d_b", Pins("AE4 AH2 AH4 AH5 AH6 AG6 AF9 AE8")),
        Subsignal("tx_clk", Pins("AG5")),
        Subsignal("tx_de",  Pins("AD19")),
        Subsignal("tx_hs",  Pins("T8")),
        Subsignal("tx_vs",  Pins("V13")),
        Subsignal("tx_int", Pins("AF11")),
        Subsignal("i2s0", Pins("T13")),
        Subsignal("mclk", Pins("U11")),
        Subsignal("lrclk", Pins("T11")),
        Subsignal("sclk", Pins("T12")),
        Subsignal("scl", Pins("U10")),
        Subsignal("sda", Pins("AA4")),
        IOStandard("3.3-V LVTTL")
    ),

    ("gpio_0", 0,
        Pins("V12 E8 W12 D11 D8 AH13 AF7 AH14 AF4 AH3 AD5 AG14 AE23 D12 AD20",
            "C12 AD17 AC23 AC22 Y19 AB23 AA19 W11 AA18 W14 Y18 Y17 AB25 AB26",
            "Y11 AA26 AA13 AA11"),
        IOStandard("3.3-V LVTTL")
    ),
    ("gpio_1", 0,
        Pins("Y15 AC24 AA15 AD26 AG28 AF28 AE25 AF27 AG26 AH27 AG25 AH26 AH24",
            "AF25 AG23 AF24 AG24 AH22 AH21 AG21 AH23 AA20 AF22 AE22 AG20 AF21",
            "AH23 AA20 AF22 AE22 AG20 AF21 AG19 AH19 AG18 AH18 AF18 AF20 AG15",
            "AE20 AE19 AE17"),
        IOStandard("3.3-V LVTTL")
    ),
    ("arduino", 0,
        Pins("AG13 AF13 AG10 AG9 U14 U13 AG8 AH8 AF17 AE15 AF15 AG16 AH11 AH12",
            "AH9, AG11, AH7"),
        IOStandard("3.3-V LVTTL")
    ),
]

_mister_sdram_module_io = [
    ("sdram_clock", 0, Pins("AD20"), IOStandard("3.3-V LVTTL")),
    ("sdram", 0,
        Subsignal("cke", Pins("AG10")),
        Subsignal("a", Pins(
            "Y11 AA26 AA13 AA11 W11 Y19 AB23 AC23 AC22 C12 AB26 AD17 D12")),
        Subsignal("dq", Pins(
            "E8 V12 D11 W12 AH13 D8 AH14 AF7 AE24 AD23 AE6 AE23 AG14 AD5 AF4 AH3")),
        Subsignal("ba", Pins(
            "Y17 AB25")),
        Subsignal("cas_n", Pins("AA18")),
        Subsignal("cs_n", Pins("Y18")),
        Subsignal("ras_n", Pins("W14")),
        Subsignal("we_n", Pins("AA19")),
        IOStandard("3.3-V LVTTL")
    ),

    ("spisdcard", 0,
        Subsignal("clk",  Pins("AH26")),
        Subsignal("mosi", Pins("AF27")),
        Subsignal("cs_n", Pins("AF28")),
        Subsignal("miso", Pins("AF25")),
        IOStandard("3.3-V LVTTL")
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self):
        AlteraPlatform.__init__(self, "5CSEBA6U23I7", _io)
        self.add_extension(_mister_sdram_module_io)

    def create_programmer(self):
        return USBBlaster()
