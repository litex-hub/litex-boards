from migen import *
from litex.build.generic_platform import *
from litex.build.gowin.platform import GowinPlatform
from litex.build.extension import IOExtension
from litex.build.gowin.programmer import GowinProgrammer
from litex.build.openfpgaloader import OpenFPGALoader

from litex_boards.platforms.sipeed_tang_console import _connectors_60k

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk
    ("sys_clk", 0, Pins("V22"), IOStandard("LVCMOS33")),

    # DDR3
    ("ddram", 0,
        Subsignal("a", Pins("R1 D1 K1 K4 H3 L1 H5 J5 J1 G3 H2 J2 J4 G2 K2 M1")),
        Subsignal("ba", Pins("M6 P2 P5")),
        Subsignal("ras_n", Pins("L5")),
        Subsignal("cas_n", Pins("L4")),
        Subsignal("we_n", Pins("M5")),
        Subsignal("cs_n", Pins("P4")),
        Subsignal("dm", Pins("V7 AA4")),
        Subsignal("dq", Pins("Y9 AB6 W9 AB8 Y7 AB7 Y8 AA8 AB1 AB5 AB2 AA1 V4 AA5 AB3 Y4")),
        Subsignal("dqs_p", Pins("V9 Y3")),
        Subsignal("dqs_n", Pins("V8 AA3")),
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

# Same SoM connectors as on the Tang Console 60K.
_connectors = _connectors_60k

# Neo Dock -----------------------------------------------------------------------------------------

# Tang Mega 60K is the 60K SoM on the Neo dock (same dock as the Tang Mega 138K).
_neo_dock_io = [
    ("sys_rst_n", 0, Pins("J2:60"), IOStandard("LVCMOS15"), Misc("PULL_MODE=UP")),

    # OV5640 Camera
    ("cmos", 0,
        Subsignal("pwdn", Pins("J2:7"), Misc("DRIVE=8")),
        Subsignal("rst_n", Pins("J2:3"), Misc("DRIVE=8")),
        Subsignal("xclk", Pins("J2:11"), Misc("DRIVE=4")),
        Subsignal("sda", Pins("J2:56"), IOStandard("LVCMOS15"), Misc("PULL_MODE=UP DRIVE=8")),
        Subsignal("scl", Pins("J2:58"), IOStandard("LVCMOS33"), Misc("PULL_MODE=UP DRIVE=8")),
        Subsignal("data", Pins("J2:13 J2:17 J0:19 J2:20 J2:55 J2:49 J2:51 J2:57")),
        Subsignal("pclk", Pins("J2:15")),
        Subsignal("href", Pins("J2:9")),
        Subsignal("vsync", Pins("J2:5")),
        IOStandard("LVCMOS33"),
        Misc("PULL_MODE=NONE")
    ),

    # HDMI Output
    ("hdmi_out", 0,
        Subsignal("clk_p", Pins("J1:62")),
        Subsignal("clk_n", Pins("J1:64")),
        Subsignal("data0_p", Pins("J1:60")),
        Subsignal("data0_n", Pins("J1:58")),
        Subsignal("data1_p", Pins("J1:56")),
        Subsignal("data1_n", Pins("J1:54")),
        Subsignal("data2_p", Pins("J1:52")),
        Subsignal("data2_n", Pins("J1:50")),
        IOStandard("LVCMOS33D"),
        Misc("PULL_MODE=NONE DRIVE=3.5")
    ),

    # Ethernet RGMII
    ("eth", 0,
        Subsignal("tx_data", Pins("J0:80 J0:78 J0:76 J0:74")),
        Subsignal("tx_en", Pins("J0:72")),
        Subsignal("gtxclk", Pins("J0:70")),
        Subsignal("phy_clk", Pins("J0:4")),
        Subsignal("rst_n", Pins("J2:19")),
        IOStandard("LVCMOS33"),
        Misc("PULL_MODE=NONE")
    ),

    # SD Card
    ("sdcard", 0,
        Subsignal("clk", Pins("J2:46"), Misc("DRIVE=8")),
        Subsignal("cs", Pins("J2:44"), Misc("DRIVE=8")),
        Subsignal("mosi", Pins("J2:42"), Misc("DRIVE=8")),
        Subsignal("miso", Pins("J2:38"), Misc("DRIVE=OFF")),
        IOStandard("LVCMOS33"),
        Misc("PULL_MODE=NONE")
    ),

    # Audio
    ("audio", 0,
        Subsignal("bck", Pins("J2:26")),
        Subsignal("ws", Pins("J2:28")),
        Subsignal("din", Pins("J2:30")),
        Subsignal("pa_en", Pins("J2:36")),
        IOStandard("LVCMOS33"),
        Misc("PULL_MODE=NONE")
    ),

    # Buttons
    ("btn", 0, Pins("J2:64"), IOStandard("LVCMOS15"), Misc("PULL_MODE=UP")),
    ("btn", 1, Pins("J2:62"), IOStandard("LVCMOS15"), Misc("PULL_MODE=UP")),

    # WS2812 LED
    ("ws2812", 0, Pins("J1:48"), IOStandard("LVCMOS33"), Misc("DRIVE=8")),

    # LEDs
    ("led", 0, Pins("J0:12"), IOStandard("LVCMOS33")),
    ("led", 1, Pins("J0:14"), IOStandard("LVCMOS33")),
    ("led", 2, Pins("J0:18"), IOStandard("LVCMOS33")),
    ("led", 3, Pins("J0:20"), IOStandard("LVCMOS33")),
    ("led", 4, Pins("J0:13"), IOStandard("LVCMOS33")),
    ("led", 5, Pins("J0:15"), IOStandard("LVCMOS33")),
    ("led", 6, Pins("J0:23"), IOStandard("LVCMOS33")),
    ("led", 7, Pins("J0:25"), IOStandard("LVCMOS33")),

    # SDRAM
    ("sdram", 0,
        Subsignal("a", Pins("J1:23 J1:31 J1:6 J1:29 J1:19 J1:17 J1:36 J1:34 J1:30 J1:18 J1:16 J1:12 J1:10")),
        Subsignal("ba", Pins("J1:4 J1:40")),
        Subsignal("dq", Pins("J1:41 J1:43 J1:35 J1:37 J1:11 J1:13 J1:5 J1:7 J1:49 J1:47 J1:55 J1:53 J1:61 J1:59 J1:67 J1:65")),
        Subsignal("dm", Pins("J1:44 J1:42")),
        Subsignal("clk", Pins("J1:25")),
        Subsignal("cas", Pins("J1:22")),
        Subsignal("ras", Pins("J1:24")),
        Subsignal("we", Pins("J1:28")),
        Subsignal("cs", Pins("J0:68")),
        IOStandard("LVCMOS33"),
        Misc("DRIVE=8")
    ),
]

# Docks --------------------------------------------------------------------------------------------

docks = {
    "neo" : IOExtension(io=_neo_dock_io, slots={}),
}

# Platform -----------------------------------------------------------------------------------------

class Platform(GowinPlatform):
    default_clk_name = "sys_clk"
    default_clk_period = 1e9/50e6  # Assuming 50MHz clock

    def __init__(self, dock="neo", toolchain="gowin"):
        GowinPlatform.__init__(self, "GW5A-LV60MG121C1/IrES", _io, _connectors, toolchain=toolchain, devicename="GW5A-60")
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
