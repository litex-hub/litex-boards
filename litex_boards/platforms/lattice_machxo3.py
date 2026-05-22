#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2016-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.lattice import LatticePlatform
from litex.build.lattice.programmer import LatticeProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk12", 0, Pins("C8"), IOStandard("LVCMOS33")),
    ("rst_n", 0, Pins("B3"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("H11"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("J13"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("J11"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("L12"), IOStandard("LVCMOS33")),
    ("user_led", 4, Pins("K11"), IOStandard("LVCMOS33")),
    ("user_led", 5, Pins("L13"), IOStandard("LVCMOS33")),
    ("user_led", 6, Pins("N15"), IOStandard("LVCMOS33")),
    ("user_led", 7, Pins("P16"), IOStandard("LVCMOS33")),

    # Switches
    ("user_dip_btn", 0, Pins("N2"), IOStandard("LVCMOS33")),
    ("user_dip_btn", 1, Pins("P1"), IOStandard("LVCMOS33")),
    ("user_dip_btn", 2, Pins("M3"), IOStandard("LVCMOS33")),
    ("user_dip_btn", 3, Pins("N1"), IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("C11"), IOStandard("LVCMOS33")),
        Subsignal("rx", Pins("A11"), IOStandard("LVCMOS33")),
        Subsignal("rts", Pins("F10"), IOStandard("LVCMOS33")),
        Subsignal("cts", Pins("D11"), IOStandard("LVCMOS33")),
        Subsignal("dtr", Pins("B11"), IOStandard("LVCMOS33")),
        Subsignal("dsr", Pins("A12"), IOStandard("LVCMOS33")),
        Subsignal("dcd", Pins("B13"), IOStandard("LVCMOS33")),
        Subsignal("ri",  Pins("A14"), IOStandard("LVCMOS33")),
    ),

    # SPI Flash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("R5")),
        Subsignal("clk",  Pins("P6")),
        Subsignal("mosi", Pins("T13")),
        Subsignal("miso", Pins("T6")),
        IOStandard("LVCMOS33"),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("J3",
        "- - A13 C13 F8 B12 C12 E11 E10 D10 "
        "- - F9 C10 E8 E9 E7 D8 D7 C7 "
        "- - C5 D6 E6 C4 A10 F7 D9 B9 "
        "- - B6 B7 B5 A5 B4 A4 - A3"
    ),
    ("J4",
        "- - K12 K13 M14 N14 L14 N16 M15 M16 "
        "- - L15 L16 K14 K16 K15 J14 H14 J15 "
        "- - J16 H15 H16 G15 G16 F15 F16 E15 "
        "- - E16 E14 D16 C15 D14 F14 G14 B16"
    ),
    ("J6",
        "- - T12 T14 R11 R13 T11 M11 P11 N10 "
        "- - T10 P10 R9 R10 T9 N9 P9 M8 "
        "- - T8 L8 P8 M6 R7 R8 P7 T7 "
        "- - L7 R6 N6 T5 R4 P4 T3 T4"
    ),
    ("J8",
        "- - H6 N3 M2 M1 L2 L1 L3 L5 "
        "- - K4 J1 K1 J2 J3 H3 H2 H1 "
        "- - G2 G1 F2 F1 E2 E1 D2 D1 "
        "- C2 C1 G3 B1 D3 E3 F3 F5 -"
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticePlatform):
    default_clk_name   = "clk12"
    default_clk_period = 1e9/12e6

    def __init__(self, toolchain="diamond"):
        LatticePlatform.__init__(self, "LCMXO3L-6900C-5BG256C", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        _xcf_template = """
<?xml version='1.0' encoding='utf-8' ?>
<!DOCTYPE       ispXCF  SYSTEM  "IspXCF.dtd" >
<ispXCF version="3.6.0">
    <Comment></Comment>
    <Chain>
        <Comm>JTAG</Comm>
        <Device>
            <SelectedProg value="TRUE"/>
            <Pos>1</Pos>
            <Vendor>Lattice</Vendor>
            <Family>MachXO3L</Family>
            <Name>LCMXO3L-6900C</Name>
            <IDCode>0x412bd043</IDCode>
            <Package>All</Package>
            <PON>LCMXO3L-6900C</PON>
            <Bypass>
                <InstrLen>8</InstrLen>
                <InstrVal>11111111</InstrVal>
                <BScanLen>1</BScanLen>
                <BScanVal>0</BScanVal>
            </Bypass>
            <File>{bitstream_file}</File>
            <JedecChecksum>N/A</JedecChecksum>
            <Operation>SRAM Fast Configuration</Operation>
            <Option>
                <SVFVendor>JTAG STANDARD</SVFVendor>
                <IOState>HighZ</IOState>
                <PreloadLength>664</PreloadLength>
                <IOVectorData>0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF</IOVectorData>
                <Usercode>0x00000000</Usercode>
                <AccessMode>SRAM</AccessMode>
            </Option>
        </Device>
    </Chain>
    <ProjectOptions>
        <Program>SEQUENTIAL</Program>
        <Process>ENTIRED CHAIN</Process>
        <OperationOverride>No Override</OperationOverride>
        <StartTAP>TLR</StartTAP>
        <EndTAP>TLR</EndTAP>
        <VerifyUsercode value="FALSE"/>
    </ProjectOptions>
    <CableOptions>
        <CableName>USB2</CableName>
        <PortAdd>FTUSB-0</PortAdd>
        <USBID>Lattice XO3L Starter Kit A Location 0000 Serial A</USBID>
    </CableOptions>
</ispXCF>
"""
        return LatticeProgrammer(_xcf_template)

    def do_finalize(self, fragment):
        LatticePlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk12", loose=True), 1e9/12e6)
