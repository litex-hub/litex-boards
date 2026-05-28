#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2024-2026 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2024 Gwenhael Goavec-Merou <gwenhael@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause
#
# More complete Agilex 5 test project:
# https://github.com/enjoy-digital/litex_agilex5_test

from litex.build.altera            import AlteraPlatform
from litex.build.altera.programmer import USBBlaster
from litex.build.generic_platform  import Pins, IOStandard, Subsignal, Misc

# Variants -----------------------------------------------------------------------------------------

_variants = {
    "production": "A5ED065BB32AE4S",
    "es":         "A5ED065BB32AE6SR0",
}

_speedgrades = {
    "production": "-4S",
    "es":         "-6S",
}

# IOs ----------------------------------------------------------------------------------------------

_io = [

    # Clk.
    ("clk100", 0, Pins("D8"),    IOStandard("3.3-V LVCMOS")), # Si5332 OUT4.
    ("clk100", 1, Pins("BF111"), IOStandard("3.3-V LVCMOS")), # Si5332 OUT5.
    ("clk125", 0, Pins("A23"),   IOStandard("1.8-V LVCMOS")), # Si5518A OUT1 (RGMII).

    # Serial.
    ("serial", 0,
        Subsignal("rx", Pins("CJ2")),
        Subsignal("tx", Pins("CK4")),
        IOStandard("3.3-V LVCMOS"),
    ),

    # Leds.
    ("user_led", 0, Pins("BM59"), IOStandard("1.1 V")),
    ("user_led", 1, Pins("BH59"), IOStandard("1.1 V")),
    ("user_led", 2, Pins("BH62"), IOStandard("1.1 V")),
    ("user_led", 3, Pins("BK59"), IOStandard("1.1 V")),

    # Switches.
    ("user_sw", 0, Pins("CH12"), IOStandard("3.3-V LVCMOS")),
    ("user_sw", 1, Pins("BU22"), IOStandard("3.3-V LVCMOS")),
    ("user_sw", 2, Pins("BW19"), IOStandard("3.3-V LVCMOS")),
    ("user_sw", 3, Pins("BH28"), IOStandard("3.3-V LVCMOS")),

    # Buttons.
    ("user_btn", 0, Pins("BK31"), IOStandard("3.3-V LVCMOS"), Misc("WEAK_PULL_UP_RESISTOR ON")),
    ("user_btn", 1, Pins("BP22"), IOStandard("3.3-V LVCMOS"), Misc("WEAK_PULL_UP_RESISTOR ON")),
    ("user_btn", 2, Pins("BK28"), IOStandard("3.3-V LVCMOS"), Misc("WEAK_PULL_UP_RESISTOR ON")),
    ("user_btn", 3, Pins("BR22"), IOStandard("3.3-V LVCMOS"), Misc("WEAK_PULL_UP_RESISTOR ON")),

    # LPDDR4. The EMIF IP owns the detailed memory IO constraints.
    ("lpddr_refclk", 0,
        Subsignal("p", Pins("BW78"), IOStandard("1.1V TRUE DIFFERENTIAL SIGNALING")),
        Subsignal("n", Pins("CA78"), IOStandard("1.1V TRUE DIFFERENTIAL SIGNALING")),
    ),
    ("lpddr4", 0,
        Subsignal("clk_p",   Pins("BM81")),
        Subsignal("clk_n",   Pins("BP81")),
        Subsignal("cke",     Pins("BR81")),
        Subsignal("reset_n", Pins("BH92")),
        Subsignal("cs",      Pins("BR78")),
        Subsignal("ca",      Pins("BR89 BU89 BR92 BU92 BW89 CA89")),
        Subsignal("dq",      Pins(
            "CA71 CC71 CH71 CF71 CH62 CF62 CH59 CF59",
            "BR59 BU59 BW59 CA59 BU71 BU69 BR71 BR69",
            "CC92 CF92 CA92 CH92 CC81 CF78 CH78 CA81",
            "CL82 CK80 CK76 CL76 CK97 CL97 CK94 CL91"),
        ),
        Subsignal("dqs_p",   Pins("CH69 BW69 CH89 CL88")),
        Subsignal("dqs_n",   Pins("CF69 CA69 CF89 CK88")),
        Subsignal("dmi",     Pins("CA62 BU62 CF81 CK85")),
        Subsignal("rzq",     Pins("BH89")),
    ),

    # SGMII Ethernet (88E2110 ENET1).
    ("eth_clocks", 0,
        Subsignal("p", Pins("AT120"), IOStandard("CURRENT MODE LOGIC (CML)")),
        Subsignal("n", Pins("AT115"), IOStandard("CURRENT MODE LOGIC (CML)")),
    ),
    ("eth", 0,
        Subsignal("int_n", Pins("BK118"), IOStandard("3.3-V LVCMOS")),
        Subsignal("rst_n", Pins("BM118"), IOStandard("3.3-V LVCMOS")),
        Subsignal("mdc",   Pins("BP112"), IOStandard("3.3-V LVCMOS")),
        Subsignal("mdio",  Pins("BM112"), IOStandard("3.3-V LVCMOS")),
        Subsignal("rx_p",  Pins("AK135")),
        Subsignal("rx_n",  Pins("AK133")),
        Subsignal("tx_p",  Pins("AL129")),
        Subsignal("tx_n",  Pins("AL126")),
    ),

    # RGMII Ethernet (88E1512).
    ("eth_clocks", 2,
        Subsignal("tx", Pins("B14")),
        Subsignal("rx", Pins("B23")),
        IOStandard("1.8-V LVCMOS"),
    ),
    ("eth", 2,
        Subsignal("int_n",   Pins("B35")),
        Subsignal("rst_n",   Pins("D34")),
        Subsignal("mdc",     Pins("B26")),
        Subsignal("mdio",    Pins("A39")),
        Subsignal("rx_ctl",  Pins("B20")),
        Subsignal("rx_data", Pins("A30 B30 A33 A35")),
        Subsignal("tx_ctl",  Pins("A14")),
        Subsignal("tx_data", Pins("A8 B4 A11 B11")),
        IOStandard("1.8-V LVCMOS"),
    ),

    # SFP+.
    ("sfp_refclk", 0,
        Subsignal("p", Pins("BC29")),
        Subsignal("n", Pins("BC25")),
    ),
    ("sfp", 0,
        Subsignal("txp", Pins("BL7")),
        Subsignal("txn", Pins("BL10")),
        Subsignal("rxp", Pins("BN1")),
        Subsignal("rxn", Pins("BN3")),
    ),
    ("sfp_tx", 0,
        Subsignal("p", Pins("BL7")),
        Subsignal("n", Pins("BL10")),
    ),
    ("sfp_rx", 0,
        Subsignal("p", Pins("BN1")),
        Subsignal("n", Pins("BN3")),
    ),
    ("sfp_ctl", 0,
        Subsignal("rs0",            Pins("BE21")),
        Subsignal("rs1",            Pins("BE43")),
        Subsignal("tx_disable",     Pins("BF40")),
        Subsignal("rx_los",         Pins("BE29")),
        Subsignal("tx_fault",       Pins("BE25")),
        Subsignal("prsnt_n",        Pins("BF32")),
        Subsignal("scl",            Pins("BM19")),
        Subsignal("sda",            Pins("BU19")),
        Subsignal("link_act_led_n", Pins("BR19")),
        IOStandard("3.3-V LVCMOS"),
    ),
    ("sfp_tx_disable", 0, Pins("BF40"), IOStandard("3.3-V LVCMOS")),

    ("sfp", 1,
        Subsignal("txp", Pins("BG7")),
        Subsignal("txn", Pins("BG10")),
        Subsignal("rxp", Pins("BJ1")),
        Subsignal("rxn", Pins("BJ3")),
    ),
    ("sfp_tx", 1,
        Subsignal("p", Pins("BG7")),
        Subsignal("n", Pins("BG10")),
    ),
    ("sfp_rx", 1,
        Subsignal("p", Pins("BJ1")),
        Subsignal("n", Pins("BJ3")),
    ),
    ("sfp_ctl", 1,
        Subsignal("rs0",            Pins("BF36")),
        Subsignal("rs1",            Pins("BF29")),
        Subsignal("tx_disable",     Pins("BF25")),
        Subsignal("rx_los",         Pins("BF16")),
        Subsignal("tx_fault",       Pins("BH19")),
        Subsignal("prsnt_n",        Pins("BK22")),
        Subsignal("link_act_led_n", Pins("CK2")),
        IOStandard("3.3-V LVCMOS"),
    ),
    ("sfp_tx_disable", 1, Pins("BF25"), IOStandard("3.3-V LVCMOS")),

    # QSFP+.
    ("qsfp", 0,
        Subsignal("clk_p", Pins("BB120")),
        Subsignal("clk_n", Pins("BB115")),
        Subsignal("rx_p",  Pins("BV135 BN135 BJ135 BF135")),
        Subsignal("rx_n",  Pins("BV133 BN133 BJ133 BF133")),
        Subsignal("tx_p",  Pins("BY129 BT129 BL129 BG129")),
        Subsignal("tx_n",  Pins("BY126 BT126 BL126 BG126")),
    ),
    ("qsfp_ctl", 0,
        Subsignal("sel_n",          Pins("BH109")),
        Subsignal("reset_n",        Pins("BE115")),
        Subsignal("modprs_n",       Pins("BF115")),
        Subsignal("lpmode",         Pins("BF107")),
        Subsignal("int_n",          Pins("BH118")),
        IOStandard("3.3-V LVCMOS"),
    ),

    ("qsfp", 1,
        Subsignal("clk_p", Pins("AV120")),
        Subsignal("clk_n", Pins("AV115")),
        Subsignal("rx_p",  Pins("BD135 BB135 AY135 AV135")),
        Subsignal("rx_n",  Pins("BD133 BB133 AY133 AV133")),
        Subsignal("tx_p",  Pins("BE129 BC129 BA129 AW129")),
        Subsignal("tx_n",  Pins("BE126 BC126 BA126 AW126")),
    ),
    ("qsfp_ctl", 1,
        Subsignal("sel_n",          Pins("BU109")),
        Subsignal("reset_n",        Pins("BF104")),
        Subsignal("modprs_n",       Pins("BR109")),
        Subsignal("lpmode",         Pins("BE107")),
        Subsignal("int_n",          Pins("BH118")),
        IOStandard("3.3-V LVCMOS"),
    ),

    # SMA transceiver connectors.
    ("sma_refclk", 0,
        Subsignal("p", Pins("BB16")),
        Subsignal("n", Pins("BB21")),
    ),
    ("sma_rx", 0,
        Subsignal("p", Pins("CB1")),
        Subsignal("n", Pins("CB3")),
    ),
    ("sma_tx", 0,
        Subsignal("p", Pins("BY7")),
        Subsignal("n", Pins("BY10")),
    ),
    ("sma_rx", 1,
        Subsignal("p", Pins("BV1")),
        Subsignal("n", Pins("BV3")),
    ),
    ("sma_tx", 1,
        Subsignal("p", Pins("BT7")),
        Subsignal("n", Pins("BT10")),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    # 2x5 expansion header (J9). Pin 0/9 are VCC/GND placeholders.
    ("j9", " --- BU31 BU28 BM28 BP31 BF21 BR28 BM31 BR31 ---"),

    ("FMC", {
        # A
        "DP1_M2C_P"       : "AT1",
        "DP1_M2C_N"       : "AT3",
        "DP2_M2C_P"       : "AP1",
        "DP2_M2C_N"       : "AP3",
        "DP3_M2C_P"       : "AM1",
        "DP3_M2C_N"       : "AM3",
        "DP4_M2C_P"       : "BF1",
        "DP4_M2C_N"       : "BF3",
        "DP5_M2C_P"       : "BD1",
        "DP5_M2C_N"       : "BD3",
        "DP1_C2M_P"       : "AR7",
        "DP1_C2M_N"       : "AR10",
        "DP2_C2M_P"       : "AN7",
        "DP2_C2M_N"       : "AN10",
        "DP3_C2M_P"       : "AL7",
        "DP3_C2M_N"       : "AL10",
        "DP4_C2M_P"       : "BE7",
        "DP4_C2M_N"       : "BE10",
        "DP5_C2M_P"       : "BC7",
        "DP5_C2M_N"       : "BC10",

        # B
        "DP7_M2C_P"       : "AY1",
        "DP7_M2C_N"       : "AY3",
        "DP6_M2C_P"       : "BB1",
        "DP6_M2C_N"       : "BB3",
        "GBTCLK1_M2C_C_P" : "AV16",
        "GBTCLK1_M2C_C_N" : "AV21",
        "DP7_C2M_P"       : "AW7",
        "DP7_C2M_N"       : "AW10",
        "DP6_C2M_P"       : "BA7",
        "DP6_C2M_N"       : "BA10",

        # C
        "DP0_C2M_P"       : "AU7",
        "DP0_C2M_N"       : "AU10",
        "DP0_M2C_P"       : "AV1",
        "DP0_M2C_N"       : "AV3",
        "LA06_P"          : "D44",
        "LA06_N"          : "F44",
        "LA10_P"          : "M58",
        "LA10_N"          : "K58",
        "LA14_P"          : "K44",
        "LA14_N"          : "M44",
        "LA18_CC_P"       : "AG57",
        "LA18_CC_N"       : "AG53",
        "LA27_P"          : "V77",
        "LA27_N"          : "T77",

        # D
        "GBTCLK0_M2C_C_P" : "AP16",
        "GBTCLK0_M2C_C_N" : "AP21",
        "LA01_CC_P"       : "B45",
        "LA01_CC_N"       : "A48",
        "LA05_P"          : "B56",
        "LA05_N"          : "A60",
        "LA09_P"          : "F55",
        "LA09_N"          : "D55",
        "LA13_P"          : "V47",
        "LA13_N"          : "T47",
        "LA17_CC_P"       : "AG83",
        "LA17_CC_N"       : "AC83",
        "LA23_P"          : "AG72",
        "LA23_N"          : "AG75",
        "LA26_P"          : "AC64",
        "LA26_N"          : "AG64",

        # G
        "CLK1_M2C_P"      : "P55",
        "CLK1_M2C_N"      : "T55",
        "LA00_CC_P"       : "A45",
        "LA00_CC_N"       : "B42",
        "LA03_P"          : "A54",
        "LA03_N"          : "B54",
        "LA08_P"          : "M47",
        "LA08_N"          : "K47",
        "LA12_P"          : "Y58",
        "LA12_N"          : "Y55",
        "LA16_P"          : "P44",
        "LA16_N"          : "T44",
        "LA20_P"          : "Y67",
        "LA20_N"          : "Y65",
        "LA22_P"          : "M74",
        "LA22_N"          : "K74",
        "LA25_P"          : "B66",
        "LA25_N"          : "A66",
        "LA29_P"          : "F8",
        "LA29_N"          : "H8",
        "LA31_P"          : "F4",
        "LA31_N"          : "K4",
        "LA33_P"          : "J1",
        "LA33_N"          : "G1",

        # H
        "CLK0_M2C_P"      : "Y44",
        "CLK0_M2C_N"      : "Y47",
        "LA02_P"          : "B51",
        "LA02_N"          : "A51",
        "LA04_P"          : "A63",
        "LA04_N"          : "B60",
        "LA07_P"          : "F47",
        "LA07_N"          : "H47",
        "LA11_P"          : "H58",
        "LA11_N"          : "F58",
        "LA15_P"          : "V58",
        "LA15_N"          : "T58",
        "LA19_P"          : "B85",
        "LA19_N"          : "A85",
        "LA21_P"          : "Y77",
        "LA21_N"          : "Y74",
        "LA24_P"          : "P74",
        "LA24_N"          : "T74",
        "LA28_P"          : "AC53",
        "LA28_N"          : "AC50",
        "LA30_P"          : "C2",
        "LA30_N"          : "D4",
        "LA32_P"          : "G2",
        "LA32_N"          : "J2",
    }),
]

# SDCard Adapter -----------------------------------------------------------------------------------

def sdcard_io(connector="j9"):
    return [
        # Custom SDCard/PMOD board developed for J9:
        # https://github.com/gsteiert/a5e2pmod
        ("spisdcard", 0,
            Subsignal("clk",  Pins(f"{connector}:7")),
            Subsignal("mosi", Pins(f"{connector}:3"), Misc("WEAK_PULL_UP_RESISTOR ON")),
            Subsignal("cs_n", Pins(f"{connector}:1"), Misc("WEAK_PULL_UP_RESISTOR ON")),
            Subsignal("miso", Pins(f"{connector}:5"), Misc("WEAK_PULL_UP_RESISTOR ON")),
            IOStandard("3.3-V LVCMOS"),
        ),
        ("sdcard", 0,
            Subsignal("data", Pins(f"{connector}:5 {connector}:2 {connector}:4 {connector}:1"), Misc("WEAK_PULL_UP_RESISTOR ON")),
            Subsignal("cmd",  Pins(f"{connector}:3"), Misc("WEAK_PULL_UP_RESISTOR ON")),
            Subsignal("clk",  Pins(f"{connector}:7")),
            Subsignal("cd",   Pins(f"{connector}:6"), Misc("WEAK_PULL_UP_RESISTOR ON")),
            IOStandard("3.3-V LVCMOS"),
        ),
    ]

_sdcard_io = sdcard_io()

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, variant="production", toolchain="quartus"):
        if variant not in _variants:
            raise ValueError(f"Unsupported variant {variant!r}, available: {', '.join(_variants)}")
        self.variant    = variant
        self.speedgrade = _speedgrades[variant]
        AlteraPlatform.__init__(self, _variants[variant], _io, _connectors, toolchain=toolchain)
        self.create_rbf = True
        self.create_svf = False # Not supported for Agilex 5 family.
        self.add_platform_command("set_global_assignment -name PWRMGT_VOLTAGE_OUTPUT_FORMAT \"LINEAR FORMAT\"")
        self.add_platform_command("set_global_assignment -name PWRMGT_LINEAR_FORMAT_N \"-12\"")
        self.add_platform_command("set_global_assignment -name ENABLE_INTERMEDIATE_SNAPSHOTS \"ON\"")
        self.add_platform_command("set_global_assignment -name DEVICE_INITIALIZATION_CLOCK \"OSC_CLK_1_125MHZ\"")

        # Calculate clock uncertainties.
        self.toolchain.additional_sdc_commands.append("derive_clock_uncertainty")

    def create_programmer(self, cable_name="Agilex 5E065B Premium DK"):
        return USBBlaster(cable_name=cable_name)

    def do_finalize(self, fragment):
        AlteraPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100", 0, loose=True), 1e9/100e6)
        self.add_period_constraint(self.lookup_request("clk100", 1, loose=True), 1e9/100e6)
        self.add_period_constraint(self.lookup_request("clk125", 0, loose=True), 1e9/125e6)
