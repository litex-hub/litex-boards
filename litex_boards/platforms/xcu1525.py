# This file is Copyright (c) 2020 David Shah <dave@ds0.me>
# This file is Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# License: BSD

from litex.build.generic_platform import Pins, Subsignal, IOStandard, Misc
from litex.build.xilinx import XilinxPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # clk
    ("clk300", 0,
        Subsignal("n", Pins("AY38"), IOStandard("DIFF_SSTL12")),
        Subsignal("p", Pins("AY37"), IOStandard("DIFF_SSTL12")),
    ),

    # led
    ("user_led", 0, Pins("BC21"), IOStandard("LVCMOS12")),
    ("user_led", 1, Pins("BB21"), IOStandard("LVCMOS12")),
    ("user_led", 2, Pins("BA20"), IOStandard("LVCMOS12")),

    # serial
    ("serial", 0,
        Subsignal("rx", Pins("BF18"), IOStandard("LVCMOS12")),
        Subsignal("tx", Pins("BB20"), IOStandard("LVCMOS12")),
    ),

    # pcie
    ("pcie_x4", 0,
        Subsignal("rst_n", Pins("BD21"), IOStandard("LVCMOS12")),
        Subsignal("clk_n", Pins("AM10")),
        Subsignal("clk_p", Pins("AM11")),
        Subsignal("rx_n", Pins("AF1 AG3 AH1 AJ3")),
        Subsignal("rx_p", Pins("AF2 AG4 AH2 AJ4")),
        Subsignal("tx_n", Pins("AF6 AG8 AH6 AJ8")),
        Subsignal("tx_p", Pins("AF7 AG9 AH7 AJ9")),
    ),

    # ddram
    ("ddram", 0,
        Subsignal("a", Pins(
            "AT36 AV36 AV37 AW35 AW36 AY36 AY35 BA40",
            "BA37 BB37 AR35 BA39 BB40 AN36"),
            IOStandard("SSTL12_DCI")),
        Subsignal("act_n", Pins("BB39"), IOStandard("SSTL12_DCI")),
        Subsignal("ba",    Pins("AT35 AT34"), IOStandard("SSTL12_DCI")),
        Subsignal("bg",    Pins("BC37 BC39"), IOStandard("SSTL12_DCI")),
        Subsignal("cas_n", Pins("AP36"), IOStandard("SSTL12_DCI")),
        Subsignal("cke",   Pins("BC38"), IOStandard("SSTL12_DCI")),
        Subsignal("clk_n", Pins("AW38"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("clk_p", Pins("AV38"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("cs_n",  Pins("AR33"), IOStandard("SSTL12_DCI")),
        Subsignal("dm",    Pins("AM32 AP31 AL29 AT30 AU30 AY28 BE36 BE32"),
            IOStandard("POD12_DCI")),
        Subsignal("dq", Pins(
            "AW28 AW29 BA28 BA27 BB29 BA29 BC27 BB27",
            "BE28 BF28 BE30 BD30 BF27 BE27 BF30 BF29",
            "BB31 BB32 AY32 AY33 BC32 BC33 BB34 BC34",
            "AV31 AV32 AV34 AW34 AW31 AY31 BA35 BA34",
            "AL30 AM30 AU32 AT32 AN31 AN32 AR32 AR31",
            "AP29 AP28 AN27 AM27 AN29 AM29 AR27 AR28",
            "AT28 AV27 AU27 AT27 AV29 AY30 AW30 AV28",
            "BD34 BD33 BE33 BD35 BF32 BF33 BF34 BF35"),
            IOStandard("POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_n", Pins("BB30 BC26 BD29 BE26 BB36 BD31 AW33 BA33"),
            IOStandard("DIFF_POD12"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_p", Pins("BA30 BB26 BD28 BD26 BB35 BC31 AV33 BA32"),
            IOStandard("DIFF_POD12"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("odt", Pins("AP34"), IOStandard("SSTL12_DCI")),
        Subsignal("ras_n", Pins("AR36"), IOStandard("SSTL12_DCI")),
        Subsignal("reset_n", Pins("AU31"), IOStandard("LVCMOS12")),
        Subsignal("we_n", Pins("AP35"), IOStandard("SSTL12_DCI")),
        Misc("SLEW=FAST")
    ),
]

_connectors = []

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "clk300"
    default_clk_period = 1e9/300e6

    def __init__(self):
        XilinxPlatform.__init__(self, "xcvu9p-fsgd2104-2l-e", _io, _connectors, toolchain="vivado")

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk300", 0, loose=True), 1e9/300e6)
        # For passively cooled boards, overheating is a significant risk if airflow isn't sufficient
        self.add_platform_command("set_property BITSTREAM.CONFIG.OVERTEMPSHUTDOWN ENABLE [current_design]")
        # Reduce programming time
        self.add_platform_command("set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 61]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 62]")
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 63]")
