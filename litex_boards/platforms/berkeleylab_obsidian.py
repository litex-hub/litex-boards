#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Michael Betz <michael@betz-engineering.ch>
# SPDX-License-Identifier: BSD-2-Clause
#
# Obsidian A35 is a low cost FPGA carrier board with several SFP ports,
# many PMOD IOs and Arduino shield compatibility.
# It was developed at Berkeley Lab as a kind of smart IO extender.
# It facilitates interfacing ADCs, DACs, sensors, UI elements or other
# peripherals to a central larger FPGA board or a PC.


from litex.build.generic_platform import Subsignal, Pins, IOStandard, Misc
from litex.build.xilinx import Xilinx7SeriesPlatform
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # WR_CLK0 (125 MHz, DAC-tunable), MGTREFCLK0
    (
        "clk125",
        0,
        Subsignal("p", Pins("D6")),
        Subsignal("n", Pins("D5")),
    ),
    # CLK20_VCXO (20 MHz, DAC-tunable), PAD NOT CLOCK-CAPABLE!
    ("clk20", 0, Pins("D13"), IOStandard("LVCMOS33")),
    # REF_CLK0 (Si5351A, channel 0 and 1, I2C-tunable, 2.5 kHz - 200 MHz), MGTREFCLK1
    # Note: the Si5351 needs to be configured to get HCSL compatible outputs.
    # See Section 6.7 in the datasheet and register setting CLKx_INV.
    (
        "clkmgt",
        0,
        Subsignal("p", Pins("B6")),
        Subsignal("n", Pins("B5")),
    ),
    # CLK2 (Si5351A, channel 2, I2C-tunable, 2.5 kHz - 200 MHz)
    ("clk2", 0, Pins("E15"), IOStandard("LVCMOS33")),
    # Gigabit Ethernet transceiver (RTL8211F-CG)
    (
        "eth",
        0,
        Subsignal("rst_n", Pins("A13")),
        Subsignal("mdio", Pins("E18")),
        Subsignal("mdc", Pins("H14")),
        Subsignal("rx_ctl", Pins("D16")),
        Subsignal("rx_data", Pins("B16 C16 D14 C13")),
        Subsignal("tx_ctl", Pins("A17")),
        Subsignal("tx_data", Pins("B17 E16 E17 D18")),
        IOStandard("LVCMOS33"),
    ),
    (
        "eth_clocks",
        0,
        Subsignal("tx", Pins("D15")),
        Subsignal("rx", Pins("E13")),
        IOStandard("LVCMOS33"),
    ),
    # USB UART (FT2232HQ)
    (
        "serial",
        0,
        # FT2232 --> FPGA
        Subsignal("rx", Pins("H18")),
        # FT2232 <-- FPGA
        Subsignal("tx", Pins("F17")),
        IOStandard("LVCMOS33"),
    ),
    # FT2232 --> FPGA. To use the RTS signal, SW2 must be ON
    ("serial_rts", 0, Pins("B10"), IOStandard("LVCMOS33")),
    # SPI Boot Flash (S25FL128SAGMFI001)
    # use STARTUPE2 primitive to access the clock pin
    (
        "spiflash",
        0,
        Subsignal("cs_n", Pins("L15")),
        Subsignal("mosi", Pins("K16")),
        Subsignal("miso", Pins("L17")),
        IOStandard("LVCMOS33"),
    ),
    # I2C system bus, connected to:
    #   0x40: IO-extender for SFP0 and SFP1 status pins (TCA9535RTWR)
    #   0x42: IO-extender for SFP2 and SFP3 status pins (TCA9535RTWR)
    #   0xC0: Clock synthesizer (Si5351A)
    #   0xA0: 256Kb I2C Serial EEPROM with Pre-Programmed Serial Number (24AA256UID)
    #   0xE0: I2C-switch for the 4 SFP ports (PCA9546ARGV)
    (
        "i2c_fpga",
        0,
        Subsignal("scl", Pins("H17")),
        Subsignal("sda", Pins("F14")),
        IOStandard("LVCMOS33"),
    ),
    # I2C pins of the Arduino host
    (
        "i2c_arduino",
        0,
        Subsignal("scl", Pins("J18")),
        Subsignal("sda", Pins("C12")),
        IOStandard("LVCMOS33"),
    ),
    # 2x DAC for White Rabbit VCXO frequency control (DAC8550IDGK)
    # clk and din is shared between the 2 DACs
    # synca updates the clk125 tuning voltage
    # syncb updates the clk20 tuning voltage
    (
        "wr_dac",
        0,
        Subsignal("clk", Pins("C11")),
        Subsignal("din", Pins("B11")),
        Subsignal("synca", Pins("D11")),
        Subsignal("syncb", Pins("D10")),
        IOStandard("LVCMOS33"),
    ),
    # DDR3 DRAM chip (AS4C256M16D3)
    (
        "ddram",
        0,
        Subsignal("a", Pins(r"U2 V3 R7 P6 V2 V4 V7 T7 V8 U4 U1 U7 U6 U5 R6 M5"), IOStandard("SSTL15")),
        Subsignal("ba", Pins(r"T3 V6 R2"), IOStandard("SSTL15")),
        Subsignal("ras_n", Pins(r"R3"), IOStandard("SSTL15")),
        Subsignal("cas_n", Pins(r"T2"), IOStandard("SSTL15")),
        Subsignal("we_n", Pins(r"T4"), IOStandard("SSTL15")),
        Subsignal("cs_n", Pins(r"P5"), IOStandard("SSTL15")),
        Subsignal("dm", Pins(r"L5 M6"), IOStandard("SSTL15")),
        Subsignal("dq", Pins(r"K3 L4 K5 K6 J4 L2 J5 L3 N3 M1 N2 M4 N6 M2 P4 N4"), IOStandard("SSTL15")),
        Subsignal("dqs_p", Pins(r"K2 N1"), IOStandard("DIFF_SSTL15")),
        Subsignal("dqs_n", Pins(r"K1 P1"), IOStandard("DIFF_SSTL15")),
        Subsignal("clk_p", Pins(r"R5"), IOStandard("DIFF_SSTL15")),
        Subsignal("clk_n", Pins(r"T5"), IOStandard("DIFF_SSTL15")),
        Subsignal("cke", Pins(r"R1"), IOStandard("SSTL15")),
        Subsignal("odt", Pins(r"P3"), IOStandard("SSTL15")),
        Subsignal("reset_n", Pins(r"J6"), IOStandard("LVCMOS15")),
        Misc("SLEW=FAST"),
    ),
    (
        "sfp_tx",
        0,
        Subsignal("p", Pins("H2")),
        Subsignal("n", Pins("H1")),
    ),
    (
        "sfp_tx",
        1,
        Subsignal("p", Pins("F2")),
        Subsignal("n", Pins("F1")),
    ),
    (
        "sfp_tx",
        2,
        Subsignal("p", Pins("D2")),
        Subsignal("n", Pins("D1")),
    ),
    (
        "sfp_tx",
        3,
        Subsignal("p", Pins("B2")),
        Subsignal("n", Pins("B1")),
    ),
    (
        "sfp_rx",
        0,
        Subsignal("p", Pins("E4")),
        Subsignal("n", Pins("E3")),
    ),
    (
        "sfp_rx",
        1,
        Subsignal("p", Pins("A4")),
        Subsignal("n", Pins("A3")),
    ),
    (
        "sfp_rx",
        2,
        Subsignal("p", Pins("C4")),
        Subsignal("n", Pins("C3")),
    ),
    (
        "sfp_rx",
        3,
        Subsignal("p", Pins("G4")),
        Subsignal("n", Pins("G3")),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("pmoda", r"M16 N17 R18 U16 M17 N18 P18 V17"),  # J4
    ("pmodb", r"T18 U17 U15 V14 R17 T17 V16 U14"),  # J5
    ("pmodc", r"M15 N16 P15 K18 N14 P16 K17 L18"),  # J6
    ("pmodd", r"J16 K15 F15 J14 J15 M14 G15 L14"),  # J7
    ("pmode", r"U10 U9 V9 V11 V12 U12 V13 U11"),  # J14
    ("pmodf", r"T13 T12 R13 T14 T15 P14 R16 R15"),  # J15
    # digital Arduino host pins
    ("arduino_d", r"G14 H16 A12 B12 C14 G17 G16 A15 C18 F18 C17 B15 B14 A14"),
    # Analog capable Arduino host pins connected to XADC
    # the order is: A0_P, A0_N, A2_P, A2_N, A1_P, A1_N, A3_P, A3_N
    ("arduino_a", r"C8 D8 A9 B9 C9 D9 A10 B10"),
]


def raw_pmod_io(pmod="pmoda", iostd="LVCMOS33"):
    """use with platform.add_extension() to expose a PMOD as GPIO pins"""
    return [
        (
            pmod,
            0,
            Pins(" ".join([f"{pmod}:{i:d}" for i in range(8)])),
            IOStandard(iostd),
        )
    ]


# Platform -----------------------------------------------------------------------------------------


class Platform(Xilinx7SeriesPlatform):
    default_clk_name = "clk125"
    default_clk_period = 1e9 / 125e6

    def __init__(self, toolchain="vivado"):
        Xilinx7SeriesPlatform.__init__(self, "xc7a35t-csg325", _io, _connectors, toolchain=toolchain)
        self.toolchain.additional_commands = [
            (
                "write_cfgmem -force -format bin -interface spix1 -size 16 -loadbit "
                + '"up 0x0 {build_name}.bit" -file {build_name}.bin'
            )
        ]

        # clk20 is a frequency source, not a phase source, so having it enter on a non-CC pin is OK.
        self.add_platform_command("set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets clk20_IBUF]")
        self.add_platform_command("set_property CONFIG_VOLTAGE 3.3 [current_design]")
        self.add_platform_command("set_property CFGBVS VCCO [current_design]")
        self.add_platform_command("set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 1 [current_design]")
        self.add_platform_command("set_property BITSTREAM.CONFIG.CONFIGRATE 50 [current_design]")
        self.add_platform_command("set_property INTERNAL_VREF 0.75 [get_iobanks 34]")

    def create_programmer(self):
        return OpenOCD("openocd_xc7_ft2232.cfg", flash_proxy_basename="bscan_spi_xc7a35t.bit")

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk20", loose=True), 1e9 / 20e6)
        self.add_period_constraint(self.lookup_request("clk125", loose=True), 1e9 / 125e6)
