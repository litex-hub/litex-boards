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
    ("clk12", 0, Pins("G15"), IOStandard("LVCMOS33")),

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
     )
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = []

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticeNexusPlatform):
    default_clk_name = "clk12"
    default_clk_period = 1e9/12e6

    def __init__(self, device="LIFCL-40-9BG400C", toolchain="radiant", **kwargs):
        # Accept "LIFCL" for backwards compatibility.
        # LIFCL just means Crosslink-NX so we can expect every
        # Crosslink-NX Evaluation Board to have a LIFCL part.
        if device == "LIFCL":
            device == "LIFCL-40-9BG400C"
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
