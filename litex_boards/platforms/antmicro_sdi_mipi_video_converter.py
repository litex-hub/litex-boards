#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023 Antmicro <www.antmicro.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.lattice import LatticeNexusPlatform
from litex.build.lattice.programmer import LatticeProgrammer
from litex.build.lattice.programmer import EcpprogProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk.
    ("clk40", 0, Pins("G15"), IOStandard("LVCMOS33")),

    # Serial.
    ("serial", 0,
        Subsignal("tx", Pins("J12"), IOStandard("LVCMOS33")),
        Subsignal("rx", Pins("J11"), IOStandard("LVCMOS33")),
     ),

    # Leds (Section 7.3).
    ("user_led", 0, Pins("E15"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("E16"), IOStandard("LVCMOS33")),

    # DIP Switches (Section 7.1).
    ("user_dip_btn", 0, Pins("F15"), IOStandard("LVCMOS33")),
    ("user_dip_btn", 1, Pins("H10"), IOStandard("LVCMOS33")),


    # SPI Flash (Section 6.3.1.).
    ("spiflash", 0,
        Subsignal("cs_n", Pins("C15")),
        Subsignal("clk",  Pins("C16")),
        Subsignal("mosi", Pins("C14")),
        Subsignal("miso", Pins("D16")),
        IOStandard("LVCMOS33")
    ),
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("C15")),
        Subsignal("clk",  Pins("C16")),
        Subsignal("dq",   Pins("C14 D16 D15 D12")),
        IOStandard("LVCMOS33")
    ),

    # I2C / Qwiic.
    ("i2c", 0,
        Subsignal("sda", Pins("G9"),  Misc("PULLMODE=UP")),
        Subsignal("scl", Pins("G10"), Misc("PULLMODE=UP")),
        IOStandard("LVCMOS33")
    ),

    # GPIO connector (J9).
    ("gpio", 0, Pins("H16 H14 H15 J15"), IOStandard("LVCMOS33")),

    # SDI deserializer.
    ("sdi", 0,
        Subsignal("pclk",       Pins("L5")),
        Subsignal("data",       Pins(
            "L1 L2 K1 K2 J1 J2 L3 H1 H4 K3",
            "H5 H2 J6 K5 D5 J5 L4 E6 K6 K4")),
        Subsignal("stat",       Pins("N2 M3 M2 N1 M1 G3")),
        Subsignal("reset_trst", Pins("D4")),
        Subsignal("cs_tms_n",   Pins("E4")),
        Subsignal("sclk_tck",   Pins("E5")),
        Subsignal("sdin_tdi",   Pins("H6")),
        Subsignal("sdout_tdo",  Pins("F4")),
        Subsignal("standby",    Pins("F6")),
        Subsignal("sw_en",      Pins("D6")),
        Subsignal("sdo_en_dis", Pins("G6")),
        Subsignal("dvb_asi",    Pins("H11")),
        IOStandard("LVCMOS33")
    ),

    # MIPI D-PHYs.
    ("mipi", 0,
        Subsignal("clkp", Pins("D1"),          IOStandard("MIPI_DPHY")),
        Subsignal("clkn", Pins("D2"),          IOStandard("LVCMOS12H")),
        Subsignal("dp",   Pins("E1 C1 F1 B1"), IOStandard("MIPI_DPHY")),
        Subsignal("dn",   Pins("E2 C2 F2 B2"), IOStandard("LVCMOS12H")),
    ),
    ("mipi", 1,
        Subsignal("clkp", Pins("A5"),          IOStandard("MIPI_DPHY")),
        Subsignal("clkn", Pins("B5"),          IOStandard("LVCMOS12H")),
        Subsignal("dp",   Pins("A4 A6 A3 A7"), IOStandard("MIPI_DPHY")),
        Subsignal("dn",   Pins("B4 B6 B3 B7"), IOStandard("LVCMOS12H")),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("ffc1", {
         1: "B2",
         2: "B1",
         3: "F2",
         4: "F1",
         5: "C2",
         6: "C1",
         7: "E2",
         8: "E1",
        10: "D2",
        11: "D1",
        19: "K7",
        20: "L6",
        21: "M7",
        22: "L7",
        23: "M4",
        24: "N4",
        25: "N3",
        26: "P3",
        28: "P2",
        29: "P1",
    }),
    ("ffc2", {
        19: "B7",
        20: "A7",
        21: "B3",
        22: "A3",
        23: "B6",
        24: "A6",
        25: "B4",
        26: "A4",
        28: "B5",
        29: "A5",
    }),
    ("gpio", {
        2: "H16",
        3: "H14",
        4: "H15",
        5: "J15",
    }),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticeNexusPlatform):
    default_clk_name = "clk40"
    default_clk_period = 1e9/40e6

    def __init__(self, device="LIFCL-40-9BG256C", toolchain="radiant", **kwargs):
        # Accept "LIFCL" for backwards compatibility.
        # LIFCL just means Crosslink-NX so we can expect every
        # Crosslink-NX Evaluation Board to have a LIFCL part.
        if device == "LIFCL":
            device = "LIFCL-40-9BG256C"
        assert device in ["LIFCL-40-9BG256C", "LIFCL-40-9BG400C", "LIFCL-40-8BG400CES", "LIFCL-40-8BG400CES2", "LIFCL-40-8BG400C"]
        LatticeNexusPlatform.__init__(self, device, _io, _connectors, toolchain=toolchain, **kwargs)

    def create_programmer(self, mode="direct", prog="radiant"):
        assert mode in ["direct", "flash"]
        assert prog in ["radiant", "ecpprog"]

        if prog == "ecpprog":
            return EcpprogProgrammer()

        xcf_template_direct = """<?xml version='1.0' encoding='utf-8' ?>
<!DOCTYPE		ispXCF	SYSTEM	"IspXCF.dtd" >
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
<!DOCTYPE		ispXCF	SYSTEM	"IspXCF.dtd" >
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
		<USBID>Lattice CrossLink-NX Eval Board A Location 0000 Serial FT4J4IK9A</USBID>
	</CableOptions>
</ispXCF>
"""

        if mode == "direct":
            xcf_template = xcf_template_direct
        if mode == "flash":
            xcf_template = xcf_template_flash

        return LatticeProgrammer(xcf_template)
