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

]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    # 8.5 PMOD Header
    # PMOD signal number:
    #          1  2  3  4  7  8  9  10
    ("PMOD0", "T3 T2 U1 U6 V2 W1 W3 AB1"), # J64
    ("PMOD1", "T1 U2 U3 V1 V3 W2 Y1 AA1"), # J65
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
