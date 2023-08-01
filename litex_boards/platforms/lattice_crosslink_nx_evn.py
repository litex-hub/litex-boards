#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 David Corrigan <davidcorrigan714@gmail.com>
# Copyright (c) 2020 Alan Green <avg@google.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.lattice import LatticeNexusPlatform
from litex.build.lattice.programmer import LatticeProgrammer
from litex.build.lattice.programmer import EcpprogProgrammer
from litex.build.lattice.programmer import OpenOCDJTAGProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Section 5.1 Clock sources
    ("clk12", 0, Pins("L13"), IOStandard("LVCMOS33")), # Ensure JP2 is installed

    # Clock signal is differential, but we only name the "p" side.
    ("clk125", 0, Pins("C12"), IOStandard("LVDS")),

    # 7.2. General Purpose Push Buttons - all logic zero when pressed
    ("gsrn",     0, Pins("G19"), IOStandard("LVCMOS33")),  # SW4
    ("programn", 0, Pins("E11"), IOStandard("LVCMOS33")),  # SW5
    ("user_btn", 0, Pins("G14"), IOStandard("LVCMOS33")),  # SW2
    ("user_btn", 1, Pins("G15"), IOStandard("LVCMOS33")),  # SW3

    # Section 6.2 UART Topology
    # Requires installation of 0-ohm jumpers R15 and R17 to properly route signals
    # Note that it is R15 and R17, not R16 and R17 as stated in the user guide
    ("serial", 0,
        Subsignal("rx", Pins("F16"), IOStandard("LVCMOS33")),
        Subsignal("tx", Pins("F18"), IOStandard("LVCMOS33")),
    ),

    # Section 7.3 General Purpose LEDs
    ("user_led", 0, Pins("E17"), IOStandard("LVCMOS33")),  # Bank 1 Green
    ("user_led", 1, Pins("F13"), IOStandard("LVCMOS33")),  # Bank 1 Green
    ("user_led", 2, Pins("G13"), IOStandard("LVCMOS33")),  # Bank 1 Green
    ("user_led", 3, Pins("F14"), IOStandard("LVCMOS33")),  # Bank 1 Green
    ("user_led", 4, Pins("L16"), IOStandard("LVCMOS33")),  # Bank 1 Green
    ("user_led", 5, Pins("L15"), IOStandard("LVCMOS33")),  # Bank 1 Green
    ("user_led", 6, Pins("L20"), IOStandard("LVCMOS33")),  # Bank 1 Green
    ("user_led", 7, Pins("L19"), IOStandard("LVCMOS33")),  # Bank 1 Green
    ("user_led", 8, Pins("R17"), IOStandard("LVCMOS33")),  # Bank 2 Green
    ("user_led", 9, Pins("R18"), IOStandard("LVCMOS33")),  # Bank 2 Green
    ("user_led", 10, Pins("U20"), IOStandard("LVCMOS33")), # Bank 2 Green
    ("user_led", 11, Pins("T20"), IOStandard("LVCMOS33")), # Bank 2 Green
    ("user_led", 12, Pins("W20"), IOStandard("LVCMOS33")), # Bank 2 Yellow
    ("user_led", 13, Pins("V20"), IOStandard("LVCMOS33")), # Bank 2 Yellow

    # Section 7.1 DIP Switch
    ("user_dip_btn", 0, Pins("N14"), IOStandard("LVCMOS33")),
    ("user_dip_btn", 1, Pins("M14"), IOStandard("LVCMOS33")),
    ("user_dip_btn", 2, Pins("M16"), IOStandard("LVCMOS33")),
    ("user_dip_btn", 3, Pins("M15"), IOStandard("LVCMOS33")),
    ("user_dip_btn", 4, Pins("N15"), IOStandard("LVCMOS33")),
    ("user_dip_btn", 5, Pins("N16"), IOStandard("LVCMOS33")),
    ("user_dip_btn", 6, Pins("M17"), IOStandard("LVCMOS33")),
    ("user_dip_btn", 7, Pins("M18"), IOStandard("LVCMOS33")),


    # Section 6.3.1. SPI Configuration
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

    # Section 8.2 Parallel FMC Configuration Connector
    ("fmc_config", 0,
        Subsignal("fmc_tck", Pins("P19")),   # 3
        Subsignal("ps_por_b", Pins("N19")),  # 4
        Subsignal("fmc_tdi", Pins("P20")),   # 7
        Subsignal("fmc_prsnt", Pins("N20")), # 8
        Subsignal("fmc_tdo", Pins("P17")),   # 9
        Subsignal("fmc_scl", Pins("M20")),   # 10
        Subsignal("fmc_tms", Pins("P18")),   # 13
        Subsignal("fmc_sda", Pins("M19")),   # 14
        IOStandard("LVCMOS33")
    ),
]


# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    #TODO ADC
    #TODO D-PHY

    # Section 8.1 FMC LPC Connector
    ("FMC", {
        "LA06_P"	: "W9",  # C10
        "LA06_N"	: "Y9",  # C11
        "LA10_P"	: "W10", # C14
        "LA10_N"	: "Y10", # C15
        "LA14_P"	: "W11", # C18
        "LA14_N"	: "Y11", # C19
        "LA18_CC_P"	: "R8",  # C22
        "LA18_CC_N"	: "T8",  # C23
        "LA27_P"	: "Y13", # C26
        "LA27_N"	: "Y14", # C27
        "LA01_CC_P"	: "W13", # D08
        "LA01_CC_N"	: "V12", # D09
        "LA05_P"	: "R5",  # D11
        "LA05_N"	: "R6",  # D12
        "LA09_P"	: "V6",  # D14
        "LA09_N"	: "U7",  # D15
        "LA13_P"	: "R9",  # D17
        "LA13_N"	: "P9",  # D18
        "LA17_P"	: "U10", # D20
        "LA17_N"	: "V10", # D21
        "LA23_P"	: "P11", # D23
        "LA23_N"	: "R11", # D24
        "LA26_P"	: "T13", # D26
        "LA26_N"	: "T14", # D27
        "CLK1_P"	: "R7",  # G02
        "CLK1_N"	: "T7",  # G03
        "LA00_CC_P"	: "V11", # G06
        "LA00_CC_N"	: "U11", # G07
        "LA03_P"	: "W6",  # G09
        "LA03_N"	: "Y6",  # G10
        "LA08_P"	: "Y7",  # G12
        "LA08_N"	: "Y8",  # G13
        "LA12_P"	: "U1",  # G15
        "LA12_N"	: "T1",  # G16
        "LA16_P"	: "P7",  # G18
        "LA16_N"	: "P8",  # G19
        "LA20_P"	: "T10", # G21
        "LA20_N"	: "T11", # G22
        "LA22_P"	: "V14", # G24
        "LA22_N"	: "U14", # G25
        "LA25_P"	: "R12", # G27
        "LA25_N"	: "P12", # G28
        "LA29_P"	: "Y15", # G30
        "LA29_N"	: "Y16", # G31
        "LA31_P"	: "Y17", # G33
        "LA31_N"	: "U16", # G34
        "VREF"	        : "T6",  # H01
        "VREFa"	        : "Y18", # H01
        "CLK0_P"	: "Y12", # H04
        "CLK0_N"	: "W12", # H05
        "LA02_P"	: "Y2",  # H07
        "LA02_N"	: "Y3",  # H08
        "LA04_P"	: "V1",  # H10
        "LA04_N"	: "W1",  # H11
        "LA07_P"	: "W7",  # H13
        "LA07_N"	: "V7",  # H14
        "LA11_P"	: "P10", # H16
        "LA11_N"	: "R10", # H17
        "LA15_P"	: "W8",  # H19
        "LA15_N"	: "V9",  # H20
        "LA19_P"	: "U12", # H22
        "LA19_N"	: "T12", # H23
        "LA21_P"	: "P13", # H25
        "LA21_N"	: "R13", # H26
        "LA24_P"	: "W14", # H28
        "LA24_N"	: "W15", # H29
        "LA28_P"	: "U15", # H31
        "LA28_N"	: "U16", # H32
        "LA30_P"	: "V17", # H34
        "LA30_N"	: "U16", # H35
    }),

    # Section 8.3 Raspberry Pi Board GPIO Header
    ("RASP",
        "None",  # (no pin 0)
        "None",  #  1 3.3V
        "None",  #  2 5V
        "L6",    #  3 RASP_IO02
        "None",  #  4 5V
        "L5",    #  5 RASP_IO03
        "None",  #  6 GND
        "M3",    #  7 RASP_IO04
        "M2",    #  8 RASP_IO14
        "None",  #  9 GND
        "L1",    # 10 RASP_IO15
        "L2",    # 11 RASP_IO17
        "R2",    # 12 RASP_IO18
        "R1",    # 13 RASP_IO27
        "None",  # 14 GND
        "P2",    # 15 RASP_IO22
        "P1",    # 16 RASP_IO23
        "None",  # 17 3.3V
        "K7",    # 18 RASP_IO24
        "N4",    # 19 RASP_IO10
        "None",  # 20 GND
        "K6",    # 21 RASP_IO09
        "K5",    # 22 RASP_IO25
        "N7",    # 23 RASP_IO11
        "P6",    # 24 RASP_IO08
        "None",  # 25 GND
        "N5",    # 26 RASP_IO07
        "M7",    # 27 RASP_ID_SD
        "M4",    # 28 RASP_ID_SC
        "K8",    # 29 RASP_IO05
        "None",  # 30 GND
        "L7",    # 31 RASP_IO06
        "L8",    # 32 RASP_IO12
        "M5",    # 33 RASP_IO13
        "None",  # 34 GND
        "M6",    # 35 RASP_IO19
        "N6",    # 36 RASP_IO16
        "P5",    # 37 RASP_IO26
        "R3",    # 38 RASP_IO20
        "None",  # 39 GND
        "R4",    # 40 RASP_IO21
    ),

    # Section 8.6 PMOD Header
    # PMOD signal number:
    #          1   2  3  4  7  8  9   10
    ("PMOD0", "D10 D9 D7 D8 D6 D5 D4  D3"),
    ("PMOD1", "E10 E9 E7 E8 E4 E3 E2  F1"),
    ("PMOD2", "J2  J1 K2 K1 K3 K4 D17 E18"),
]

# Test and Demo ------------------------------------------------------------------------------------

serial_pmods = [
    ("serial_pmod0", 0,
        Subsignal("rx", Pins("PMOD0:0"), IOStandard("LVCMOS33")),
        Subsignal("tx", Pins("PMOD0:1"), IOStandard("LVCMOS33")),
    ),
    ("serial_pmod1", 0,
        Subsignal("rx", Pins("PMOD1:0"), IOStandard("LVCMOS33")),
        Subsignal("tx", Pins("PMOD1:1"), IOStandard("LVCMOS33")),
    ),
    ("serial_pmod2", 0,
        Subsignal("rx", Pins("PMOD2:0"), IOStandard("LVCMOS33")),
        Subsignal("tx", Pins("PMOD2:1"), IOStandard("LVCMOS33")),
    ),
]


# Platform -----------------------------------------------------------------------------------------

class Platform(LatticeNexusPlatform):
    default_clk_name   = "clk12"
    default_clk_period = 1e9/12e6

    def __init__(self, device="LIFCL-40-9BG400C", toolchain="radiant", **kwargs):
        # Accept "LIFCL" for backwards compatibility.
        # LIFCL just means Crosslink-NX so we can expect every
        # Crosslink-NX Evaluation Board to have a LIFCL part.
        if device == "LIFCL":
            device == "LIFCL-40-9BG400C"
        assert device in ["LIFCL-40-9BG400C", "LIFCL-40-8BG400CES"]
        LatticeNexusPlatform.__init__(self, device, _io, _connectors, toolchain=toolchain, **kwargs)

    def request(self, *args, **kwargs):
        import time
        if "serial" in args:
            msg =  "FT2232H will be used as serial, make sure that:\n"
            msg += " -the hardware has been modified: R18 and R19 should be removed, two 0 Ω resistors shoud be populated on R15 (and not R16) and R17.\n"
            msg += " -the chip is configured as UART with virtual COM on port B (With FTProg or https://github.com/trabucayre/fixFT2232_ecp5evn)."
            print(msg)
            time.sleep(2)
        return LatticeNexusPlatform.request(self, *args, **kwargs)

    def create_programmer(self, mode = "direct", prog="radiant"):
        assert mode in ["direct","flash"]
        assert prog in ["radiant","ecpprog","openocd"]

        if prog == "ecpprog":
            return EcpprogProgrammer()

        if prog == "openocd":
            return OpenOCDJTAGProgrammer("openocd_evn_nx.cfg")

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
