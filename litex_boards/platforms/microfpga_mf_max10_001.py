# This file is Copyright (c) 2019 Antti Lukats <antti.lukats@gmail.com>
# This file is Copyright (c) 2019 Florent Kermarrec <florent@enjoy-digital.fr>
# License: BSD

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.altera.programmer import USBBlaster

# IOs ----------------------------------------------------------------------------------------------

#_io_10M08_U169 = [
#    ("mfio", 0, Pins("D8"), 
#         IOStandard("3.3-V LVTTL"))
#]

# TODO: dynamic/selectable IO standard, Misc() also

# 10M08 and 10M16 are the same
_io_10M08_U169 = [
    ("mfio", 0, Pins(
        "D1", "C2", "E3", "E4", "C1", "B1", "F1", "E1", "E5", "H1", "F4", "G4", "H2", "H3", "G5", "J1", "H6", "J2", "H5", "M1", "H4", "M2", "N2", "L1", "N3", "L2", "M3", "K1", "L3", "K2", "L5", "M4", "L4", "M5", "K5", "N4", "J5", "N5", "N6", "N7", "M7", "N8", "J6", "M8", "K6", "M9", "J7", "N11", "K7", "N12", "M13", "N10", "M12", "N9", "M11", "L11", "J8", "K8", "M10", "L10", "K10", "K11", "J10", "L12", "K12", "L13", "J12", "K13", "J9", "J13", "H10", "H13", "H9", "G13", "H8", "G12", "G9", "G10", "F13", "E13", "F12", "E12", "F9", "D13", "F10", "C13", "F8", "B12", "E9", "B11", "C12", "B13", "C11", "A12", "E10", "D9", "D12", "D11", "C10", "A8", "C9", "A9", "B10", "A10", "B9", "A11", "D8", "E8", "B7", "D7", "A7", "A6", "B6", "A4", "B5", "A3", "E6", "B3", "D6", "B4", "C4", "A5", "C5", "A2", "B2"
    ), IOStandard("3.3-V LVTTL"))
]

_io_MAX1000 = [
    ("mfio", 0, Pins("D8"), 
         IOStandard("3.3-V LVTTL"))
]


# FPGA DEVICE, _io_XXX, ROM_SIZE, RAM_SIZE
_variants = [
    ("10M08SAU169C8G", _io_MAX1000,    16, 8),
    ("10M08SAU169C8G", _io_10M08_U169, 16, 8),
    ("10M16SAU169C8G", _io_10M08_U169, 16, 16)
]


# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name = "sys_clk"
    default_clk_period = 1e9/116e6
 
    rom_size = 16
    ram_size = 8 

    def __init__(self, id = 0):
        _device, _io, rom_size, ram_size = _variants[id]
        
        AlteraPlatform.__init__(self, _device, _io)

        self.add_platform_command("set_global_assignment -name FAMILY \"MAX 10\"")
        self.add_platform_command("set_global_assignment -name ENABLE_CONFIGURATION_PINS OFF")
        self.add_platform_command("set_global_assignment -name INTERNAL_FLASH_UPDATE_MODE \"SINGLE IMAGE WITH ERAM\"")
        self.add_platform_command("set_global_assignment -name ENABLE_BOOT_SEL_PIN OFF")

 

    def create_programmer(self):
        return USBBlaster()
