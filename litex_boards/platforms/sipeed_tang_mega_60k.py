from migen import *
from litex.build.generic_platform import *
from litex.build.gowin.platform import GowinPlatform
from litex.build.gowin.programmer import GowinProgrammer
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("sys_clk", 0, Pins("V22"), IOStandard("LVCMOS33")),
    ("sys_rst_n", 0, Pins("AA13"), IOStandard("LVCMOS15"), Misc("PULL_MODE=UP")),

    # OV5640 Camera
    ("cmos", 0,
        Subsignal("pwdn", Pins("AB22"), Misc("DRIVE=8")),
        Subsignal("rst_n", Pins("Y22"), Misc("DRIVE=8")),
        Subsignal("xclk", Pins("AA21"), Misc("DRIVE=4")),
        Subsignal("sda", Pins("Y13"), IOStandard("LVCMOS15"), Misc("PULL_MODE=UP DRIVE=8")),
        Subsignal("scl", Pins("AA14"), IOStandard("LVCMOS33"), Misc("PULL_MODE=UP DRIVE=8")),
        Subsignal("data", Pins("AA20 AA19 T20 N15 R14 R16 P15 P14")),
        Subsignal("pclk", Pins("AB20")),
        Subsignal("href", Pins("AB21")),
        Subsignal("vsync", Pins("Y21")),
        IOStandard("LVCMOS33"),
        Misc("PULL_MODE=NONE")
    ),

    # HDMI Output
    ("hdmi_out", 0,
        Subsignal("clk_p", Pins("G16")),
        Subsignal("clk_n", Pins("G15")),
        Subsignal("data0_p", Pins("J14")),
        Subsignal("data0_n", Pins("H14")),
        Subsignal("data1_p", Pins("J15")),
        Subsignal("data1_n", Pins("H15")),
        Subsignal("data2_p", Pins("K17")),
        Subsignal("data2_n", Pins("J17")),
        IOStandard("LVCMOS33D"),
        Misc("PULL_MODE=NONE DRIVE=3.5")
    ),

    # Ethernet RGMII
    ("eth", 0,
        Subsignal("tx_data", Pins("D21 E21 D22 E22")),
        Subsignal("tx_en", Pins("F21")),
        Subsignal("gtxclk", Pins("F20")),
        Subsignal("phy_clk", Pins("V19")),
        Subsignal("rst_n", Pins("W20")),
        IOStandard("LVCMOS33"),
        Misc("PULL_MODE=NONE")
    ),

    # SD Card
    ("sdcard", 0,
        Subsignal("clk", Pins("V15"), Misc("DRIVE=8")),
        Subsignal("cs", Pins("W15"), Misc("DRIVE=8")),
        Subsignal("mosi", Pins("Y16"), Misc("DRIVE=8")),
        Subsignal("miso", Pins("AA15"), Misc("DRIVE=OFF")),
        IOStandard("LVCMOS33"),
        Misc("PULL_MODE=NONE")
    ),

    # Audio
    ("audio", 0,
        Subsignal("bck", Pins("Y17")),
        Subsignal("ws", Pins("AB17")),
        Subsignal("din", Pins("AA16")),
        Subsignal("pa_en", Pins("AB16")),
        IOStandard("LVCMOS33"),
        Misc("PULL_MODE=NONE")
    ),

    # Buttons
    ("btn", 0, Pins("Y12"), IOStandard("LVCMOS15"), Misc("PULL_MODE=UP")),
    ("btn", 1, Pins("AB13"), IOStandard("LVCMOS15"), Misc("PULL_MODE=UP")),

    # WS2812 LED
    ("ws2812", 0, Pins("J16"), IOStandard("LVCMOS33"), Misc("DRIVE=8")),

    # LEDs
    ("led", 0, Pins("T18"), IOStandard("LVCMOS33")),
    ("led", 1, Pins("R18"), IOStandard("LVCMOS33")),
    ("led", 2, Pins("R17"), IOStandard("LVCMOS33")),
    ("led", 3, Pins("P16"), IOStandard("LVCMOS33")),
    ("led", 4, Pins("U21"), IOStandard("LVCMOS33")),
    ("led", 5, Pins("T21"), IOStandard("LVCMOS33")),
    ("led", 6, Pins("R19"), IOStandard("LVCMOS33")),
    ("led", 7, Pins("P19"), IOStandard("LVCMOS33")),

    # SDRAM
    ("sdram", 0,
        Subsignal("a", Pins("B18 D17 D20 C17 A18 A19 D14 D15 E16 C18 C19 E19 D19")),
        Subsignal("ba", Pins("C20 F15")),
        Subsignal("dq", Pins("B16 B15 A16 A15 A20 B20 A21 B21 A13 A14 C13 B13 C14 C15 E13 E14")),
        Subsignal("dm", Pins("F13 F14")),
        Subsignal("clk", Pins("B17")),
        Subsignal("cas", Pins("E17")),
        Subsignal("ras", Pins("F16")),
        Subsignal("we", Pins("D16")),
        Subsignal("cs", Pins("F19")),
        IOStandard("LVCMOS33"),
        Misc("DRIVE=8")
    ),

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

# Platform -----------------------------------------------------------------------------------------

class Platform(GowinPlatform):
    default_clk_name = "sys_clk"
    default_clk_period = 1e9/50e6  # Assuming 50MHz clock

    def __init__(self, toolchain="gowin"):
        GowinPlatform.__init__(self, "GW5A-LV60MG121C1/IrES", _io, [], toolchain=toolchain, devicename="GW5A-60")

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
