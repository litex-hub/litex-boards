#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022-2023 Icenowy Zheng <uwu@icenowy.me>
# Copyright (c) 2022 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2025 Gwenhael Goavec-Merou <gwenhael.goavec-merou@trabucayre.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.build.generic_platform import *
from litex.build.gowin.platform import GowinPlatform
from litex.build.gowin.programmer import GowinProgrammer
from litex.build.openfpgaloader import OpenFPGALoader

from litex_boards.extensions.sdram_modules import MiSTerSDRAM, SipeedSDRAM
from litex_boards.extensions.sipeed        import tang_mega_138k_som_connectors, TangMegaNeoDock

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst.
    ("clk50", 0, Pins("V22"), IOStandard("LVCMOS33"), Misc("PULL_MODE=UP DRIVE=OFF PULL_STRENGTH=STRONG BANK_VCCIO=3.3")),

    # Serial.
    ("serial", 0,
        Subsignal("rx", Pins("V14")),
        Subsignal("tx", Pins("U15")),
        IOStandard("LVCMOS33")
    ),

    # Leds
    ("led", 0, Pins("G11"), IOStandard("LVCMOS33")), # Done.
    ("led", 1, Pins("U12"), IOStandard("LVCMOS33")), # Ready.

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

    ## PCI Express
    #("pcie_clkreq_n", 0, Pins("AA14"), IOStandard("LVCMOS33")),
    ("pcie", 0,
        Subsignal("rst_n",  Pins("W11")),
    #    Subsignal("wake_n", Pins("T14"),  IOStandard("LVCMOS33")),
        IOStandard("LVCMOS33"),
        Misc("PULL_MODE=UP DRIVE=OFF BANK_VCCIO=3.3"),
    ),

    ## DDR3 SDRAM MT41J256M16JT-125
    # FIXME: Tang Mega 138k: Two chips (but only one is used here.
    ("ddram", 0,
        Subsignal("a", Pins(
            "M1 K2 G2 J4 J2 H2 G3 J1",
            "J5 H5 L1 H3 K4 K1 D1"),   # R1(A15): Unused
        ),
        Subsignal("ba",      Pins("P5 P2 M6")),
        Subsignal("ras_n",   Pins("L5")),
        Subsignal("cas_n",   Pins("L4")),
        Subsignal("we_n",    Pins("M5")),
        Subsignal("cs_n",    Pins("P4")),
        Subsignal("dm",      Pins("AA4 V7")),
        Subsignal("dq",      Pins(
            " Y4 AB3 AA5 V4 AA1 AB2 AB5 AB1",
            "AA8  Y8 AB7 Y7 AB8  W9 AB6  Y9"),
        ),
        Subsignal("dqs_p",   Pins("Y3 V9"),  IOStandard("SSTL15D"), Misc("PULL_MODE=NONE DRIVE=8 BANK_VCCIO=1.5")),
        Subsignal("dqs_n",   Pins("AA3 V8"), IOStandard("SSTL15D"), Misc("PULL_MODE=NONE DRIVE=8 BANK_VCCIO=1.5")),
        Subsignal("clk_p",   Pins("L3"),     IOStandard("SSTL15D"), Misc("PULL_MODE=NONE DRIVE=8 BANK_VCCIO=1.5")),
        Subsignal("clk_n",   Pins("K3"),     IOStandard("SSTL15D"), Misc("PULL_MODE=NONE DRIVE=8 BANK_VCCIO=1.5")),
        Subsignal("cke",     Pins("K6"),     Misc("PULL_MODE=NONE DRIVE=8 BANK_VCCIO=1.5")),
        Subsignal("odt",     Pins("M2")),
        Subsignal("reset_n", Pins("L6")),
        IOStandard("SSTL15"),
        Misc("PULL_MODE=NONE DRIVE=12 BANK_VCCIO=1.5"),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = tang_mega_138k_som_connectors

# SDRAMs -------------------------------------------------------------------------------------------

def misterSDRAM(conn="sdram0_connector"):
    return MiSTerSDRAM(conn).get_io(GowinPlatform)

def sipeedSDRAM(conn="sdram0_connector"):
    return SipeedSDRAM(conn).get_io(GowinPlatform)

# Docks --------------------------------------------------------------------------------------------

docks = {
    "neo" : TangMegaNeoDock(som="138k"),
}

# Platform -----------------------------------------------------------------------------------------

class Platform(GowinPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self, dock="neo", toolchain="gowin"):
        GowinPlatform.__init__(self, "GW5AST-LV138PG484AC1/I0", _io, _connectors, toolchain=toolchain, devicename="GW5AST-138B")
        if dock is not None:
            if dock not in docks:
                raise ValueError(f"Unsupported dock {dock}, supported: {', '.join(docks)} or None (SoM only).")
            self.add_extension(docks[dock])

        self.toolchain.options["use_ready_as_gpio"] = 1
        self.toolchain.options["use_done_as_gpio"]  = 1
        self.toolchain.options["use_mspi_as_gpio"]  = 1
        self.toolchain.options["use_sspi_as_gpio"]  = 1
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
