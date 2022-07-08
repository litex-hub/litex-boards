#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 John Simons <jammsimons@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.altera.programmer import USBBlaster

# IOs ----------------------------------------------------------------------------------------------


_io = [
    # Clk / Rst
    ("clk48", 0, Pins("E2"), IOStandard("3.3-V LVTTL")),

    # SDR SDRAM
    ("sdram_clock", 0, Pins("B14"), IOStandard("3.3-V LVTTL")),
    ("sdram", 0,
        Subsignal("a", Pins(
            "A12 B12 A15 A14 D14 C14 D11 D12",
            "E11 C9 B13 E10 ")),
        Subsignal("ba",    Pins("A10 B10")),
        Subsignal("cs_n",  Pins("A11")),
        Subsignal("cke",   Pins("E9")),
        Subsignal("ras_n", Pins("D9")),
        Subsignal("cas_n", Pins("B7")),
        Subsignal("we_n",  Pins("B11")),
        Subsignal("dq", Pins(
            "A2 B4 B3 A3 A4 A5 B5 A6",
            "F8 C8 E7 E8 E6 D8 D6 B6")),
        Subsignal("dm", Pins("A7 F9")),

        Misc("FAST_OUTPUT_REGISTER ON"),

        IOStandard("3.3-V LVTTL")
    ),

    # # SPIFlash (W25Q64)
    # ("spiflash", 0,
    #     # clk
    #     Subsignal("cs_n", Pins("E2")),
    #     Subsignal("clk",  Pins("K2")),
    #     Subsignal("mosi", Pins("D1")),
    #     Subsignal("miso", Pins("E2")),
    #     IOStandard("3.3-V LVTTL"),
    # ),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("G1"),  IOStandard("3.3-V LVTTL")), # Pin D0
        Subsignal("rx", Pins("N3"), IOStandard("3.3-V LVTTL"))  # Pin D1
    ),

#     # USB FIFO
#     ("usb_fifo", 0,
#         Subsignal("dq",    Pins("AM28 AL28 AM29 AK28 AK32 AM30 AJ32 AL30"), IOStandard("LVCMOS33")),
#         Subsignal("txe_n", Pins("AM31"),  IOStandard("LVCMOS33")),
#         Subsignal("rxf_n", Pins("AJ31"),  IOStandard("LVCMOS33")),
#         Subsignal("rd_n",  Pins("AL32"),  IOStandard("LVCMOS33")),
#         Subsignal("wr_n",  Pins("AG28"),  IOStandard("LVCMOS33")),
#         Subsignal("siwu_n", Pins("AJ28"), IOStandard("LVCMOS33")),
#     ),


#     # PCIe
#     ("pcie_x1", 0,
#         Subsignal("clk_p",  Pins("AM14")),
#         Subsignal("clk_n",  Pins("AM15")),
#         Subsignal("rx_p",   Pins("AM8  AK12")),
#         Subsignal("rx_n",   Pins("AM9  AK13")),
#         Subsignal("tx_p",   Pins("AK9  AM11")),
#         Subsignal("tx_n",   Pins("AK10 AM12")),
#         Subsignal("perst",  Pins("D22"), IOStandard("LVCMOS33")),
#         Subsignal("wake_n", Pins("A23"), IOStandard("LVCMOS33")),
#     ),


#    # SPIFlash
#     ("spiflash", 0,
#         Subsignal("clk",  Pins("AM3")),
#         Subsignal("cs_n", Pins("AJ3")),
#         Subsignal("mosi", Pins("AK2")),
#         Subsignal("miso", Pins("AJ2")),
#         Subsignal("wp",   Pins("AM2")),
#         Subsignal("hold", Pins("AL1")),
#         IOStandard("LVCMOS33")
#     ),
    


#     # HDMI
#     ("hdmi", 0,
#         Subsignal("tx_d_r", Pins("AS12 AE12 W8 Y8 AD11 AD10 AE11 Y5")),
#         Subsignal("tx_d_g", Pins("AF10 Y4 AE9 AB4 AE7 AF6 AF8 AF5")),
#         Subsignal("tx_d_b", Pins("AE4 AH2 AH4 AH5 AH6 AG6 AF9 AE8")),
#         Subsignal("tx_clk", Pins("AG5")),
#         Subsignal("tx_de",  Pins("AD19")),
#         Subsignal("tx_hs",  Pins("T8")),
#         Subsignal("tx_vs",  Pins("V13")),
#         Subsignal("tx_int", Pins("AF11")),
#         Misc("FAST_OUTPUT_REGISTER ON"),
#         IOStandard("3.3-V LVTTL")
#     ),

#     # I2C
#     ("i2c", 0,
#         Subsignal("scl",    Pins("U10")),
#         Subsignal("sda",    Pins("AA4")),
#         IOStandard("3.3-V LVTTL")
#     ),


'''

# SAM D21 PINS
set_location_assignment PIN_B1  -to bMKR_AREF
set_location_assignment PIN_C2  -to bMKR_A[0]
set_location_assignment PIN_C3  -to bMKR_A[1]
set_location_assignment PIN_C6  -to bMKR_A[2]
set_location_assignment PIN_D1  -to bMKR_A[3]
set_location_assignment PIN_D3  -to bMKR_A[4]
set_location_assignment PIN_F3  -to bMKR_A[5]
set_location_assignment PIN_G2  -to bMKR_A[6]

set_location_assignment PIN_G1  -to bMKR_D[0]
set_location_assignment PIN_N3  -to bMKR_D[1]
set_location_assignment PIN_P3  -to bMKR_D[2]
set_location_assignment PIN_R3  -to bMKR_D[3]
set_location_assignment PIN_T3  -to bMKR_D[4]
set_location_assignment PIN_T2  -to bMKR_D[5]
set_location_assignment PIN_G16 -to bMKR_D[6]
set_location_assignment PIN_G15 -to bMKR_D[7]
set_location_assignment PIN_F16 -to bMKR_D[8]
set_location_assignment PIN_F15 -to bMKR_D[9]
set_location_assignment PIN_C16 -to bMKR_D[10]
set_location_assignment PIN_C15 -to bMKR_D[11]
set_location_assignment PIN_B16 -to bMKR_D[12]
set_location_assignment PIN_C11 -to bMKR_D[13]
set_location_assignment PIN_A13 -to bMKR_D[14]
  
# Mini PCIe
set_location_assignment PIN_P8  -to bPEX_PIN6
set_location_assignment PIN_L7  -to bPEX_PIN8
set_location_assignment PIN_N8  -to bPEX_PIN10
set_location_assignment PIN_T8  -to iPEX_PIN11
set_location_assignment PIN_M8  -to bPEX_PIN12
set_location_assignment PIN_R8  -to iPEX_PIN13
set_location_assignment PIN_L8  -to bPEX_PIN14
set_location_assignment PIN_M10 -to bPEX_PIN16
set_location_assignment PIN_N12 -to bPEX_PIN20
set_location_assignment PIN_T9  -to iPEX_PIN23
set_location_assignment PIN_R9  -to iPEX_PIN25
set_location_assignment PIN_T13 -to bPEX_PIN28
set_location_assignment PIN_R12 -to bPEX_PIN30
set_location_assignment PIN_A9  -to iPEX_PIN31
set_location_assignment PIN_F13  -to bPEX_PIN32
set_location_assignment PIN_B9  -to iPEX_PIN33
set_location_assignment PIN_R13 -to bPEX_PIN42
set_location_assignment PIN_P14 -to bPEX_PIN44
set_location_assignment PIN_T15 -to bPEX_PIN45
set_location_assignment PIN_R14 -to bPEX_PIN46
set_location_assignment PIN_T14 -to bPEX_PIN47
set_location_assignment PIN_F14 -to bPEX_PIN48
set_location_assignment PIN_D16 -to bPEX_PIN49
set_location_assignment PIN_D15 -to bPEX_PIN51
set_location_assignment PIN_T12 -to bPEX_RST

# HDMI output
set_instance_assignment -name IO_STANDARD LVDS -to oHDMI_TX*
set_instance_assignment -name IO_STANDARD LVDS -to oHDMI_CLK
set_location_assignment PIN_R16 -to oHDMI_TX[0]
set_location_assignment PIN_K15 -to oHDMI_TX[1]
set_location_assignment PIN_J15 -to oHDMI_TX[2]
set_location_assignment PIN_P16 -to oHDMI_TX[0](n)
set_location_assignment PIN_K16 -to oHDMI_TX[1](n)
set_location_assignment PIN_J16 -to oHDMI_TX[2](n)
set_location_assignment PIN_N15 -to oHDMI_CLK
set_location_assignment PIN_N16 -to oHDMI_CLK(n)
set_instance_assignment -name IO_STANDARD "2.5 V" -to bHDMI_SCL
set_instance_assignment -name IO_STANDARD "2.5 V" -to bHDMI_SDA
set_location_assignment PIN_K5 -to bHDMI_SCL
set_location_assignment PIN_L4 -to bHDMI_SDA
set_location_assignment PIN_M16 -to iHDMI_HPD

# MIPI input
set_instance_assignment -name FAST_INPUT_REGISTER ON -to iMIPI_D*
set_instance_assignment -name IO_STANDARD LVDS -to iMIPI_D*
set_instance_assignment -name IO_STANDARD LVDS -to iMIPI_CLK*
set_location_assignment PIN_L2  -to iMIPI_D[0]
set_location_assignment PIN_J2  -to iMIPI_D[1]
set_location_assignment PIN_L1  -to iMIPI_D[0](n)
set_location_assignment PIN_J1  -to iMIPI_D[1](n)
set_location_assignment PIN_M2  -to iMIPI_CLK
set_location_assignment PIN_M1  -to iMIPI_CLK(n)
set_location_assignment PIN_P2  -to bMIPI_SDA
set_instance_assignment -name IO_STANDARD "2.5 V" -to bMIPI_SDA
set_location_assignment PIN_P1  -to bMIPI_SCL
set_instance_assignment -name IO_STANDARD "2.5 V" -to bMIPI_SCL
set_location_assignment PIN_M7  -to bMIPI_GP[0]
set_location_assignment PIN_P9  -to bMIPI_GP[1]

# misc pins
set_instance_assignment -name IO_STANDARD "2.5 V" -to panel_en
set_location_assignment PIN_L4  -to panel_en

# Flash interface
set_location_assignment PIN_C1  -to oFLASH_MOSI
set_location_assignment PIN_H2  -to iFLASH_MISO
set_location_assignment PIN_H1  -to oFLASH_SCK
set_location_assignment PIN_D2  -to oFLASH_CS
set_location_assignment PIN_R7 -to oFLASH_HOLD
set_location_assignment PIN_T7 -to oFLASH_WP

# interrupt pins
set_location_assignment PIN_N2 -to oSAM_INT
set_location_assignment PIN_L16 -to iSAM_INT
set_instance_assignment -name IO_STANDARD "2.5 V" -to oSAM_INT
set_instance_assignment -name IO_STANDARD "3.3-V LVCMOS" -to iSAM_INT
'''

]

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name   = "clk48"
    default_clk_period = 1e9/48e6

    def __init__(self):
        AlteraPlatform.__init__(self, "10CL016YU256C8G", _io)

    def create_programmer(self):
        return USBBlaster(cable_name="Arduino MKR Vidor 4000") #  [3-2]

    def do_finalize(self, fragment):
        AlteraPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk48", loose=True), 1e9/48e6)
        # Generate PLL clock in STA
        self.toolchain.additional_sdc_commands.append("derive_pll_clocks")
        # Calculates clock uncertainties
        self.toolchain.additional_sdc_commands.append("derive_clock_uncertainty")
