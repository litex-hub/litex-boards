# This file is Copyright (c) 2019 Antti Lukats <antti.lukats@gmail.com>
# This file is Copyright (c) 2019 Florent Kermarrec <florent@enjoy-digital.fr>
# License: BSD

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.altera.programmer import USBBlaster

# IOs ----------------------------------------------------------------------------------------------

_io_10CL055 = [
    ("user_led", 0, Pins("C18"), 
         IOStandard("3.3-V LVTTL")),
    ("mfio", 0, Pins(
        "D19 C19"
    ), IOStandard("3.3-V LVTTL"))
]

_io_10CL025_U256 = [
    ("user_led", 0, Pins("M6"), 
         IOStandard("3.3-V LVTTL")),
    ("mfio", 0, Pins(
       "B1", "C2", "C1", "F3", "D2", "D1", "F4", "G2", "G1", "H1", "H2", "H5", "H4", "H3"
    ), IOStandard("3.3-V LVTTL"))
]


# FPGA DEVICE, _io_XXX, ROM_SIZE, RAM_SIZE
_variants = [
    ("10CL055YU484A7G", _io_10CL055, 16, 8),
    ("10M08SAU169C8G",  _io_10CL025_U256, 16, 8),
    ("10M16SAU169C8G",  _io_10M16_U169, 16, 16)
]


# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name = "sys_clk"
    default_clk_period = 1e9/80e6


    def __init__(self, id = 0):
        _device, _io = _variants[id]

        AlteraPlatform.__init__(self, _device, _io)

        self.add_platform_command("set_global_assignment -name FAMILY \"Cyclone 10 LP\"")


    def create_programmer(self):
        return USBBlaster()
