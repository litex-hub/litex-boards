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
    # 4. CertusPro-NX Clock Sources.
    ("clk161_1", 0,
        Subsignal("p", Pins("C14"), IOStandard("LVDS")), # F_SFP_161.1328Mhz_CLK_P
        Subsignal("n", Pins("D13"), IOStandard("LVDS")), # F_SFP_161.1328Mhz_CLK_N
    ),
    ("clkin125", 0,    Pins("P24"), IOStandard("LVCMOS33")), # F_CLKIN_125Mhz / BANK6
    ("clk125", 0,
        Subsignal("p", Pins("W24"), IOStandard("LVDS")), # F_125Mhz_P
        Subsignal("n", Pins("W23"), IOStandard("LVDS")), # F_125Mhz_N
    ),
    ("clk100", 0,
        Subsignal("p", Pins("AB19"), IOStandard("LVDS")), # F_DDR_100Mhz_P
        Subsignal("n", Pins("AB18"), IOStandard("LVDS")), # F_DDR_100Mhz_N
    ),

    # 7.2. General Purpose Push Buttons - all logic zero when pressed.
    ("programn", 0, Pins("G4"),  IOStandard("LVCMOS33")),  # SW2
    ("gsrn",     0, Pins("N9"),  IOStandard("LVCMOS33")),  # SW3
    ("user_btn", 0, Pins("H21"), IOStandard("LVCMOS33")),  # SW7

    # 7.1. DIP Switch.
    ("user_dip_btn", 0, Pins("AA23"), IOStandard("LVCMOS33")),
    ("user_dip_btn", 1, Pins("AB22"), IOStandard("LVCMOS33")),
    ("user_dip_btn", 2, Pins("AC22"), IOStandard("LVCMOS33")),
    ("user_dip_btn", 3, Pins("AA22"), IOStandard("LVCMOS33")),
    ("user_dip_btn", 4, Pins("W21"),  IOStandard("LVCMOS33")),

    # 6.2 UART Topology (FTDI with J32&J33).
    ("serial", 0,
        Subsignal("rx", Pins("L8"), IOStandard("LVCMOS33")),
        Subsignal("tx", Pins("M9"), IOStandard("LVCMOS33")),
    ),

    # 7.3. General Purpose LEDs (Inverted).
    ("user_led", 0, Pins("R5"), IOStandard("LVCMOS33")),  # Bank 1 Green
    ("user_led", 1, Pins("R4"), IOStandard("LVCMOS33")),  # Bank 1 Green
    ("user_led", 2, Pins("R8"), IOStandard("LVCMOS33")),  # Bank 1 Green
    ("user_led", 3, Pins("R9"), IOStandard("LVCMOS33")),  # Bank 1 Green
    ("user_led", 4, Pins("U8"), IOStandard("LVCMOS33")),  # Bank 1 Green
    ("user_led", 5, Pins("R7"), IOStandard("LVCMOS33")),  # Bank 1 Green
    ("user_led", 6, Pins("R6"), IOStandard("LVCMOS33")),  # Bank 1 Green
    ("user_led", 7, Pins("P8"), IOStandard("LVCMOS33")),  # Bank 1 Green

    # 7.4. 7-Segment LED.
    ("seven_seg", 0, Pins("M4 M3 M2 M1 N1 N2 N3 N4"), IOStandard("LVCMOS33")),
    ("seven_seg_ctrl_n", 0, Pins("AC21 W22 AE26"), IOStandard("LVCMOS33")),

    # 6.1. I2C Topology (FTDI with J32&J33).
    ("i2c", 0,
        Subsignal("scl",  Pins("M7")),
        Subsignal("sda",  Pins("M6")),
    ),

    # 6.3. SPI Topology.
    ("spiflash", 0,
        Subsignal("cs_n", Pins("H3")),
        Subsignal("clk",  Pins("G6")),
        Subsignal("mosi", Pins("H7")),
        Subsignal("miso", Pins("H6")),
        Subsignal("wp",   Pins("K5")),
        Subsignal("hold", Pins("H4")),
        IOStandard("LVCMOS33")
    ),

    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("H3")),
        Subsignal("clk",  Pins("G6")),
        Subsignal("dq",   Pins("H7 H6 K5 H4")),
        IOStandard("LVCMOS33")
    ),

    # 8.1 SMA Connectors.
    ("sma_tx", 0,
        Subsignal("p", Pins("A18")), # J6
        Subsignal("n", Pins("A17")), # J3
    ),
    ("sma_tx", 1,
        Subsignal("p", Pins("A15")), # J11
        Subsignal("n", Pins("A14")), # J9
    ),
    ("sma_rx", 0,
        Subsignal("p", Pins("C16")), # J8
        Subsignal("n", Pins("B16")), # J10
    ),
    ("sma_rx", 1,
        Subsignal("p", Pins("B20")), # J2
        Subsignal("n", Pins("B19")), # J5
    ),

    # 8.8 PCIe Edge Connector.
    ("pcie_x4", 0,
        Subsignal("clk_p",  Pins("F20")), # 100MHz ref clk.
        Subsignal("clk_n",  Pins("E20")),
        Subsignal("rx_p",   Pins("G24 E24 C24 C21")),
        Subsignal("rx_n",   Pins("G25 D25 B23 C22")),
        Subsignal("tx_p",   Pins("F26 C26 A25 A22")),
        Subsignal("tx_n",   Pins("E26 B26 A24 A21")),
        Subsignal("perst",  Pins("R26"), IOStandard("LVCMOS33")),
        Subsignal("refret", Pins("E22 G21 E19 D18")), # serdes analog reference return for PMA PLL
        Subsignal("rext",   Pins("E21 G20 D19 C18")), # serdes external resistor for calibration
    ),
    ("pcie_ctrl", 0,
        Subsignal("sw_sel",  Pins("AF25")),
        Subsignal("clk_sel", Pins("AB25")),
        Subsignal("sw1_pd",  Pins("T6")),
        Subsignal("sw2_pd",  Pins("T5")),
    ),

    # 8.7 SFP Connectors.
    ("sfp", 0, # J12, 10Gbe Ethernet 1.
        Subsignal("txp", Pins("A12")),
        Subsignal("txn", Pins("A11")),
        Subsignal("rxp", Pins("B13")),
        Subsignal("rxn", Pins("C12")),
    ),
    ("sfp", 1, # J13, 10Gbe Ethernet 2.
        Subsignal("txp", Pins("A9")),
        Subsignal("txn", Pins("A8")),
        Subsignal("rxp", Pins("B10")),
        Subsignal("rxn", Pins("C10")),
    ),
    ("sfp", 2, # J15, SGMII Ethernet 1.
        Subsignal("txp", Pins("U26")),
        Subsignal("txn", Pins("V26")),
        Subsignal("rxp", Pins("V24")),
        Subsignal("rxn", Pins("V25")),
    ),
    ("sfp", 3, # J16, SGMII Ethernet 2.
        Subsignal("txp", Pins("W25")),
        Subsignal("txn", Pins("W26")),
        Subsignal("rxp", Pins("V23")),
        Subsignal("rxn", Pins("V22")),
    ),

]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    # 8.5 PMOD Header
    # PMOD signal number:
    #          1  2  3  4  7  8  9  10
    ("PMOD0", "T3 T2 U1 U6 V2 W1 W3 AB1"), # J64
    ("PMOD1", "T1 U2 U3 V1 V3 W2 Y1 AA1"), # J65

    # 8.2 Raspberry PI Board GPIO Header.
    ("RASP",
        "None",  # (no pin 0)
        "None",  #  1 3.3V
        "None",  #  2 5V
        "J22",   #  3 RASP_IO02
        "None",  #  4 5V
        "J21",   #  5 RASP_IO03
        "None",  #  6 GND
        "J20",   #  7 RASP_IO04
        "L26",   #  8 RASP_IO14
        "None",  #  9 GND
        "L25",   # 10 RASP_IO15
        "L23",   # 11 RASP_IO17
        "L22",   # 12 RASP_IO18
        "N21",   # 13 RASP_IO27
        "None",  # 14 GND
        "N26",   # 15 RASP_IO22
        "N25",   # 16 RASP_IO23
        "None",  # 17 3.3V
        "N24",   # 18 RASP_IO24
        "L21",   # 19 RASP_IO10
        "None",  # 20 GND
        "K21",   # 21 RASP_IO09
        "N23",   # 22 RASP_IO25
        "K24",   # 23 RASP_IO11
        "K19",   # 24 RASP_IO08
        "None",  # 25 GND
        "K18",   # 26 RASP_IO07
        "N19",   # 27 RASP_ID_SD
        "P18",   # 28 RASP_ID_SC
        "J19",   # 29 RASP_IO05
        "None",  # 30 GND
        "K20",   # 31 RASP_IO06
        "K25",   # 32 RASP_IO12
        "K26",   # 33 RASP_IO13
        "None",  # 34 GND
        "L20",   # 35 RASP_IO19
        "L24",   # 36 RASP_IO16
        "N22",   # 37 RASP_IO26
        "L19",   # 38 RASP_IO20
        "None",  # 39 GND
        "M26",   # 40 RASP_IO21
    ),

    # 8.10 HP_GPIO Header.
    ("HP_GPIO",
        "None",  # (no pin 0)
        "None",  #  1 GND
        "None",  #  2 GND
        "AB23",  #  3 HP_GPIO6
        "AD23",  #  4 HP_GPIO1
        "AB24",  #  5 HP_GPIO7
        "AC24",  #  6 HP_GPIO2
        "AD26",  #  7 HP_GPIO8
        "AC25",  #  8 HP_GPIO3
        "None",  #  9 NC
        "AC26",  # 10 HP_GPIO4
        "None",  # 11 NC
        "AB26",  # 12 HP_GPIO5
        "None",  # 13 VCCIO5_1V8
        "None",  # 14 VCCIO5_1V8
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticeNexusPlatform):
    default_clk_name   = "clkin125"
    default_clk_period = 1e9/125e6

    def __init__(self, device="LFCPNX", toolchain="radiant", **kwargs):
        assert device in ["LFCPNX"]
        LatticeNexusPlatform.__init__(self, device + "-100-9LFG672I", _io, _connectors, toolchain=toolchain, **kwargs)
        # SPI Pins may be used as General IO Pins (see FPGA-AN-02048 4.1.7)
        self.add_platform_command("ldc_set_sysconfig {{MASTER_SPI_PORT=DISABLE}}")
        # Evaluation mode (with free license)
        self.toolchain.set_prj_strategy_opts({"bit_ip_eval": "true"})

    def create_programmer(self):
        return OpenFPGALoader()

    def do_finalize(self, fragment):
        LatticeNexusPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clkin125", loose=True), 1e9/125e6)
