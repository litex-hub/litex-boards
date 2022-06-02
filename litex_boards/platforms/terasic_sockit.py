#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 Hans Baier <hansfbaier@gmail.com>
#
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.altera            import AlteraPlatform
from litex.build.altera.programmer import USBBlaster
from litex.build.generic_platform  import Pins, IOStandard, Subsignal, Misc

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk.
    ("clk50", 0, Pins("AF14"), IOStandard("3.3-V LVTTL")),

    # Leds.
    ("user_led", 0, Pins("AF10"), IOStandard("3.3-V LVTTL")),
    ("user_led", 1, Pins("AD10"), IOStandard("3.3-V LVTTL")),
    ("user_led", 2, Pins("AE11"), IOStandard("3.3-V LVTTL")),
    ("user_led", 3, Pins("AD7"),  IOStandard("3.3-V LVTTL")),

    # Buttons.
    ("user_btn", 0, Pins("AE9"),  IOStandard("3.3-V LVTTL")),
    ("user_btn", 1, Pins("AE12"), IOStandard("3.3-V LVTTL")),
    ("user_btn", 2, Pins("AD9"),  IOStandard("3.3-V LVTTL")),
    ("user_btn", 3, Pins("AD11"), IOStandard("3.3-V LVTTL")),

    # Switches
    ("user_sw", 0, Pins("W25"),  IOStandard("3.3-V LVTTL")),
    ("user_sw", 1, Pins("V25"),  IOStandard("3.3-V LVTTL")),
    ("user_sw", 2, Pins("AC28"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 3, Pins("AC29"), IOStandard("3.3-V LVTTL")),

    # MiSTer SDRAM (via GPIO expansion board on J2).
    ("sdram_clock", 0, Pins("D10"), IOStandard("3.3-V LVTTL")),
    ("sdram", 0,
        Subsignal("a",     Pins(
            "B1 C2 B2 D2 D9 C7 E12 B7",
            "D12 A11 B6 D11 A10")),
        Subsignal("ba",    Pins("B5 A4")),
        Subsignal("cs_n",  Pins("A3")),
        Subsignal("cke",   Pins("B3")), # CKE not connected on XS 2.2/2.4.
        Subsignal("ras_n", Pins("E9")),
        Subsignal("cas_n", Pins("A6")),
        Subsignal("we_n",  Pins("A5")),
        Subsignal("dq", Pins(
            "F14 G15 F15 H15 G13 A13 H14 B13",
            "C13 C8 B12 B8 F13 C12 B11 E13"),
        ),
        Subsignal("dm", Pins("AB27 AA26")), # DQML/DQMH not connected on XS 2.2/2.4
        IOStandard("3.3-V LVTTL"),
        Misc("CURRENT_STRENGTH_NEW \"MAXIMUM CURRENT\""),
    ),

    # DDR3 SDRAM.
    ("ddram", 0,
        Subsignal("a", Pins(
            "AJ14 AK14 AH12 AJ12 AG15 AH15 AK12 AK13",
            "AH13 AH14 AJ9  AK9  AK7  AK8  AG12"),
            IOStandard("SSTL15"),
        ),
        Subsignal("ba",    Pins("AH10 AJ11 AK11"), IOStandard("SSTL-15 CLASS I"), ),
        Subsignal("ras_n", Pins("AH8"), IOStandard("SSTL-15 CLASS I")),
        Subsignal("cas_n", Pins("AH7"), IOStandard("SSTL-15 CLASS I")),
        Subsignal("we_n",  Pins("AJ6"), IOStandard("SSTL-15 CLASS I")),
        Subsignal("dm", Pins("AH17 AG23 AK23 AJ27"),
            IOStandard("SSTL-15 CLASS I"),
            Misc("OUTPUT_TERMINATION=SERIES 50 OHM WITH CALIBRATION")
        ),
        Subsignal("dq", Pins(
            "AF18 AE17 AG16 AF16 AH20 AG21 AJ16 AH18",
            "AK18 AJ17 AG18 AK19 AG20 AF19 AJ20 AH24",
            "AE19 AE18 AG22 AK22 AF21 AF20 AH23 AK24",
            "AF24 AF23 AJ24 AK26 AE23 AE22 AG25 AK27"),
            IOStandard("SSTL-15 CLASS I"),
            Misc("INPUT_TERMINATION=PARALLEL 50 OHM WITH CALIBRATION"),
            Misc("OUTPUT_TERMINATION=SERIES 50 OHM WITH CALIBRATION"),
        ),
        Subsignal("dqs_p", Pins("V16 V17 Y17 AC20"),
            IOStandard("DIFFERENTIAL 1.5-V SSTL CLASS I"),
            Misc("INPUT_TERMINATION=PARALLEL 50 OHM WITH CALIBRATION"),
            Misc("OUTPUT_TERMINATION=SERIES 50 OHM WITH CALIBRATION")
        ),
        Subsignal("dqs_n", Pins("W16 W17 AA18 AD19"),
            IOStandard("DIFFERENTIAL 1.5-V SSTL CLASS I"),
            Misc("INPUT_TERMINATION=PARALLEL 50 OHM WITH CALIBRATION"),
            Misc("OUTPUT_TERMINATION=SERIES 50 OHM WITH CALIBRATION")
        ),
        Subsignal("clk_p", Pins("AA14"),
            IOStandard("DIFFERENTIAL 1.5-V SSTL CLASS I"),
            Misc("OUTPUT_TERMINATION=SERIES 50 OHM WITH CALIBRATION"),
            Misc("D5_DELAY=2")
        ),
        Subsignal("clk_n", Pins("AA15"),
            IOStandard("DIFFERENTIAL 1.5-V SSTL CLASS I"),
            Misc("OUTPUT_TERMINATION=SERIES 50 OHM WITH CALIBRATION"),
            Misc("D5_DELAY=2")
        ),
        Subsignal("cs_n",    Pins("AB15"), IOStandard("SSTL-15 CLASS I")),
        Subsignal("cke",     Pins("AJ21"), IOStandard("SSTL-15 CLASS I")),
        Subsignal("odt",     Pins("AE16"), IOStandard("SSTL-15 CLASS I")),
        Subsignal("reset_n", Pins("AK21"), IOStandard("SSTL-15 CLASS I")),
        Subsignal("rzq",     Pins("AG1"),  IOStandard("SSTL-15")),
        Misc("CURRENT_STRENGTH_NEW=MAXIMUM CURRENT")
        ),

    # VGA.
    ("vga", 0,
        Subsignal("sync_n",  Pins("AG2")),
        Subsignal("blank_n", Pins("AH3")),
        Subsignal("clk",     Pins("W20")),
        Subsignal("hsync_n", Pins("AD12")),
        Subsignal("vsync_n", Pins("AC12")),
        Subsignal("r", Pins("AG5  AA12 AB12 AF6  AG6  AJ2  AH5  AJ1")),
        Subsignal("g", Pins("Y21  AA25 AB26 AB22 AB23 AA24 AB25 AE27")),
        Subsignal("b", Pins("AE28 Y23  Y24  AG28 AF28 V23  W24  AF29")),
        IOStandard("3.3-V LVTTL")
    ),

    # IrDA.
    ("irda", 0,
        Subsignal("irda_rxd", Pins("AH2")),
        IOStandard("3.3-V LVTTL")
    ),

    # Temperatue.
    ("temperature", 0,
        Subsignal("temp_cs_n", Pins("AF8")),
        Subsignal("temp_din",  Pins("AG7")),
        Subsignal("temp_dout", Pins("AG1")),
        Subsignal("temp_sclk", Pins("AF9")),
        IOStandard("3.3-V LVTTL")
    ),

    # Audio.
    ("audio", 0,
        Subsignal("aud_adclrck",  Pins("AG30")),
        Subsignal("aud_adcdat",   Pins("AC27")),
        Subsignal("aud_daclrck",  Pins("AH4")),
        Subsignal("aud_dacdat",   Pins("AG3")),
        Subsignal("aud_xck",      Pins("AC9")),
        Subsignal("aud_bclk",     Pins("AE7")),
        Subsignal("aud_i2c_sclk", Pins("AH30")),
        Subsignal("aud_i2c_sdat", Pins("AF30")),
        Subsignal("aud_mute",     Pins("AD26")),
        IOStandard("3.3-V LVTTL")
    ),

    # GPIO Serial.
    ("gpio_serial", 0,
        Subsignal("tx", Pins("J3:9")),
        Subsignal("rx", Pins("J3:10")),
        IOStandard("3.3-V LVTTL"))
]

# Connectors ---------------------------------------------------------------------------------------

_connectors_hsmc_gpio_daughterboard = [
    ("J2", "- G15 F14 H15 F15 A13 G13 B13 H14 B11 E13 - - " +
           "C12 F13 B8 B12 C8 C13 A10 D10 A11 D11 B7 D12 C7 E12 A5 D9 - - " +
           "A6 E9 A3 B5 A4 B6 B1 C2 B2 D2"),
    ("J2p", "- D1 E1 E11 F11"), # Top to bottom, starting with 57.

    ("J3", "- AB27 F8 AA26 F9 B3 G8 C3 H8 D4 H7 - - " +
           "E4 J7 E2 K8 E3 K7 E6 J9 E7 J10 C4 J12 D5 G10 C5 J12 - - " +
           "D6 K12 F6 G11 G7 G12 D7 A8 E8 A9"),
    ("J3p", "- C9 C10 H12 H13"), # Top to bottom, starting with 117.

    ("J4", "- - - AD3 AE1 AD4 AE2 - - AB3 AC1 - - " +
           "AB4 AC2 - - Y3 AA1 Y4 AA2 - - V3 W1 V4 W2 - - - -" +
           "T3 U1 T4 R1 - R2 P3 U2 P4 -"),
    ("J4p", "- M3 M4 - H3 H4 J14 AD29 - N1 N2 - J1 J2") # Top to bottom, starting with 169.
]

# Platform -----------------------------------------------------------------------------------------

_device_map = {
    "revb" : "5CSXFC6D6F31C8ES",
    "revc" : "5CSXFC6D6F31C8ES",
    "revd" : "5CSXFC6D6F31C8",
}

class Platform(AlteraPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self, revision="revd", toolchain="quartus"):
        assert revision in _device_map.keys()
        self.revision = revision
        AlteraPlatform.__init__(self, _device_map[revision], _io, connectors=_connectors_hsmc_gpio_daughterboard, toolchain=toolchain)

    def create_programmer(self):
        return USBBlaster(cable_name="CV SoCKit")

    def do_finalize(self, fragment):
        AlteraPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
