from litex.builds.generic_platform import *
from litex.build.xilinx import XilinxPlatform
from litex.build.openocd import OpenOCD

# Pin H16 sysclk 125 MHz
# CPU reset to BTN0 on Pin D19
_io = [
        ("sysclk", 0, Pins("H16"), IOStandard("LVCMOS33")),
        ("cpu_reset", 0, Pins("D19"), IOStandard("LVCMOS33"))
        ]

#TODO add connectors
# DRAM goes here?
_connectors = []

#TODO is Zynq-7020 a 7-Series?
#It uses a 7-Series...
class Platform(XilinxPlatform):
    default_clk_name = "sysclk"
    # 8 ns clk period - 125 MHz
    default_clk_period = 8

    def __init__(self, toolchain="vivado"):
        #TODO figure out part number for Zynq-P2
        XilinxPlatform._init__(self, "xc7z020-1clg400c", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        # From vc707 platform
        # return OpenOCD("openocd_xc7_ft2232.cfg", "xc7vx485t.bit")
        pass

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
