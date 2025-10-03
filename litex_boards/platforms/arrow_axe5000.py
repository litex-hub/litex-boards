#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Gwenhael Goavec-merou<gwenhael.goavec-merou@trabucayre.com>
#
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.altera            import AlteraPlatform
from litex.build.altera.programmer import USBBlaster
from litex.build.generic_platform  import Pins, IOStandard, Subsignal, Misc

# IOs ----------------------------------------------------------------------------------------------

_io = [

    # Clk
    ("clk25",      0, Pins("A7"),    IOStandard("1.3-V LVCMOS")),
    ("refclk",     0, Pins("AJ28"),  IOStandard("3.3-V LVCMOS")),
    ("sys_clk100", 0, Pins("BF111"), IOStandard("1.3-V LVCMOS")),

    # Serial
    ("serial", 0,
        Subsignal("rx", Pins("AG23")),
        Subsignal("tx", Pins("AG24")),
        IOStandard("3.3-V LVCMOS"),
    ),

    # Leds
    ("user_led", 0, Pins("AG21"), IOStandard("3.3-V LVCMOS")),
    ("rgb_led",  0,
        Subsignal("r", Pins("AH22")),
        Subsignal("g", Pins("AK21")),
        Subsignal("b", Pins("AK20")),
        IOStandard("3.3-V LVCMOS"),
    ),

    # Switches
    ("user_sw", 0, Pins("A14"), IOStandard("1.3-V LVCMOS")),
    ("user_sw", 1, Pins("A13"), IOStandard("1.3-V LVCMOS")),

    # Buttons
    ("user_btn", 0, Pins("A12"), IOStandard("1.3-V LVCMOS"), Misc("WEAK_PULL_UP_RESISTOR ON")),

    # HyperRAM
    ("hyperram", 0,
        Subsignal("dq",    Pins("C3 C2 B4 B6 D3 A4 B3 C6")),
        Subsignal("rwds",  Pins("A6")),
        Subsignal("cs_n",  Pins("D8")),
        Subsignal("rst_n", Pins("F7")),
        Subsignal("clk",   Pins("D7")),
        IOStandard("1.3-V LVCMOS")
    ),

    # VADJ selector between 1.2V(low) and 1.3V(high)
    ("vsel_1v3", 0, Pins("AJ24"), IOStandard("3.3-V LVCMOS")),

    # Accelerometer (LIS3DH)
    ("accel_int", 0, Pins("AK24 AJ25"), IOStandard("3.3-V LVCMOS")),
    ("accel_i2c", 0,
        Subsignal("sda", Pins("AK26")),
        Subsignal("scl", Pins("AH25")),
        IOStandard("3.3-V LVCMOS"),
    ),

    # MKR Form Factor Peripherals ------------------------------------------------------------------

    # Serial
    ("serial", 1,
        Subsignal("rx", Pins("AH23")), # J2.8 (D13)
        Subsignal("tx", Pins("AJ23")), # J2.9 (D14)
        IOStandard("3.3-V LVCMOS"),
    ),

    # I2C
    ("i2c", 0,
        Subsignal("scl", Pins("AK22")), # J2.7 (D12)
        Subsignal("sda", Pins("AJ22")), # J2.6 (D11)
        IOStandard("3.3-V LVCMOS"),
    ),

    # SPI
    ("spi", 0,
        Subsignal("clk",  Pins("AH18")), # J2.4 (D9)
        Subsignal("cs_n", Pins("AH27")), # J1.6 (AIN4)
        Subsignal("mosi", Pins("AH21")), # J2.3 (D8)
        Subsignal("miso", Pins("AJ20")), # J2.5 (D10)
        IOStandard("3.3-V LVCMOS"),
    ),

    # Interrupt
    ("int", 0, Pins("AF27"), IOStandard("3.3-V LVCMOS")), # J1.7 (AIN5)

    # PWM
    ("pwm", 0, Pins("AF26"), IOStandard("3.3-V LVCMOS")), # J1.8 (AIN6)
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    # Arduino MKR Header (J1/J2)
    ("arduino_io", {
        # J1
        "AREF" : "AF22", #  1
        "AIN0" : "AF23", #  2
        "AIN1" : "AF24", #  3
        "AIN2" : "AG26", #  4
        "AIN3" : "AH28", #  5
        "AIN4" : "AH27", #  6
        "AIN5" : "AF27", #  7
        "AIN6" : "AF26", #  8
        "D0"   : "AE25", #  9
        "D1"   : "AF21", # 10
        "D2"   : "AH20", # 11
        "D3"   : "AG19", # 12
        "D4"   : "AF19", # 13
        "D5"   : "AG20", # 14

        # J2
        "D6"   : "AK19", #  1
        "D7"   : "AJ19", #  2
        "D8"   : "AH21", #  3
        "D9"   : "AH18", #  4
        "D10"  : "AJ20", #  5
        "D11"  : "AJ22", #  6 / Also Connected to AK25
        "D12"  : "AK22", #  7 / Also Connected to AK27
        "D13"  : "AH23", #  8
        "D14"  : "AJ23", #  9
        "RST"  : "---",  # 10
        "GND"  : "---",  # 11
        "3_3V" : "---",  # 12
        "VIN"  : "---",  # 13
        "5V"   : "---",  # 14
    }),

    # CRUVI header
    ["J3",
        # B2_P/B2_N (27/29) are assigned to 2 sets of pins on the FPGA
        # due to MIPI Hard IP pin placement:
        # B2_P: U5/T4
        # B2_N: AC6/AC5
        # -----------------------------------------------------------
        " ----", # 0
        #   NC           3.3V                     3.3V        ( 1-10).
        " ----   N7 AH26 ---- AJ29   N6 AJ27  AF1 ---- AE10",
        #       GND  GND                      GND  GND        (11-20).
        " AJ28 ---- ----   N2   V6   N1   W5 ---- ----   R2",
        #                 GND  GND        T4       AC5  GND   (21-30).
        "  AC7   T1  AD7 ---- ----   T2   U5   U1  AC6 ----",
        #  GND                     VADJ  GND                  (31-40).
        " ----   V1   V3   V2   W3 ---- ----   T3   U4   R4",
        #  GND  GND  GND                      GND  GND   NC   (41-50).
        "   U3 ---- ----   Y1   P5   W2   P4 ---- ---- ----",
        #   NC   NC   NC  GND   NC   NC   NC   NC   NC   5V   (51-60).
       " ---- ---- ---- ---- ---- ---- ---- ---- ---- ----",
    ],
]

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name   = "clk25"
    default_clk_period = 1e9/25e6

    def __init__(self, toolchain="quartus"):
        AlteraPlatform.__init__(self, "A5EC008BM16AE6S", _io, _connectors, toolchain=toolchain)
        self.create_rbf = True
        self.create_svf = False # Not supported for Agilex5 family.
        self.add_platform_command("set_global_assignment -name ENABLE_INTERMEDIATE_SNAPSHOTS \"ON\"")

        # Calculates clock uncertainties
        self.toolchain.additional_sdc_commands.append("derive_clock_uncertainty")

    def create_programmer(self):
        return USBBlaster(cable_name="USB Blaster III")

    def do_finalize(self, fragment):
        AlteraPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk25", loose=True), 1e9/25e6)
