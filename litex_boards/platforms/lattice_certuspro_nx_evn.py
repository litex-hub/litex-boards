#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2024 Enjoy-Digital <enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.lattice import LatticeNexusPlatform
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # 5. CertusPro-NX Clock Sources
    ("clk125",  0, Pins("N25"), IOStandard("LVCMOS33")), # JP15: open
    ("clk12",   0, Pins("R4"),  IOStandard("LVCMOS33")), # JP6: close
    ("clkresv", 0, Pins("R6"),  IOStandard("LVCMOS33")), # DNI, JP18: open

    # Disable Clk Signals
    ("resv_clk_dis",   0, Pins("R7"),  IOStandard("LVCMOS33")),
    ("clk125_clk_dis", 0, Pins("J23"), IOStandard("LVCMOS33")),

    # 7.2. General Purpose Push Buttons - all logic zero when pressed
    ("programn", 0, Pins("G4"), IOStandard("LVCMOS18")), # SW2
    ("user_btn_n", 0, Pins("J5"), IOStandard("LVCMOS18")), # SW1
    ("user_btn_n", 1, Pins("J2"), IOStandard("LVCMOS18")), # SW4
    ("user_btn_n", 2, Pins("J3"), IOStandard("LVCMOS18")), # SW5

    # 7.1. DIP Switch
    ("user_dip_btn", 0, Pins("K8"), IOStandard("LVCMOS18")),
    ("user_dip_btn", 1, Pins("K7"), IOStandard("LVCMOS18")),
    ("user_dip_btn", 2, Pins("K6"), IOStandard("LVCMOS18")),
    ("user_dip_btn", 3, Pins("K4"), IOStandard("LVCMOS18")),
    ("user_dip_btn", 4, Pins("K3"), IOStandard("LVCMOS18")),
    ("user_dip_btn", 5, Pins("K2"), IOStandard("LVCMOS18")),
    ("user_dip_btn", 6, Pins("J7"), IOStandard("LVCMOS18")),
    ("user_dip_btn", 7, Pins("J6"), IOStandard("LVCMOS18")),

    # 6.1 UART Topology (JP1/JP2: close, JP4/JP5: open)
    ("serial", 0,
        Subsignal("rx", Pins("L2")),
        Subsignal("tx", Pins("L1")),
        IOStandard("LVCMOS33")
    ),

    # 7.3. General Purpose LEDs (Inverted)
    ("user_led",  0, Pins("N5"), IOStandard("LVCMOS33")), # Bank 1 Green
    ("user_led",  1, Pins("N6"), IOStandard("LVCMOS33")), # Bank 1 Green
    ("user_led",  2, Pins("N7"), IOStandard("LVCMOS33")), # Bank 1 Green
    ("user_led",  3, Pins("N8"), IOStandard("LVCMOS33")), # Bank 1 Green
    ("user_led",  4, Pins("L6"), IOStandard("LVCMOS33")), # Bank 1 Green
    ("user_led",  5, Pins("N9"), IOStandard("LVCMOS33")), # Bank 1 Green
    ("user_led",  6, Pins("L8"), IOStandard("LVCMOS33")), # Bank 1 Green
    ("user_led",  7, Pins("M9"), IOStandard("LVCMOS33")), # Bank 1 Green
    ("user_led",  8, Pins("N1"), IOStandard("LVCMOS33")), # Bank 1 Yellow
    ("user_led",  9, Pins("N2"), IOStandard("LVCMOS33")), # Bank 1 Yellow
    ("user_led", 10, Pins("N3"), IOStandard("LVCMOS33")), # Bank 1 Yellow
    ("user_led", 11, Pins("M1"), IOStandard("LVCMOS33")), # Bank 1 Yellow
    ("user_led", 12, Pins("M2"), IOStandard("LVCMOS33")), # Bank 1 Yellow
    ("user_led", 13, Pins("M3"), IOStandard("LVCMOS33")), # Bank 1 Yellow
    ("user_led", 14, Pins("L3"), IOStandard("LVCMOS33")), # Bank 1 Yellow
    ("user_led", 15, Pins("N4"), IOStandard("LVCMOS33")), # Bank 1 Yellow
    ("user_led", 16, Pins("T4"), IOStandard("LVCMOS33")), # Bank 1 Red
    ("user_led", 17, Pins("T5"), IOStandard("LVCMOS33")), # Bank 1 Red
    ("user_led", 18, Pins("T6"), IOStandard("LVCMOS33")), # Bank 1 Red
    ("user_led", 19, Pins("T7"), IOStandard("LVCMOS33")), # Bank 1 Red
    ("user_led", 20, Pins("U8"), IOStandard("LVCMOS33")), # Bank 1 Red
    ("user_led", 21, Pins("T8"), IOStandard("LVCMOS33")), # Bank 1 Red
    ("user_led", 22, Pins("R9"), IOStandard("LVCMOS33")), # Bank 1 Red
    ("user_led", 23, Pins("P9"), IOStandard("LVCMOS33")), # Bank 1 Red

    # 6.1 I2C Topology (connected to the FTDI with JP4/JP5
    ("i2c", 0,
        Subsignal("scl", Pins("M7")),
        Subsignal("sda", Pins("M6")),
        IOStandard("LVCMOS33"),
    ),

    # 6.3 SPI Topology
    ("spiflash", 0,
        Subsignal("cs_n", Pins("H3")),
        Subsignal("clk",  Pins("G6")),
        Subsignal("mosi", Pins("H7")),
        Subsignal("miso", Pins("H6")),
        Subsignal("wp",   Pins("K5")),
        Subsignal("hold", Pins("H4")),
        IOStandard("LVCMOS18")
    ),

    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("H3")),
        Subsignal("clk",  Pins("G6")),
        Subsignal("dq",   Pins("H7 H6 K5 H4")),
        IOStandard("LVCMOS18")
    ),

    # HyperRAM
    ("hyperram", 0,
        Subsignal("dq",    Pins("V18 W19 AB19 AB20 AB21 AB18 AA17 W18"), IOStandard("LVCMOS18H")),
        Subsignal("rwds",  Pins("V19"),  IOStandard("LVCMOS18H")),
        Subsignal("cs_n",  Pins("AA18"), IOStandard("LVCMOS18H")),
        Subsignal("rst_n", Pins("AB17"), IOStandard("LVCMOS18H")),
        Subsignal("clk",   Pins("Y19"),  IOStandard("LVDS")),
        # Subsignal("clk_n", Pins("Y18"), IOStandard("LVDS")),
        Misc("SLEWRATE=FAST")
    ),
    ("hyperram", 1,
        Subsignal("dq",    Pins("V22 AA20 V21 U21 U20 Y22 AA22 AA21"), IOStandard("LVCMOS18H")),
        Subsignal("rwds",  Pins("Y21"),  IOStandard("LVCMOS18H")),
        Subsignal("cs_n",  Pins("AA19"), IOStandard("LVCMOS18H")),
        Subsignal("rst_n", Pins("U18"),  IOStandard("LVCMOS18H")),
        Subsignal("clk",   Pins("W22"),  IOStandard("LVDS")),
        # Subsignal("clk_n", Pins("W21"), IOStandard("LVDS")),
        Misc("SLEWRATE=FAST")
    ),

    # 8.1 SMA Header.
    ("sma_rx", 0,
        Subsignal("p", Pins("B20")),
        Subsignal("n", Pins("B19")),
    ),
    ("sma_tx", 0,
        Subsignal("p", Pins("A18")),
        Subsignal("n", Pins("A17")),
    ),
    ("sma_rx", 1,
        Subsignal("p", Pins("C16")),
        Subsignal("n", Pins("B16")),
    ),
    ("sma_tx", 1,
        Subsignal("p", Pins("A15")),
        Subsignal("n", Pins("A14")),
    ),
    ("sma_rx", 2,
        Subsignal("p", Pins("B13")),
        Subsignal("n", Pins("C12")),
    ),
    ("sma_tx", 2,
        Subsignal("p", Pins("A12")),
        Subsignal("n", Pins("A11")),
    ),
    ("sma_rx", 3,
        Subsignal("p", Pins("B10")),
        Subsignal("n", Pins("C10")),
    ),
    ("sma_tx", 3,
        Subsignal("p", Pins("A9")),
        Subsignal("n", Pins("A8")),
    ),

    # 8.3 Parallel FMC Configuration Header.
    ("fmc_config", 0,
        Subsignal("fmc_tck",   Pins("H20")),
        Subsignal("pg_c2m",    Pins("J22")),
        Subsignal("pg_m2c",    Pins("J25")),
        Subsignal("fmc_tdi",   Pins("J24")),
        Subsignal("fmc_prsnt", Pins("H21")),
        Subsignal("fmc_tdo",   Pins("H26")),
        Subsignal("fmc_scl",   Pins("H22")),
        Subsignal("fmc_tms",   Pins("J26")),
        Subsignal("fmc_sda",   Pins("H23")),
        IOStandard("LVCMOS33")
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    # Table 6.2 PMOD Header
    # PMOD signal number:
    #          1    2   3   4   7   8   9   10
    ("PMOD0", "Y1   W2  V3  V1  Y2  W3  W1  V2"), # J5
    ("PMOD1", "V7   V6  V5  V4  V8  W7  W6  W5"), # J4
    ("PMOD2", "AA4 AB3 AA2 AA1  W4  Y4 AB2 AB1"), # J6

    # 8.4 Raspberry PI Board GPIO Header.
    ("RASP",
        "None",  # (no pin 0)
        "None",  #  1 3.3V
        "None",  #  2 5V
        "K26",   #  3 RASP_IO02
        "None",  #  4 5V
        "L26",   #  5 RASP_IO03
        "None",  #  6 GND
        "K25",   #  7 RASP_IO04
        "L25",   #  8 RASP_IO14
        "None",  #  9 GND
        "K24",   # 10 RASP_IO15
        "L24",   # 11 RASP_IO17
        "N26",   # 12 RASP_IO18
        "J21",   # 13 RASP_IO27
        "None",  # 14 GND
        "L23",   # 15 RASP_IO22
        "J20",   # 16 RASP_IO23
        "None",  # 17 3.3V
        "K21",   # 18 RASP_IO24
        "J19",   # 19 RASP_IO10
        "None",  # 20 GND
        "K20",   # 21 RASP_IO09
        "L22",   # 22 RASP_IO25
        "M26",   # 23 RASP_IO11
        "K19",   # 24 RASP_IO08
        "None",  # 25 GND
        "K18",   # 26 RASP_IO07
        "P20",   # 27 RASP_ID_SD
        "P19",   # 28 RASP_ID_SC
        "L20",   # 29 RASP_IO05
        "None",  # 30 GND
        "L19",   # 31 RASP_IO06
        "L21",   # 32 RASP_IO12
        "N23",   # 33 RASP_IO13
        "None",  # 34 GND
        "N22",   # 35 RASP_IO19
        "N19",   # 36 RASP_IO16
        "N20",   # 37 RASP_IO26
        "N21",   # 38 RASP_IO20
        "None",  # 39 GND
        "P18",   # 40 RASP_IO21
    ),

    # 8.2 FMC Connector.
    ("FMC", {
        "DP1_M2C_P"     : "E24",  # A2
        "DP1_M2C_N"     : "D25",  # A3
        "DP2_M2C_P"     : "C24",  # A6
        "DP2_M2C_N"     : "B23",  # A7
        "DP3_M2C_P"     : "C21",  # A10
        "DP3_M2C_N"     : "C22",  # A11
        "DP1_C2M_P"     : "C26",  # A22
        "DP1_C2M_N"     : "B26",  # A23
        "DP2_C2M_P"     : "A25",  # A26
        "DP2_C2M_N"     : "A24",  # A27
        "DP3_C2M_P"     : "A22",  # A30
        "DP3_C2M_N"     : "A21",  # A31
        "RES1"          : "R5",   # B1
        "GBTCLK1_M2C_P" : "E10",  # B20
        "GBTCLK1_M2C_N" : "D9",   # B21
        "RES0"          : "P8",   # B40
        "DP0_C2M_P"     : "F26",  # C2
        "DP0_C2M_N"     : "E26",  # C3
        "DP0_M2C_P"     : "G24",  # C6
        "DP0_M2C_N"     : "G25",  # C7
        "LA06_P"        : "AD5",  # C10
        "LA06_N"        : "AE5",  # C11
        "LA10_P"        : "AA7",  # C14
        "LA10_N"        : "Y7",   # C15
        "LA14_P"        : "AA12", # C18
        "LA14_N"        : "AB12", # C19
        "LA18_CC_P"     : "AD25", # C22
        "LA18_CC_N"     : "AE25", # C23
        "LA27_P"        : "W11",  # C26
        "LA27_N"        : "W10",  # C27
        "FMC_SCL"       : "H22",  # C30
        "FMC_SDA"       : "H23",  # C31
        "PG_C2M"        : "J22",  # D1
        "GBTCLK0_M2C_P" : "D11",  # D4
        "GBTCLK0_M2C_N" : "E11",  # D5
        "LA01_CC_P"     : "Y5",   # D8
        "LA01_CC_N"     : "AA5",  # D9
        "LA05_P"        : "AF6",  # D11
        "LA05_N"        : "AF5",  # D12
        "LA09_P"        : "AD6",  # D14
        "LA09_N"        : "AE6",  # D15
        "LA13_P"        : "Y11",  # D17
        "LA13_N"        : "AA11", # D18
        "LA17_CC_P"     : "AB4",  # D20
        "LA17_CC_N"     : "AC4",  # D21
        "LA23_P"        : "Y10",  # D23
        "LA23_N"        : "AA10", # D24
        "LA26_P"        : "AB23", # D26
        "LA26_N"        : "AB24", # D27
        "FMC_TCK"       : "H20",  # D29
        "FMC_TDI"       : "J24",  # D30
        "FMC_TDO"       : "H26",  # D31
        "FMC_TMS"       : "J26",  # D33
        "HA01_CC_P"     : "AA13", # E2
        "HA01_CC_N"     : "AB13", # E3
        "HA05_P"        : "AD14", # E6
        "HA05_N"        : "AE14", # E7
        "HA09_P"        : "Y14",  # E9
        "HA09_N"        : "AA14", # E10
        "HA13_P"        : "W13",  # E12
        "HA13_N"        : "Y13",  # E13
        "HA16_P"        : "AE22", # E15
        "HA16_N"        : "AE23", # E16
        "HA20_P"        : "AC13", # E18
        "HA20_N"        : "AD13", # E19
        "PG_M2C"        : "J25",  # F1
        "HA00_CC_P"     : "AE13", # F4
        "HA00_CC_N"     : "AE12", # F5
        "HA04_P"        : "AF15", # F7
        "HA04_N"        : "AF16", # F8
        "HA08_P"        : "W15",  # F10
        "HA08_N"        : "W14",  # F11
        "HA12_P"        : "AF21", # F13
        "HA12_N"        : "AF20", # F14
        "HA15_P"        : "AD20", # F16
        "HA15_N"        : "AC19", # F17
        "HA19_P"        : "Y18",  # F19
        "HA19_N"        : "AA18", # F20
        "CLK1_M2C_P"    : "AB19", # G2
        "CLK1_M2C_N"    : "AB18", # G3
        "LA00_CC_P"     : "AC12", # G6
        "LA00_CC_N"     : "AD12", # G7
        "LA03_P"        : "AD4",  # G9
        "LA03_N"        : "AE4",  # G10
        "LA08_P"        : "Y6",   # G12
        "LA08_N"        : "AA6",  # G13
        "LA12_P"        : "AD10", # G15
        "LA12_N"        : "AE10", # G16
        "LA16_P"        : "AF12", # G18
        "LA16_N"        : "AF11", # G19
        "LA20_P"        : "AB9",  # G21
        "LA20_N"        : "AC9",  # G22
        "LA22_P"        : "AB22", # G24
        "LA22_N"        : "AA22", # G25
        "LA25_P"        : "AE24", # G27
        "LA25_N"        : "AF24", # G28
        "LA29_P"        : "AB25", # G30
        "LA29_N"        : "AC24", # G31
        "LA31_P"        : "AC26", # G33
        "LA31_N"        : "AB26", # G34
        "LA33_P"        : "W22",  # G36
        "LA33_N"        : "W21",  # G37
        "PRSNT_M2C_L"   : "H21",  # H2
        "CLK0_M2C_P"    : "AD21", # H4
        "CLK0_M2C_N"    : "AE21", # H5
        "LA02_P"        : "AF4",  # H7
        "LA02_N"        : "AF3",  # H8
        "LA04_P"        : "AB6",  # H10
        "LA04_N"        : "AC6",  # H11
        "LA07_P"        : "AC7",  # H13
        "LA07_N"        : "AB7",  # H14
        "LA11_P"        : "AF10", # H16
        "LA11_N"        : "AF9",  # H17
        "LA15_P"        : "AD11", # H19
        "LA15_N"        : "AE11", # H20
        "LA19_P"        : "AD9",  # H22
        "LA19_N"        : "AE9",  # H23
        "LA21_P"        : "AC22", # H25
        "LA21_N"        : "AD23", # H26
        "LA24_P"        : "AE26", # H28
        "LA24_N"        : "AF25", # H29
        "LA28_P"        : "AC25", # H31
        "LA28_N"        : "AD26", # H32
        "LA30_P"        : "AA23", # H34
        "LA30_N"        : "AA24", # H35
        "LA32_P"        : "W25",  # H37
        "LA32_N"        : "W26",  # H38
        "CLK3_M2C_P"    : "AC21", # J2
        "CLK3_M2C_N"    : "AD22", # J3
        "HA03_P"        : "AF14", # J6
        "HA03_N"        : "AF13", # J7
        "HA07_P"        : "AB15", # J9
        "HA07_N"        : "AC15", # J10
        "HA11_P"        : "AF19", # J12
        "HA11_N"        : "AE19", # J13
        "HA14_P"        : "Y16",  # J15
        "HA14_N"        : "W16",  # J16
        "HA18_P"        : "AA17", # J18
        "HA18_N"        : "Y17",  # J19
        "HA22_P"        : "V24",  # J21
        "HA22_N"        : "V25",  # J22
        "CLK2_M2C_P"    : "AB11", # K4
        "CLK2_M2C_N"    : "AC11", # K5
        "HA02_P"        : "AD15", # K7
        "HA02_N"        : "AE15", # K8
        "HA06_P"        : "AC18", # K10
        "HA06_N"        : "AD18", # K11
        "HA10_P"        : "AF22", # K13
        "HA10_N"        : "AF23", # K14
        "HA17_CC_P"     : "W24",  # K16
        "HA17_CC_N"     : "W23",  # K17
        "HA21_P"        : "W17",  # K19
        "HA21_N"        : "W18",  # K20
        "HA23_P"        : "U26",  # K22
        "HA23_N"        : "V26",  # K23
    }),

    # TODO: TP headers
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticeNexusPlatform):
    default_clk_name   = "clk125"
    default_clk_period = 1e9/125e6

    def __init__(self, device="LFCPNX", toolchain="radiant", **kwargs):
        assert device in ["LFCPNX"]
        LatticeNexusPlatform.__init__(self, device + "-100-9LFG672C", _io, _connectors, toolchain=toolchain, **kwargs)
        # SPI Pins may be used as General IO Pins (see FPGA-AN-02048 4.1.7)
        self.add_platform_command("ldc_set_sysconfig {{MASTER_SPI_PORT=DISABLE}}")
        # Evaluation mode (with free license)
        self.toolchain.set_prj_strategy_opts({"bit_ip_eval": "true"})

    def create_programmer(self):
        return OpenFPGALoader()

    def do_finalize(self, fragment):
        LatticeNexusPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk125", loose=True), 1e9/125e6)
