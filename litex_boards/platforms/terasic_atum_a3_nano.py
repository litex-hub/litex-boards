#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Gwenhael Goavec-Merou <gwenhael.goavec-merou@trabucayre.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.altera            import AlteraPlatform
from litex.build.altera.programmer import USBBlaster
from litex.build.generic_platform  import Pins, IOStandard, Subsignal, Misc
from litex.build.openfpgaloader    import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk.
    ("clk50_0", 0, Pins("K43"), IOStandard("1.2-V")),
    ("clk50_1", 0, Pins("A8"),  IOStandard("3.3-V LVCMOS")),
    ("clk50_2", 0, Pins("AH9"), IOStandard("3.3-V LVCMOS")),
    ("clk50_3", 0, Pins("R2"),  IOStandard("3.3-V LVCMOS")),

    # Buttons.
    ("user_btn", 0, Pins("E2"), IOStandard("3.3-V LVCMOS"), Misc("WEAK_PULL_UP_RESISTOR ON")),
    ("user_btn", 1, Pins("K3"), IOStandard("3.3-V LVCMOS"), Misc("WEAK_PULL_UP_RESISTOR ON")),

    # Leds.
    ("user_led", 0, Pins("AG2"), IOStandard("3.3-V LVCMOS")),
    ("user_led", 1, Pins("AM6"), IOStandard("3.3-V LVCMOS")),
    ("user_led", 2, Pins("AF1"), IOStandard("3.3-V LVCMOS")),
    ("user_led", 3, Pins("AF2"), IOStandard("3.3-V LVCMOS")),

    # Switches.
    ("user_sw", 0, Pins("A19"), IOStandard("1.2-V LVCMOS")),
    ("user_sw", 1, Pins("B24"), IOStandard("1.2-V LVCMOS")),

    # Serial.
    ("serial", 0,
        Subsignal("rx", Pins("L1")),
        Subsignal("tx", Pins("T6")),
        IOStandard("3.3-V LVCMOS"),
    ),

    # RGMII Ethernet (RTL8211F).
    ("eth_clocks", 0,
        Subsignal("tx", Pins("AY6")),
        Subsignal("rx", Pins("AT9")),
        IOStandard("1.8-V LVCMOS"),
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("AW12")),
        Subsignal("mdio",    Pins("BH7")),
        Subsignal("mdc",     Pins("BB9")),
        Subsignal("rx_ctl",  Pins("AU4")),
        Subsignal("rx_data", Pins("BF12 BF9 BB12 BH3")),
        Subsignal("tx_ctl",  Pins("AU6")),
        Subsignal("tx_data", Pins("PIN_BH10 PIN_BK10 PIN_BM2 PIN_BM3")),
        IOStandard("1.8-V LVCMOS"),
    ),

    # HDMI / TFP410.
    ("hdmi", 0,
        Subsignal("r",       Pins("F40 F32 V52 K35 V51 K32 K40 A24")), # [23:16]
        Subsignal("g",       Pins("B29 B27 A26 B26 A31 H35 A37 F35")), # [15:8]
        Subsignal("b",       Pins("G52 J52 G51 J51 M51 H43 A34 A29")), # [ 7:0]
        Subsignal("vsync",   Pins("N52")),
        Subsignal("hsync",   Pins("R52")),
        Subsignal("clk",     Pins("L51"), IOStandard("DIFFERENTIAL 1.2-V SSTL")),
        Subsignal("de",      Pins("R51")),
        Subsignal("pdn",     Pins("J1"),  IOStandard("3.3-V LVCMOS")),
        Subsignal("isel",    Pins("J2"),  IOStandard("3.3-V LVCMOS")),
        Subsignal("sda",     Pins("N2"),  IOStandard("3.3-V LVCMOS")),
        Subsignal("scl",     Pins("M2"),  IOStandard("3.3-V LVCMOS")),
        Subsignal("ddc_sda", Pins("AN1"), IOStandard("3.3-V LVCMOS")),
        Subsignal("ddc_scl", Pins("AV2"), IOStandard("3.3-V LVCMOS")),
        IOStandard("1.2-V")
    ),

    # SDCard.
    ("spisdcard", 0,
        Subsignal("clk",  Pins("Y1")),
        Subsignal("mosi", Pins("N1")),
        Subsignal("cs_n", Pins("V1")),
        Subsignal("miso", Pins("AC2")),
        IOStandard("3.3-V LVCMOS"),
    ),
    ("sdcard", 0,
        Subsignal("data", Pins("AC2 AC1 V2 V1")),
        Subsignal("cmd",  Pins("N1")),
        Subsignal("clk",  Pins("Y1")),
        IOStandard("3.3-V LVCMOS"),
    ),

    # SDR SDRAM.
    ("sdram_clock", 0, Pins("BK32"), IOStandard("1.8-V LVCMOS")),
    ("sdram", 0,
        Subsignal("a",     Pins(
            "BN26 BH27 BM26 BH21 BH26 BH18 BK18 BH32",
            "BM24 BH35 BN27 BN29 BK26")),
        Subsignal("ba",    Pins("BH43 BM29")),
        Subsignal("cs_n",  Pins("BN34")),
        Subsignal("cke",   Pins("BK40")),
        Subsignal("ras_n", Pins("BM31")),
        Subsignal("cas_n", Pins("BH40")),
        Subsignal("we_n",  Pins("BM34")),
        Subsignal("dq", Pins(
            "BM50 BM51 BN47 BM47 BL51 BH50 BK50 BH46",
            "BM37 BN37 BM42 BN42 BM44 BN45 BN39 BM45",
            " BG2  BA2  BC2  BJ1  BE4  BG1  BC1  BD1",
            " BN5  BM9  BM8 BN11  BN8 BN14 BM11 BN16")),
        Subsignal("dm", Pins("BE6 BM19 BJ2 BM14")),
        IOStandard("1.8-V LVCMOS")
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    # TMD0
    ("pmod0", "AD6 P6  AB9 AE12 P4   AA4 AH12 AA6"), # 3.3-V LVCMOS
    ("pmod1", "AR2 AJ6 AK1 AR1  AL12 AJ4 AV1  AK2"), # 3.3-V LVCMOS


    # GPIO
    ("gpio",
        "----", # 0
        #                                                    ( 1-10).
        "  B3  A11  D18  B11   H7   B5   W9   F3   U9   C2",
        #  5V  GND                                           (11-20).
        "---- ----  U12   F7   P9   K7  K10  K13   D3  H13",
        #                                        3.3V  GND   (21-30).
        "  B8  F10   A9  D10  F13  K18  F18  H21 ---- ----",
        #                                                    (31-40).
        " D26  K21  H27  F26  B14  F27  B16  A14  F21  B19",
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name   = "clk50_1"
    default_clk_period = 1e9/50e6

    def __init__(self, toolchain="quartus"):
        AlteraPlatform.__init__(self, "A3CZ135BB18AE7S", _io, _connectors, toolchain=toolchain)
        self.create_rbf = True
        self.create_svf = False # Not supported for Agilex5 family.
        self.add_platform_command("set_global_assignment -name ENABLE_INTERMEDIATE_SNAPSHOTS \"ON\"")
        self.add_platform_command("set_global_assignment -name USE_CONF_DONE SDM_IO16")
        self.add_platform_command("set_global_assignment -name USE_INIT_DONE SDM_IO13")
        self.add_platform_command("set_global_assignment -name STRATIXV_CONFIGURATION_SCHEME \"ACTIVE SERIAL X4\"")
        self.add_platform_command("set_global_assignment -name ACTIVE_SERIAL_CLOCK AS_FREQ_100MHZ")
        self.add_platform_command("set_global_assignment -name DEVICE_INITIALIZATION_CLOCK OSC_CLK_1_125MHZ")

        # Calculates clock uncertainties
        self.toolchain.additional_sdc_commands.append("derive_clock_uncertainty")

    def create_programmer(self, programmer="openFPGALoader"):
        if programmer == "openFPGALoader":
            return OpenFPGALoader(cable="usb-blasterIII")
        else:
            return USBBlaster(cable_name="USB Blaster III")

    def do_finalize(self, fragment):
        AlteraPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50_1", loose=True), 1e9/50e6)
