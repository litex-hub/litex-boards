#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 David Corrigan <davidcorrigan714@gmail.com>
# Copyright (c) 2020 Alan Green <avg@google.com>
# Copyright (c) 2020 David Shah <dave@ds0.me>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.lattice import LatticePlatform
from litex.build.lattice.programmer import LatticeProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    ("clk12", 0, Pins("L16"), IOStandard("LVCMOS33")), # Ensure JP2 is installed

    # Reference clocks. Why are there four 27MHz oscs. Is this really correct??
    ("clk27_0", 0, Pins("L5"), IOStandard("LVCMOS18")),
    ("clk27_1", 0, Pins("L7"), IOStandard("LVCMOS18")),
    ("clk27_2", 0, Pins("M2"), IOStandard("LVCMOS18")),
    ("clk27_3", 0, Pins("Y2"), IOStandard("LVCMOS18")),

    # 8.1. General Purpose Push Buttons - all logic zero when pressed]
    ("cam_reset", 0, Pins("T1"), IOStandard("LVCMOS18H"), Misc("PULLMODE=UP")),  # SW1
    ("gsrn",      0, Pins("G13"), IOStandard("LVCMOS33")),  # SW3
    ("programn",  0, Pins("E11"), IOStandard("LVCMOS33")),  # SW4
    ("user_btn",  0, Pins("L20"), IOStandard("LVCMOS33")),  # SW5
    ("user_btn",  1, Pins("L19"), IOStandard("LVCMOS33")),  # SW6

    ("serial", 0,
        Subsignal("rx", Pins("F14"), IOStandard("LVCMOS33")),
        Subsignal("tx", Pins("F16"), IOStandard("LVCMOS33")),
    ),

    # Section 7.1 Status LEDs
    ("user_led", 0, Pins("G14"), IOStandard("LVCMOS33")),  # Green
    ("user_led", 1, Pins("G15"), IOStandard("LVCMOS33")),  # Green
    ("user_led", 2, Pins("L13"), IOStandard("LVCMOS33")),  # Green
    ("user_led", 3, Pins("L14"), IOStandard("LVCMOS33")),  # Green


    # Section 8.1 DIP Switch
    ("user_dip_btn", 0, Pins("R5"), IOStandard("LVCMOS18")),
    ("user_dip_btn", 1, Pins("R6"), IOStandard("LVCMOS18")),
    ("user_dip_btn", 2, Pins("Y5"), IOStandard("LVCMOS18")),
    ("user_dip_btn", 3, Pins("W5"), IOStandard("LVCMOS18")),

    # SPI Flash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("E13")),
        Subsignal("clk",  Pins("E12")),
        Subsignal("mosi", Pins("D13")),
        Subsignal("miso", Pins("D15")),
        Subsignal("wp",   Pins("D14")),
        Subsignal("hold", Pins("D16")),
        IOStandard("LVCMOS33")
    ),

    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("E13")),
        Subsignal("clk",  Pins("E12")),
        Subsignal("dq",   Pins("D13 D15 D14 D16")),
        IOStandard("LVCMOS33")
    ),

    # Camera I2C buses
    ("i2c", 0,
        Subsignal("sda", Pins("N4")),
        Subsignal("scl", Pins("N5")),
        IOStandard("LVCMOS18")
    ),
    ("i2c", 1,
        Subsignal("sda", Pins("N6")),
        Subsignal("scl", Pins("N7")),
        IOStandard("LVCMOS18")
    ),
    ("i2c", 2,
        Subsignal("sda", Pins("P1")),
        Subsignal("scl", Pins("P2")),
        IOStandard("LVCMOS18")
    ),
    ("i2c", 3,
        Subsignal("sda", Pins("P5")),
        Subsignal("scl", Pins("P6")),
        IOStandard("LVCMOS18")
    ),

    # Shared camera control signals
    ("cam_ctrl",
        Subsignal("cam_reset", Pins("T1")),
        Subsignal("cam_frame_sync", Pins("U1")),
    ),

    # HyperRAM
    ("hyperram", 0,
        Subsignal("dq", Pins("Y6 W7 V7 P7 P8 R8 T8 Y7"), IOStandard("LVCMOS18H")),
        Subsignal("rwds", Pins("W6"), IOStandard("LVCMOS18H")),
        Subsignal("cs_n", Pins("V6"), IOStandard("LVCMOS18H")),
        Subsignal("rst_n", Pins("U7"), IOStandard("LVCMOS18H")),
        Subsignal("clk", Pins("R7"), IOStandard("LVDS")),
        # Subsignal("clk_n", Pins("T7"), IOStandard("LVDS")),
        Misc("SLEWRATE=FAST")
    ),
    ("hyperram", 1,
        Subsignal("dq", Pins("W8 V9 W9 Y9 T10 T11 U10 V10"), IOStandard("LVCMOS18H")),
        Subsignal("rwds", Pins("R10"), IOStandard("LVCMOS18H")),
        Subsignal("cs_n", Pins("P9"), IOStandard("LVCMOS18H")),
        Subsignal("rst_n", Pins("P10"), IOStandard("LVCMOS18H")),
        Subsignal("clk", Pins("W10"), IOStandard("LVDS")),
        # Subsignal("clk_n", Pins("Y10"), IOStandard("LVDS")),
        Misc("SLEWRATE=FAST")
    ),

    ("camera_mclk", 0, Pins("M3"), IOStandard("LVCMOS18")),
    ("camera_mclk", 1, Pins("M4"), IOStandard("LVCMOS18")),
    ("camera_mclk", 2, Pins("M5"), IOStandard("LVCMOS18")),
    ("camera_mclk", 3, Pins("M6"), IOStandard("LVCMOS18")),

    # MIPI camera modules
    # Note that use of MIPI_DPHY standard for + and LVCMOS12H for - is copied from Lattice PDC
    # MIPI pins are unconstrained to work around a Radiant 2.0 bug
    ("camera", 0,
        Subsignal("clkp", Pins("X")),
        Subsignal("clkn", Pins("X")),
        Subsignal("dp", Pins("X X X X")),
        Subsignal("dn", Pins("X X X X")),
    ),
    ("camera", 1,
        Subsignal("clkp", Pins("X")),
        Subsignal("clkn", Pins("X")),
        Subsignal("dp", Pins("X X X X")),
        Subsignal("dn", Pins("X X X X")),
    ),
    ("camera", 2,
        Subsignal("clkp", Pins("W11"), IOStandard("MIPI_DPHY")),
        Subsignal("clkn", Pins("Y11"), IOStandard("LVCMOS12H")),
        Subsignal("dp", Pins("V11 W13 U12 R12"), IOStandard("MIPI_DPHY")),
        Subsignal("dn", Pins("U11 V12 T12 P12"), IOStandard("LVCMOS12H")),
    ),
    ("camera", 3,
        Subsignal("clkp", Pins("T13"), IOStandard("MIPI_DPHY")),
        Subsignal("clkn", Pins("T14"), IOStandard("LVCMOS12H")),
        Subsignal("dp", Pins("Y15 U15 V17 P13"), IOStandard("MIPI_DPHY")),
        Subsignal("dn", Pins("Y16 V16 U16 R13"), IOStandard("LVCMOS12H")),
    ),
]


# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    # Link to ECP5
    ("UPSTREAM", {
        "D0": "N14",
        "D1": "M14",
        "D2": "M16",
        "D3": "M15",
        "D4": "N15",
        "D5": "N16",
        "D6": "M17",
        "D7": "M18",
        "D8": "M19",
        "D9": "M20",
        "D10": "N19",
        "D11": "N20",
        "D12": "P19",
        "D13": "P20",
        "D14": "P17",
        "D15": "P18",
        "D16": "R17",
        "D17": "R18",
        "D18": "U20",
        "D19": "T20",
        "D20": "W20",
        "D21": "V20",
        "D22": "T18",
        "D23": "U18",
        "D24": "V18",
        "D25": "V19",
        "D26": "W19",

        "PCLK_DOWN": "Y19",
        "GSRN": "G13",
        "SDA": "E20",
        "SCL": "F20",

        "UP_GPIO39": "F18",
        "UP_GPIO40": "G19",
        "UP_GPIO41": "L15",
        "UP_GPIO42": "D17",
    }
    ),
    # PMOD signal number:
    #          1   2  3  4  7  8  9   10
    ("PMOD0", "D10 D9 D7 D8 D6 D5 D4  D3"),
    ("PMOD1", "E10 E9 E7 E8 E4 E3 E2  F1"),
    ("PMOD2", "J2  J1 K2 K1 K3 K4 E17 F13"),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticePlatform):
    default_clk_name   = "clk12"
    default_clk_period = 1e9/12e6

    def __init__(self, device="LIFCL", toolchain="radiant", **kwargs):
        assert device in ["LIFCL"]
        LatticePlatform.__init__(self, device + "-40-9BG400C", _io, _connectors, toolchain=toolchain, **kwargs)

    def create_programmer(self, mode = "direct"):
        assert mode in ["direct","flash"]

        xcf_template_direct = """<?xml version='1.0' encoding='utf-8' ?>
<!DOCTYPE       ispXCF  SYSTEM  "IspXCF.dtd" >
<ispXCF version="R1.2.0">
    <Comment></Comment>
    <Chain>
        <Comm>JTAG</Comm>
        <Device>
            <SelectedProg value="TRUE"/>
            <Pos>1</Pos>
            <Vendor>Lattice</Vendor>
            <Family>LIFCL</Family>
            <Name>LIFCL-40</Name>
            <IDCode>0x010f1043</IDCode>
            <Package>All</Package>
            <PON>LIFCL-40</PON>
            <Bypass>
                <InstrLen>8</InstrLen>
                <InstrVal>11111111</InstrVal>
                <BScanLen>1</BScanLen>
                <BScanVal>0</BScanVal>
            </Bypass>
            <File>{bitstream_file}</File>
            <JedecChecksum>N/A</JedecChecksum>
            <MemoryType>Static Random Access Memory (SRAM)</MemoryType>
            <Operation>Fast Configuration</Operation>
            <Option>
                <SVFVendor>JTAG STANDARD</SVFVendor>
                <IOState>HighZ</IOState>
                <PreloadLength>362</PreloadLength>
                <IOVectorData>0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF</IOVectorData>
                <Usercode>0x00000000</Usercode>
                <AccessMode>Direct Programming</AccessMode>
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
        <TCKDelay>3</TCKDelay>
    </ProjectOptions>
    <CableOptions>
        <CableName>USB2</CableName>
        <PortAdd>FTUSB-0</PortAdd>
    </CableOptions>
</ispXCF>
"""

        xcf_template_flash = """<?xml version='1.0' encoding='utf-8' ?>
<!DOCTYPE       ispXCF  SYSTEM  "IspXCF.dtd" >
<ispXCF version="R1.2.0">
    <Comment></Comment>
    <Chain>
        <Comm>JTAG2SPI</Comm>
        <Device>
            <SelectedProg value="TRUE"/>
            <Pos>1</Pos>
            <Vendor>Lattice</Vendor>
            <Family>LIFCL</Family>
            <Name>LIFCL-40</Name>
            <Package>All</Package>
            <Bypass>
                <InstrLen>8</InstrLen>
                <InstrVal>11111111</InstrVal>
                <BScanLen>1</BScanLen>
                <BScanVal>0</BScanVal>
            </Bypass>
            <File>{bitstream_file}</File>
            <MemoryType>External SPI Flash Memory (SPI FLASH)</MemoryType>
            <Operation>Erase,Program,Verify</Operation>
            <Option>
                <SVFVendor>JTAG STANDARD</SVFVendor>
                <Usercode>0x00000000</Usercode>
                <AccessMode>Direct Programming</AccessMode>
            </Option>
            <FPGALoader>
            <CPLDDevice>
                <Device>
                    <Pos>1</Pos>
                    <Vendor>Lattice</Vendor>
                    <Family>LIFCL</Family>
                    <Name>LIFCL-40</Name>
                    <IDCode>0x010f1043</IDCode>
                    <Package>All</Package>
                    <PON>LIFCL-40</PON>
                    <Bypass>
                        <InstrLen>8</InstrLen>
                        <InstrVal>11111111</InstrVal>
                        <BScanLen>1</BScanLen>
                        <BScanVal>0</BScanVal>
                    </Bypass>
                    <MemoryType>Static Random Access Memory (SRAM)</MemoryType>
                    <Operation>Refresh Verify ID</Operation>
                    <Option>
                        <SVFVendor>JTAG STANDARD</SVFVendor>
                        <IOState>HighZ</IOState>
                        <PreloadLength>362</PreloadLength>
                        <IOVectorData>0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF</IOVectorData>
                        <AccessMode>Direct Programming</AccessMode>
                    </Option>
                </Device>
            </CPLDDevice>
            <FlashDevice>
                <Device>
                    <Pos>1</Pos>
                    <Vendor>Macronix</Vendor>
                    <Family>SPI Serial Flash</Family>
                    <Name>MX25L12833F</Name>
                    <IDCode>0x18</IDCode>
                    <Package>8-pin SOP</Package>
                    <Operation>Erase,Program,Verify</Operation>
                    <File>{bitstream_file}</File>
                    <AddressBase>0x00000000</AddressBase>
                    <EndAddress>0x000F0000</EndAddress>
                    <DeviceSize>128</DeviceSize>
                    <DataSize>1016029</DataSize>
                    <NumberOfDevices>1</NumberOfDevices>
                    <ReInitialize value="FALSE"/>
                </Device>
            </FlashDevice>
            <FPGADevice>
                <Device>
                    <Pos>1</Pos>
                    <Name></Name>
                    <File>{bitstream_file}</File>
                    <LocalChainList>
                        <LocalDevice index="-99"
                            name="Unknown"
                            file="{bitstream_file}"/>
                    </LocalChainList>
                    <Option>
                        <SVFVendor>JTAG STANDARD</SVFVendor>
                    </Option>
                </Device>
            </FPGADevice>
            </FPGALoader>
        </Device>
    </Chain>
    <ProjectOptions>
        <Program>SEQUENTIAL</Program>
        <Process>ENTIRED CHAIN</Process>
        <OperationOverride>No Override</OperationOverride>
        <StartTAP>TLR</StartTAP>
        <EndTAP>TLR</EndTAP>
        <DisableCheckBoard value="TRUE"/>
        <VerifyUsercode value="FALSE"/>
        <TCKDelay>3</TCKDelay>
    </ProjectOptions>
    <CableOptions>
        <CableName>USB2</CableName>
        <PortAdd>FTUSB-0</PortAdd>
        <USBID>Lattice ECP5 VIP Processor Board 0000 Serial FT4RXXZ5</USBID>
    </CableOptions>
</ispXCF>
"""

        if mode == "direct":
            xcf_template = xcf_template_direct
        if mode == "flash":
            xcf_template = xcf_template_flash

        return LatticeProgrammer(xcf_template)



