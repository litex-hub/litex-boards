from migen import *
from litex.build.generic_platform import *
from litex.build.gowin.platform import GowinPlatform
from litex.build.gowin.programmer import GowinProgrammer
from litex.build.openfpgaloader import OpenFPGALoader

from litex_boards.extensions.sipeed import tang_mega_som_connectors, TangMegaNeoDock

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk
    ("sys_clk", 0, Pins("V22"), IOStandard("LVCMOS33")),

    # DDR3
    ("ddram", 0,
        Subsignal("a", Pins("M1 K2 G2 J4 J2 H2 G3 J1 J5 H5 L1 H3 K4 K1 D1 R1")),
        Subsignal("ba", Pins("P5 P2 M6")),
        Subsignal("ras_n", Pins("L5")),
        Subsignal("cas_n", Pins("L4")),
        Subsignal("we_n", Pins("M5")),
        Subsignal("cs_n", Pins("P4")),
        Subsignal("dm", Pins("AA4 V7")),
        Subsignal("dq", Pins("Y4 AB3 AA5 V4 AA1 AB2 AB5 AB1 AA8 Y8 AB7 Y7 AB8 W9 AB6 Y9")),
        Subsignal("dqs_p", Pins("Y3 V9")),
        Subsignal("dqs_n", Pins("AA3 V8")),
        Subsignal("clk_p", Pins("L3")),
        Subsignal("clk_n", Pins("K3")),
        Subsignal("cke", Pins("K6")),
        Subsignal("odt", Pins("M2")),
        Subsignal("reset_n", Pins("L6")),
        IOStandard("SSTL15"),
        Misc("DRIVE=12")
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = tang_mega_som_connectors

# Docks --------------------------------------------------------------------------------------------

# Tang Mega 60K is the 60K SoM on the Neo dock (same dock as the Tang Mega 138K).
docks = {
    "neo" : TangMegaNeoDock(som="60k"),
}

# Platform -----------------------------------------------------------------------------------------

class Platform(GowinPlatform):
    default_clk_name = "sys_clk"
    default_clk_period = 1e9/50e6  # Assuming 50MHz clock

    def __init__(self, dock="neo", toolchain="gowin"):
        GowinPlatform.__init__(self, "GW5AT-LV60PG484AC1/I0", _io, _connectors, toolchain=toolchain, devicename="GW5AT-60B")
        if dock is not None:
            if dock not in docks:
                raise ValueError(f"Unsupported dock {dock}, supported: {', '.join(docks)} or None (SoM only).")
            self.add_extension(docks[dock])

        # Toolchain options
        self.toolchain.options["use_ready_as_gpio"] = 1
        self.toolchain.options["use_done_as_gpio"] = 1
        self.toolchain.options["use_mspi_as_gpio"] = 1
        self.toolchain.options["use_sspi_as_gpio"] = 1
        self.toolchain.options["use_cpu_as_gpio"] = 1
        self.toolchain.options["rw_check_on_ram"] = 1
        self.toolchain.options["bit_security"] = 0
        self.toolchain.options["bit_encrypt"] = 0
        self.toolchain.options["bit_compress"] = 0

    def create_programmer(self, kit="openfpgaloader"):
        if kit == "gowin":
            return GowinProgrammer(self.devicename)
        elif kit == "openfpgaloader":
            return OpenFPGALoader(cable="ft2232")
        else:
            raise ValueError(f"Unsupported programmer kit: {kit}")

    def do_finalize(self, fragment):
        GowinPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("sys_clk", loose=True), 1e9/50e6)
