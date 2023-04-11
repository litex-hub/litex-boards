#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2014-2019 Hans Baier <hansfbaier@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.altera.programmer import USBBlaster

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst.
    ("clk10",     0, Pins("M9"),    IOStandard("2.5 V")),
    ("clk50",     0, Pins("M8"),    IOStandard("2.5 V")),
    ("clk50",     1, Pins("P11"),   IOStandard("3.3-V LVTTL")),
    ("rst_n",     0, Pins("P9:10"), IOStandard("3.3-V LVTTL")),
    ("power_btn", 0, Pins("P9:9"),  IOStandard("3.3-V LVTTL")),

    # Leds.
    ("user_led", 0, Pins("C7"),  IOStandard("1.2 V")),
    ("user_led", 1, Pins("C8"),  IOStandard("1.2 V")),
    ("user_led", 2, Pins("A6"),  IOStandard("1.2 V")),
    ("user_led", 3, Pins("B7"),  IOStandard("1.2 V")),
    ("user_led", 4, Pins("C4"),  IOStandard("1.2 V")),
    ("user_led", 5, Pins("A5"),  IOStandard("1.2 V")),
    ("user_led", 6, Pins("B4"),  IOStandard("1.2 V")),
    ("user_led", 7, Pins("C5"),  IOStandard("1.2 V")),

    # Buttons.
    ("user_btn", 0, Pins("H21"),  IOStandard("1.5 V SCHMITT TRIGGER")),
    ("user_btn", 1, Pins("H22"),  IOStandard("1.5 V SCHMITT TRIGGER")),

    # Switches.
    ("user_sw", 0, Pins("J21"),  IOStandard("1.5 V SCHMITT TRIGGER")),
    ("user_sw", 1, Pins("J22"),  IOStandard("1.5 V SCHMITT TRIGGER")),

    # CapSense Buttons (I2C).
    ("cap_sense_i2c", 0,
        Subsignal("scl", Pins("AB2")),
        Subsignal("sda", Pins("AB3")),
        IOStandard("3.3-V LVTTL")
    ),

    # Temperature sensor.
    ("temp", 0,
        Subsignal("cs_n", Pins("PIN_AB4")),
        Subsignal("sc",   Pins("PIN_AA1")),
        Subsignal("sio",  Pins("PIN_Y2")),
        IOStandard("3.3-V LVTTL")
    ),

    # Power monitor (I2C).
    ("pmonitor_i2c", 0,
        Subsignal("alert", Pins("Y4")),
        Subsignal("scl",   Pins("Y3")),
        Subsignal("sda",   Pins("Y1")),
        IOStandard("3.3-V LVTTL")
    ),

    # Temperature / Humidity sensor (I2C).
    ("rh_temp_i2c", 0,
        Subsignal("drdy_n", Pins("AB9")),
        Subsignal("scl",    Pins("Y10")),
        Subsignal("sda",    Pins("AA10")),
        IOStandard("3.3-V LVTTL")
    ),

    # Proximity / Ambient light sensor (I2C).
    ("proximity_i2c", 0,
        Subsignal("scl",    Pins("Y8")),
        Subsignal("sda",    Pins("AA8")),
        Subsignal("int",    Pins("AA9")),
        IOStandard("3.3-V LVTTL")
    ),

    # Accelerometer.
    ("gsensor", 0,
        Subsignal("sdi", Pins("C6")),
        Subsignal("sdo", Pins("D5")),
        Subsignal("cs_n", Pins("E9")),
        Subsignal("sclk", Pins("B5")),
        Subsignal("int1", Pins("E8")),
        Subsignal("int2", Pins("D7")),
        IOStandard("1.2 V")
    ),

    # DDR3 SDRAM.
    ("ddram", 0,
        Subsignal("a", Pins(
            "E21 V20 V21 C20 Y21 J14 V18 U20",
            "Y20 W22 C22 Y22 N18 V22 W20"),
            IOStandard("SSTL-15"),
        ),
        Subsignal("ba",    Pins("D19 W19 F19"), IOStandard("SSTL-15")),
        Subsignal("ras_n", Pins("D22"), IOStandard("SSTL-15")),
        Subsignal("cas_n", Pins("E20"), IOStandard("SSTL-15")),
        Subsignal("we_n",  Pins("E22"), IOStandard("SSTL-15")),
        Subsignal("dm", Pins("N19 J15"),
            IOStandard("SSTL-15"),
            Misc("OUTPUT_TERMINATION \"SERIES 40 OHM WITH CALIBRATION\""),
            Misc("DM_PIN ON")
        ),
        Subsignal("dq", Pins(
            "L20 L19 L18 M15 M18 M14 M20 N20",
            "K19 K18 J18 K20 H18 J20 H20 H19"),
            IOStandard("SSTL-15"),
            Misc("OUTPUT_TERMINATION \"SERIES 40 OHM WITH CALIBRATION\""),
        ),
        Subsignal("dqs_p", Pins("L14 K14"),
            IOStandard("DIFFERENTIAL 1.5-V SSTL"),
            Misc("OUTPUT_TERMINATION \"SERIES 40 OHM WITH CALIBRATION\"")
        ),
        Subsignal("dqs_n", Pins("L15 K15"),
            IOStandard("DIFFERENTIAL 1.5-V SSTL"),
            Misc("OUTPUT_TERMINATION \"SERIES 40 OHM WITH CALIBRATION\"")
        ),
        Subsignal("clk_p", Pins("D18"),
            IOStandard("DIFFERENTIAL 1.5-V SSTL"),
            Misc("OUTPUT_TERMINATION \"SERIES 40 OHM WITH CALIBRATION\""),
            Misc("CKN_CK_PAIR ON -from ddram_clk_n")
        ),
        Subsignal("clk_n", Pins("E18"),
            IOStandard("DIFFERENTIAL 1.5-V SSTL"),
            Misc("OUTPUT_TERMINATION \"SERIES 40 OHM WITH CALIBRATION\""),
        ),
        Subsignal("cs_n",    Pins("F22"), IOStandard("SSTL-15")),
        Subsignal("cke",     Pins("B22"), IOStandard("SSTL-15")),
        Subsignal("odt",     Pins("G22"), IOStandard("SSTL-15")),
        Subsignal("reset_n", Pins("U19"), IOStandard("SSTL-15")),
    ),

    # Audio.
    ("audio", 0,
        Subsignal("bclk",       Pins("R14")),
        Subsignal("reset_n",    Pins("M21")),
        Subsignal("din_mfp1",   Pins("P15")),
        Subsignal("dout_mfp2",  Pins("P18")),
        Subsignal("gpio_mfp5",  Pins("M22")),
        Subsignal("mclk",       Pins("P14")),
        Subsignal("miso_mfp4",  Pins("N21")),
        Subsignal("sclk_mfp3",  Pins("P19")),
        Subsignal("scl_ss_n",   Pins("P20")),
        Subsignal("sda_mosi",   Pins("P21")),
        Subsignal("spi_select", Pins("N22")),
        Subsignal("wclk",       Pins("R15")),
        IOStandard("1.5 V")
    ),

    # USB ULPI (TUSB1210).
    ("ulpi", 0,
        Subsignal("fault_n", Pins("D8"),  IOStandard("1.2 V")),
        Subsignal("cs",      Pins("J11"), IOStandard("1.8 V")),
        Subsignal("clk",     Pins("H11"), IOStandard("1.2 V")),
        Subsignal("stp",     Pins("J12"), IOStandard("1.8 V")),
        Subsignal("dir",     Pins("J13"), IOStandard("1.8 V")),
        Subsignal("nxt",     Pins("H12"), IOStandard("1.8 V")),
        Subsignal("reset_n", Pins("E16"), IOStandard("1.8 V")),
        Subsignal("data",    Pins("E12 E13 H13 E14 H14 D15 E15 F15"), IOStandard("1.8 V")),
    ),

    # SDCard.
    ("sdcard", 0,
        Subsignal("sel",    Pins("P13"), IOStandard("3.3-V LVTTL")),
        Subsignal("fb_clk", Pins("R22")),
        Subsignal("clk",    Pins("T20")),
        Subsignal("cmd",    Pins("T21")),
        Subsignal("data",   Pins("R18 T18 T19 R20")),
        IOStandard("1.5 V")
    ),

    # SPI SDCard.
    ("spisdcard", 0,
        Subsignal("clk",    Pins("T20")),
        Subsignal("cs_n",   Pins("R20")),
        Subsignal("mosi",   Pins("T21")),
        Subsignal("miso",   Pins("R18")),
        IOStandard("1.5 V")
    ),
    ("spisdcard_aux", 0,
        Subsignal("sel",      Pins("P13"), IOStandard("3.3-V LVTTL")),
        Subsignal("cmd_dir",  Pins("U22")),
        Subsignal("d0_dir",   Pins("T22")),
        Subsignal("d123_dir", Pins("U21")),
        Subsignal("dat1",     Pins("T18")),
        Subsignal("dat2",     Pins("T19")),
        IOStandard("1.5 V")
    ),

    # MII Ethernet.
    ("eth_clocks", 0,
        Subsignal("tx", Pins("T5")),
        Subsignal("rx", Pins("T6")),
        IOStandard("2.5 V"),
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("R3")),
        Subsignal("mdio",    Pins("N8")),
        Subsignal("mdc",     Pins("R5")),
        Subsignal("rx_dv",   Pins("P4")),
        Subsignal("rx_er",   Pins("V1")),
        Subsignal("rx_data", Pins("U5 U4 R7 P8")),
        Subsignal("tx_en",   Pins("P3")),
        Subsignal("tx_data", Pins("U2 W1 N9 W2")),
        Subsignal("col",     Pins("R4")),
        Subsignal("crs",     Pins("P5")),
        Subsignal("pcf_en",  Pins("V9"), IOStandard("3.3-V LVTTL")),
        IOStandard("2.5 V"),
    ),

    # HDMI.
    ("hdmi", 0,
        Subsignal("r", Pins("C18 D17 C17 C19 D14 B19 D13 A19")),
        Subsignal("g", Pins("C14 A17 B16 C15 A14 A15 A12 A16")),
        Subsignal("b", Pins("A13 C16 C12 B17 B12 B14 A18 C13")),
        Subsignal("clk",   Pins("A20")),
        Subsignal("de",    Pins("C9")),
        Subsignal("hsync", Pins("B11")),
        Subsignal("vsync", Pins("C11")),
        Subsignal("int",   Pins("B10")),
        Misc("FAST_OUTPUT_REGISTER ON"),
        IOStandard("1.8 V")
    ),
    # HDMI_I2C.
    ("hdmi_i2c", 0,
        Subsignal("scl",    Pins("C10")),
        Subsignal("sda",    Pins("B15")),
        IOStandard("1.8 V")
    ),
    # HDMI_I2S.
    ("hdmi_i2s", 0,
        Subsignal("i2s",    Pins("A9 A11 A8 B8")),
        Subsignal("mclk",   Pins("A7")),
        Subsignal("lrclk",  Pins("A10")),
        Subsignal("sclk",   Pins("D12")),
        IOStandard("1.8 V")
    ),

    # MIPI.
    ("camera", 0,
        Subsignal("mclk",    Pins("U3")),
        Subsignal("clkp",    Pins("N5")),
        Subsignal("clkn",    Pins("N4")),
        Subsignal("dp",      Pins("R2 N1 T2 N2")),
        Subsignal("dn",      Pins("R1 P1 T1 N3")),
        Subsignal("reset_n", Pins("T3")),
        Subsignal("wp",      Pins("U1")),
        Subsignal("core_en", Pins("V3")),
        IOStandard("2.5 V"),
    ),
    # LP-MIPI.
    ("camera", 1,
        Subsignal("mclk",    Pins("U3"), IOStandard("2.5 V")),
        Subsignal("clkp",    Pins("E11")),
        Subsignal("clkn",    Pins("E10")),
        Subsignal("dp",      Pins("A4 C3 B1 B3")),
        Subsignal("dn",      Pins("A3 C2 B2 A2")),
        IOStandard("1.2 V"),
    ),
    ("mipi_i2c", 0,
        Subsignal("scl",    Pins("M1")),
        Subsignal("sda",    Pins("M2")),
        IOStandard("2.5 V")
    ),

    # GPIO 0.
    ("gpio", 0, Pins(
        "P8:3  P8:4  P8:5  P8:6  P8:7  P8:8  P8:9  P8:10",
        "P8:11 P8:12 P8:13 P8:14 P8:15 P8:16 P8:17 P8:18",
        "P8:19 P8:20 P8:21 P8:22 P8:23 P8:24 P8:25 P8:26",
        "P8:27 P8:28 P8:29 P8:30 P8:31 P8:32 P8:33 P8:34",
        "P8:35 P8:36 P8:37 P8:38 P8:39 P8:40 P8:41 P8:42",
        "P8:43 P8:44 P8:45 P8:46"),
        IOStandard("3.3-V LVTTL")
    ),

    # GPIO 1.
    ("gpio", 1, Pins(
        "P9:11 P9:12 P9:13 P9:14 P9:15 P9:16 P9:17 P9:18",
        "P9:19 P9:20 P9:21 P9:22 P9:23 P9:24 P9:25 P9:26",
        "P9:27 P9:28 P9:29 P9:30 P9:31 P9:41 P9:42"),
        IOStandard("3.3-V LVTTL")
    ),

    # GPIO Serial.
    ("gpio_serial", 0,
        Subsignal("tx", Pins("P8:3")),
        Subsignal("rx", Pins("P8:4")),
        IOStandard("3.3-V LVTTL"))
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    # Beagle bone black headers (numbering 1-based, Pin 0 is dummy)
    # PIN   0 1 2   3   4   5    6    7    8    9   10   11  12  13   14  15  16   17   18   19  20   21  22  23   24   25   26   27   28   29   30   31   32   33  34  35  36  37  38  39  40  41  42  43  44  45  46
    ("P8", "- - - W18 Y18 Y19 AA17 AA20 AA19 AB21 AB20 AB19 Y16 V16 AB18 V15 W17 AB17 AA16 AB16 W16 AB15 W15 Y14 AA15 AB14 AA14 AB13 AA13 AB12 AA12 AB11 AA11 AB10 Y13 Y11 W13 W12 W11 V12 V11 V13 V14 Y17 W14 U15 R13"),
    ("P9", "- - -   -   -   -    -    -    -   U6  AA2   Y5  Y6  W6   W7  W8  V8  AB8   V7  R11 AB7  AB6 AA7 AA6   Y7  V10   U7   W9   W5   R9   W4   P9    -   K4   -  J4  H3  J8  J9  F5  F4 V17  W3   -   -   -   -")
]

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6
    create_rbf         = False

    def __init__(self, toolchain="quartus"):
        AlteraPlatform.__init__(self, "10M50DAF484C6GES", _io, _connectors, toolchain=toolchain)
        # Disable config pin so bank8 can use 1.2V.
        self.add_platform_command("set_global_assignment -name AUTO_RESTART_CONFIGURATION ON")
        self.add_platform_command("set_global_assignment -name ENABLE_CONFIGURATION_PINS OFF")
        self.add_platform_command("set_global_assignment -name ENABLE_BOOT_SEL_PIN OFF")
        self.add_platform_command("set_global_assignment -name INTERNAL_FLASH_UPDATE_MODE \"SINGLE IMAGE WITH ERAM\"")
        self.add_platform_command("set_instance_assignment -name DQ_GROUP 9 -from ddram_dqs_p[0] -to ddram_dq[0]")
        self.add_platform_command("set_instance_assignment -name DQ_GROUP 9 -from ddram_dqs_p[0] -to ddram_dq[1]")
        self.add_platform_command("set_instance_assignment -name DQ_GROUP 9 -from ddram_dqs_p[0] -to ddram_dq[2]")
        self.add_platform_command("set_instance_assignment -name DQ_GROUP 9 -from ddram_dqs_p[0] -to ddram_dq[3]")
        self.add_platform_command("set_instance_assignment -name DQ_GROUP 9 -from ddram_dqs_p[0] -to ddram_dq[4]")
        self.add_platform_command("set_instance_assignment -name DQ_GROUP 9 -from ddram_dqs_p[0] -to ddram_dq[5]")
        self.add_platform_command("set_instance_assignment -name DQ_GROUP 9 -from ddram_dqs_p[0] -to ddram_dq[6]")
        self.add_platform_command("set_instance_assignment -name DQ_GROUP 9 -from ddram_dqs_p[0] -to ddram_dq[7]")
        self.add_platform_command("set_instance_assignment -name DQ_GROUP 9 -from ddram_dqs_p[1] -to ddram_dq[8]")
        self.add_platform_command("set_instance_assignment -name DQ_GROUP 9 -from ddram_dqs_p[1] -to ddram_dq[9]")
        self.add_platform_command("set_instance_assignment -name DQ_GROUP 9 -from ddram_dqs_p[1] -to ddram_dq[10]")
        self.add_platform_command("set_instance_assignment -name DQ_GROUP 9 -from ddram_dqs_p[1] -to ddram_dq[11]")
        self.add_platform_command("set_instance_assignment -name DQ_GROUP 9 -from ddram_dqs_p[1] -to ddram_dq[12]")
        self.add_platform_command("set_instance_assignment -name DQ_GROUP 9 -from ddram_dqs_p[1] -to ddram_dq[13]")
        self.add_platform_command("set_instance_assignment -name DQ_GROUP 9 -from ddram_dqs_p[1] -to ddram_dq[14]")
        self.add_platform_command("set_instance_assignment -name DQ_GROUP 9 -from ddram_dqs_p[1] -to ddram_dq[15]")
        self.add_platform_command("set_instance_assignment -name DQ_GROUP 9 -from ddram_dqs_p[0] -to ddram_dm[0]")
        self.add_platform_command("set_instance_assignment -name DQ_GROUP 9 -from ddram_dqs_p[1] -to ddram_dm[1]")

    def create_programmer(self):
        return USBBlaster(cable_name="Arrow MAX 10 DECA")

    def do_finalize(self, fragment):
        AlteraPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
        # Generate PLL clocsk in STA
        self.toolchain.additional_sdc_commands.insert(0, "derive_pll_clocks -create_base_clocks -use_net_name")
        self.toolchain.additional_sdc_commands.insert(0, "derive_clock_uncertainty")
