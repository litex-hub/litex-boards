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
