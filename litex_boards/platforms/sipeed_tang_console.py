#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022-2023 Icenowy Zheng <uwu@icenowy.me>
# Copyright (c) 2022 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2023 Gwenhael Goavec-Merou <gwenhael@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.build.generic_platform import *
from litex.build.gowin.platform import GowinPlatform
from litex.build.gowin.programmer import GowinProgrammer
from litex.build.openfpgaloader import OpenFPGALoader

from litex_boards.extensions.sdram_modules import MiSTerSDRAM, SipeedSDRAM
from litex_boards.extensions.sipeed        import tang_mega_60k_som_connectors, tang_mega_138k_som_connectors, TangConsoleDock

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk.
    ("clk50",  0, Pins("V22"), IOStandard("LVCMOS33")),

    # Serial.
    ("serial", 0,
        Subsignal("rx", Pins("V14")),
        Subsignal("tx", Pins("U15")),
        IOStandard("LVCMOS33")
    ),

    # Leds.
    ("led", 0,  Pins("G11"), IOStandard("LVCMOS33")), # Done.
    ("led", 1,  Pins("U12"), IOStandard("LVCMOS33")), # Ready.

    # SPIFlash.
    ("spiflash", 0,
        Subsignal("cs_n", Pins("T19")),
        Subsignal("clk",  Pins("L12")),
        Subsignal("miso", Pins("R22")),
        Subsignal("mosi", Pins("P22")),
        Subsignal("wp",   Pins("P21")),
        Subsignal("hold", Pins("R21")),
        IOStandard("LVCMOS33"),
    ),
    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("T19")),
        Subsignal("clk",  Pins("L12")),
        Subsignal("dq",   Pins("P22 R22 P21 R21")),
        IOStandard("LVCMOS33"),
    ),
]


def _ddram_io(device):
    suffix = "_I" if device == "GW5AT-60B" else ""
    return [
        # DDR3 SDRAM MT41J256M16JT-125.
        # Tang Mega 60K: One chip. 138K: Only the first of two chips is used.
        ("ddram", 0,
            Subsignal("a", Pins(
                "M1 K2 G2 J4 J2 H2 G3 J1",
                "J5 H5 L1 H3 K4 K1 D1"), # A15: Unused.
                IOStandard("SSTL15" + suffix),
                Misc("DRIVE=12"),
            ),
            Subsignal("ba",      Pins("P5 P2 M6"), IOStandard("SSTL15" + suffix), Misc("DRIVE=12")),
            Subsignal("ras_n",   Pins("L5"),       IOStandard("SSTL15" + suffix), Misc("DRIVE=12")),
            Subsignal("cas_n",   Pins("L4"),       IOStandard("SSTL15" + suffix), Misc("DRIVE=12")),
            Subsignal("we_n",    Pins("M5"),       IOStandard("SSTL15" + suffix), Misc("DRIVE=12")),
            Subsignal("cs_n",    Pins("P4"),       IOStandard("SSTL15" + suffix), Misc("DRIVE=12")),
            Subsignal("dm",      Pins("AA4 V7"),   IOStandard("SSTL15" + suffix), Misc("DRIVE=12")),
            Subsignal("dq",      Pins(
                " Y4 AB3 AA5 V4 AA1 AB2 AB5 AB1",
                "AA8  Y8 AB7 Y7 AB8  W9 AB6  Y9"),
                IOStandard("SSTL15" + suffix),
                Misc("DRIVE=12"),
            ),
            Subsignal("dqs_p",   Pins("Y3 V9"),    IOStandard("SSTL15D" + suffix), Misc("DRIVE=8")),
            Subsignal("dqs_n",   Pins("AA3 V8"),   IOStandard("SSTL15D" + suffix), Misc("DRIVE=8")),
            Subsignal("clk_p",   Pins("L3"),       IOStandard("SSTL15D" + suffix), Misc("DRIVE=8")),
            Subsignal("clk_n",   Pins("K3"),       IOStandard("SSTL15D" + suffix), Misc("DRIVE=8")),
            Subsignal("cke",     Pins("K6"),       IOStandard("SSTL15" + suffix), Misc("DRIVE=4")),
            Subsignal("odt",     Pins("M2"),       IOStandard("SSTL15" + suffix), Misc("DRIVE=12")),
            Subsignal("reset_n", Pins("L6"),       IOStandard("SSTL15" + suffix), Misc("DRIVE=12")),
            Misc("PULL_MODE=NONE BANK_VCCIO=1.5"),
        ),
    ]


_io_60k = [
    # Rst.
    ("rst", 0, Pins("AA13"), IOStandard("LVCMOS15")), # EX_KEY.0.

    # PCI Express.
    ("pcie_clkreq_n", 0, Pins("AA14"), IOStandard("LVCMOS33")),
    ("pcie", 0,
        Subsignal("rst_n",  Pins("W11"), IOStandard("LVCMOS15")),
        Subsignal("wake_n", Pins("T14"), IOStandard("LVCMOS33")),
    ),
]

_io_138k = [
    # Rst.
    ("rst", 0, Pins("AA13"), IOStandard("LVCMOS33")), # EX_KEY.0.

    # PCI Express.
    ("pcie", 0,
        Subsignal("rst_n", Pins("W11")),
        IOStandard("LVCMOS33"),
        Misc("PULL_MODE=UP DRIVE=OFF BANK_VCCIO=3.3"),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors_60k  = tang_mega_60k_som_connectors
_connectors_138k = tang_mega_138k_som_connectors

# SDRAMs -------------------------------------------------------------------------------------------

def misterSDRAM(conn="sdram0_connector"):
    return MiSTerSDRAM(conn).get_io(GowinPlatform)

def sipeedSDRAM(conn="sdram0_connector"):
    return SipeedSDRAM(conn).get_io(GowinPlatform)

# Docks --------------------------------------------------------------------------------------------

docks = {
    "standard" : TangConsoleDock(),
}

# Platform -----------------------------------------------------------------------------------------

class Platform(GowinPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self, dock="standard", toolchain="gowin", device="GW5AT-60B"):
        assert device in ["GW5AT-60B", "GW5AST-138C"]
        device_map = {
            "GW5AT-60B":   "GW5AT-LV60PG484AC1/I0",
            "GW5AST-138C": "GW5AST-LV138PG484AC1/I0",
        }
        io = {
            "GW5AT-60B":   _io_60k,
            "GW5AST-138C": _io_138k,
        }[device]
        connectors = {
            "GW5AT-60B":   _connectors_60k,
            "GW5AST-138C": _connectors_138k,
        }[device]
        GowinPlatform.__init__(self, device_map[device], _io, connectors, toolchain=toolchain, devicename=device)
        self.add_extension(io)
        self.add_extension(_ddram_io(device))
        if dock is not None:
            if dock not in docks:
                raise ValueError(f"Unsupported dock {dock}, supported: {', '.join(docks)} or None (SoM only).")
            self.add_extension(docks[dock])

        self.toolchain.options["use_ready_as_gpio"] = 1
        self.toolchain.options["use_done_as_gpio"]  = 1
        self.toolchain.options["use_mspi_as_gpio"]  = 1
        #self.toolchain.options["use_sspi_as_gpio"]  = 1
        self.toolchain.options["use_cpu_as_gpio"]   = 1
        self.toolchain.options["rw_check_on_ram"]   = 1
        self.toolchain.options["bit_security"]      = 0
        self.toolchain.options["bit_encrypt"]       = 0
        self.toolchain.options["bit_compress"]      = 0

    def create_programmer(self, kit="openfpgaloader"):
        if kit == "gowin":
            return GowinProgrammer(self.devicename)
        elif kit == "openfpgaloader":
            return OpenFPGALoader(cable="ft2232")
        else:
            raise ValueError(f"Unsupported programmer kit: {kit}")

    def do_finalize(self, fragment):
        GowinPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
