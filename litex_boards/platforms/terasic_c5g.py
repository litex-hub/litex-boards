#
# This file is part of LiteX-Boards.
#
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import IOStandard, Pins, Subsignal
from litex.build.altera import AlteraPlatform
from litex.build.altera.programmer import USBBlaster

# IOs ----------------------------------------------------------------------------------------------

# Pin assignments follow the Terasic Cyclone V GX Starter Kit User Manual, chapter 3.
_io = [
    # Clocks from the fixed 50 MHz oscillator.
    ("clk50", 0, Pins("R20"), IOStandard("3.3-V LVTTL")),
    ("clk50", 1, Pins("N20"), IOStandard("3.3-V LVTTL")),

    # Programmable Si5338 outputs at their factory defaults.
    ("clk50", 2, Pins("H12"), IOStandard("2.5 V")),
    ("clk50", 3, Pins("M10"), IOStandard("2.5 V")),
    ("clk125", 0,
        Subsignal("p", Pins("U12")),
        Subsignal("n", Pins("V12")),
        IOStandard("LVDS"),
    ),

    # USB UART (FT232R).
    ("serial", 0,
        Subsignal("tx", Pins("L9")),
        Subsignal("rx", Pins("M9")),
        IOStandard("2.5 V"),
    ),

    # Red LEDs followed by green LEDs.
    *[("user_led", i, Pins(pin), IOStandard("2.5 V")) for i, pin in enumerate(
        "F7 F6 G6 G7 J8 J7 K10 K8 H7 J10 L7 K6 D8 E9 A5 B6 H8 H9".split())],

    # Active-low buttons and CPU reset.
    *[("user_btn", i, Pins(pin), IOStandard("1.2 V")) for i, pin in enumerate(
        "P11 P12 Y15 Y16".split())],
    ("cpu_reset_n", 0, Pins("AB24"), IOStandard("3.3-V LVTTL")),

    # Slide switches.
    *[("user_sw", i, Pins(pin), IOStandard("1.2 V")) for i, pin in enumerate(
        "AC9 AE10 AD13 AC8 W11 AB10 V10 AC10 Y11 AE19".split())],

    # Active-low segments a through g. HEX2/3 share GPIO22–35 via S1/S2.
    ("seven_seg", 0, Pins("V19 V18 V17 W18 Y20 Y19 Y18"), IOStandard("1.2 V")),
    ("seven_seg", 1, Pins("AA18 AD26 AB19 AE26 AE25 AC19 AF24"), IOStandard("1.2 V")),
    ("seven_seg", 2, Pins("AD7 AD6 U20 V22 V20 W21 W20"), IOStandard("3.3-V LVTTL")),
    ("seven_seg", 3, Pins("Y24 Y23 AA23 AA22 AC24 AC23 AC22"), IOStandard("3.3-V LVTTL")),

    # IS61WV25616 asynchronous SRAM.
    ("sram", 0,
        Subsignal("a", Pins(
            "B25 B26 H19 H20 D25 C25 J20 J21 D22 E23",
            "G20 F21 E21 F22 J25 J26 N24 M24")),
        Subsignal("dq", Pins(
            "E24 E25 K24 K23 F24 G24 L23 L24 H23 H24 H22 J23 F23 G22 L22 K21")),
        Subsignal("ce_n", Pins("N23")),
        Subsignal("oe_n", Pins("M22")),
        Subsignal("we_n", Pins("G25")),
        Subsignal("lb_n", Pins("H25")),
        Subsignal("ub_n", Pins("M25")),
        IOStandard("3.3-V LVTTL"),
    ),

    # LPDDR2. Rank 1 control pins are routed but unused by the fitted memory.
    ("lpddr2", 0,
        Subsignal("ca", Pins("AE6 AF6 AF7 AF8 U10 U11 AE9 AF9 AB12 AB11"), IOStandard("1.2-V HSUL")),
        Subsignal("dq", Pins(
            "AA14 Y14 AD11 AD12 Y13 W12 AD10 AF12",
            "AC15 AB15 AC14 AF13 AB16 AA16 AE14 AF18",
            "AD16 AD17 AC18 AF19 AC17 AB17 AF21 AE21",
            "AE15 AE16 AC20 AD21 AF16 AF17 AD23 AF23"), IOStandard("1.2-V HSUL")),
        Subsignal("dm", Pins("AF11 AE18 AE20 AE24"), IOStandard("1.2-V HSUL")),
        Subsignal("cke", Pins("AF14 AE13"), IOStandard("1.2-V HSUL")),
        Subsignal("cs_n", Pins("R11 T11"), IOStandard("1.2-V HSUL")),
        Subsignal("ck_p", Pins("N10"), IOStandard("DIFFERENTIAL 1.2-V HSUL")),
        Subsignal("ck_n", Pins("P10"), IOStandard("DIFFERENTIAL 1.2-V HSUL")),
        Subsignal("dqs_p", Pins("V13 U14 V15 W16"), IOStandard("DIFFERENTIAL 1.2-V HSUL")),
        Subsignal("dqs_n", Pins("W13 V14 W15 W17"), IOStandard("DIFFERENTIAL 1.2-V HSUL")),
    ),
    ("lpddr2_rzq", 0, Pins("AE11"), IOStandard("1.2 V")),

    # Shared I²C control bus.
    ("i2c", 0,
        Subsignal("scl", Pins("B7")),
        Subsignal("sda", Pins("G11")),
        IOStandard("2.5 V"),
    ),

    # Alternate modes for the same microSD socket.
    ("sdcard", 0,
        Subsignal("clk", Pins("AB6")),
        Subsignal("cmd", Pins("W8")),
        Subsignal("data", Pins("U7 T7 V8 T8")),
        IOStandard("3.3-V LVTTL"),
    ),
    ("spisdcard", 0,
        Subsignal("clk", Pins("AB6")),
        Subsignal("mosi", Pins("W8")),
        Subsignal("miso", Pins("U7")),
        Subsignal("cs_n", Pins("T8")),
        IOStandard("3.3-V LVTTL"),
    ),

    # ADC serving the Arduino analog header.
    ("adc", 0,
        Subsignal("convst", Pins("AB22")),
        Subsignal("sck", Pins("AA21")),
        Subsignal("mosi", Pins("Y10")),
        Subsignal("miso", Pins("W10")),
        IOStandard("1.2 V"),
    ),

    # HSMC dedicated transceiver lanes and programmable reference clocks.
    ("hsmc_xcvr", 0,
        Subsignal("rx_p", Pins("AD2 AB2 Y2 V2")),
        Subsignal("rx_n", Pins("AD1 AB1 Y1 V1")),
        Subsignal("tx_p", Pins("AE4 AC4 AA4 W4")),
        Subsignal("tx_n", Pins("AE3 AC3 AA3 W3")),
        IOStandard("1.5-V PCML"),
    ),
    ("xcvr_refclk", 0,
        Subsignal("p", Pins("V6")),
        Subsignal("n", Pins("W6")),
        IOStandard("1.5-V PCML"),
    ),
    ("xcvr_refclk", 1,
        Subsignal("p", Pins("N7")),
        Subsignal("n", Pins("P6")),
        IOStandard("1.5-V PCML"),
    ),
]

# GPIO uses schematic signal indices (GPIO0–35). Arduino D0–D15 share GPIO3–18.
_gpio = (
    "T21 D26 K25 E26 K26 M26 M21 P20 T22 T19 U19 U22 "
    "P8 R8 R9 R10 F26 Y9 G26 Y8 AA7 AA6 "
    "AD7 AD6 U20 V22 V20 W21 W20 Y24 Y23 AA23 AA22 AC24 AC23 AC22"
).split()
_connectors = [
    ("GPIO", " ".join(_gpio)),
    ("ARDUINO", " ".join(_gpio[3:19])),
    # HSMC fabric pins by schematic signal name. I2C uses the shared resource above.
    ("HSMC", {
        "CLKIN0": "N9",
        "CLKIN_P1": "G15", "CLKIN_N1": "G14",
        "CLKIN_P2": "L8",  "CLKIN_N2": "K9",
        "CLKOUT0": "A7",
        "CLKOUT_P1": "A19", "CLKOUT_N1": "A18",
        "CLKOUT_P2": "A17", "CLKOUT_N2": "A16",
        **{f"D{i}": pin for i, pin in enumerate("D11 H14 D12 H13".split())},
        **{f"RX_P{i}": pin for i, pin in enumerate(
            "N12 M11 H18 L12 H15 J12 G16 G12 E18 F16 E13 C14 E16 D18 E20 D21 B24".split())},
        **{f"RX_N{i}": pin for i, pin in enumerate(
            "M12 L11 H17 K11 J16 J11 G17 F12 F18 E15 D13 D15 D16 D17 E19 D20 A24".split())},
        **{f"TX_P{i}": pin for i, pin in enumerate(
            "E10 C9 D10 A12 B10 C20 B15 B22 C13 A8 B12 C23 A14 A23 C17 C19 B21".split())},
        **{f"TX_N{i}": pin for i, pin in enumerate(
            "E11 B9 C10 B11 A11 B19 C15 A21 C12 A9 A13 C22 B14 A22 B17 C18 B20".split())},
    }),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self, toolchain="quartus"):
        AlteraPlatform.__init__(self, "5CGXFC5C6F27C7", _io, connectors=_connectors, toolchain=toolchain)

    def create_programmer(self):
        return USBBlaster()

    def do_finalize(self, fragment):
        AlteraPlatform.do_finalize(self, fragment)
        for i in range(4):
            self.add_period_constraint(self.lookup_request("clk50", i, loose=True), self.default_clk_period)
        self.add_period_constraint(self.lookup_request("clk125", loose=True), 1e9/125e6)
