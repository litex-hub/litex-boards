#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 blurbdust <blurbdust@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

# Microsoft/HP "Storey Peak" Catapult v2 FPGA accelerator card.
#   P/N X930613-001 / 861309-001, PCB DAT6MTHUEB0 rev B.
#   Altera Stratix V GS, PCIe x16 edge (2x bifurcated x8), 2x QSFP+ 40G, 72-bit DDR3L.
#
# Pin assignments are transcribed from the unofficial Pikes Peak/Storey Peak reference design
# (https://github.com/j-marjanovic/pp-sp-reference-design, project/otma_bringup.qsf). No pin here
# is inferred.
#
# Verified on hardware:
#   clk125, user_led 0-7 (active high), i2c 0/1/2, pcie_x8 0.
# Not verified:
#   ddram, ddram_oct, qsfp 0/1, qsfp_refclk, pcie_x8 1.
#   The qsfp lane assignments are the weakest data here: they are commented out in the reference
#   design, so that design never exercised them.
# Known bad:
#   i2c 3, see the note at its declaration.
#
# The chip-face marking "5SGSKF40I3LNAC" is not a valid Quartus device name. The JTAG IDCODE
# 0x029070dd identifies the die as 5SGSMD5; the reference design builds and runs as
# 5SGSMD5K1F40C1, which is what is used here.

import os
import shutil
import subprocess

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk
    # 125 MHz from the onboard IDT clock generator. SSTL-135 because the pin sits in the DDR3 bank.
    # Whether it free-runs at power-on or needs the IDT part programmed over i2c0 is not established.
    ("clk125", 0, Pins("M23"), IOStandard("SSTL-135")),

    # Leds
    ("user_led", 0, Pins("A11"), IOStandard("2.5 V")),
    ("user_led", 1, Pins("A10"), IOStandard("2.5 V")),
    ("user_led", 2, Pins("B10"), IOStandard("2.5 V")),
    ("user_led", 3, Pins("C10"), IOStandard("2.5 V")),
    ("user_led", 4, Pins("C9"),  IOStandard("2.5 V")),
    ("user_led", 5, Pins("C8"),  IOStandard("2.5 V")),
    ("user_led", 6, Pins("B8"),  IOStandard("2.5 V")),
    ("user_led", 7, Pins("A8"),  IOStandard("2.5 V")),

    # I2C busses
    ("i2c", 0,
        Subsignal("scl", Pins("N7")),
        Subsignal("sda", Pins("P7")),
        IOStandard("2.5 V")
    ), # IDT clock generator.
    ("i2c", 1,
        Subsignal("scl", Pins("AB24")),
        Subsignal("sda", Pins("AC24")),
        IOStandard("2.5 V")
    ), # QSFP0 module.
    ("i2c", 2,
        Subsignal("scl", Pins("AA25")),
        Subsignal("sda", Pins("AB25")),
        IOStandard("2.5 V")
    ), # QSFP1 module.
    # Board monitor. Does not work as assigned: both lines read low permanently and do not respond
    # to being driven, so a bus scan sees every address ACK. i2c 0/1/2 behave correctly on the same
    # card. Kept because it is what the reference design assigns.
    ("i2c", 3,
        Subsignal("scl", Pins("AW26")),
        Subsignal("sda", Pins("AV26")),
        IOStandard("2.5 V")
    ),

    # DDR3 on-chip-termination RZQ calibration resistor.
    ("ddram_oct", 0, Pins("B34"), IOStandard("SSTL-135")),

    # PCIe: x16 edge connector, bifurcated as 2x x8 onto the two Stratix V PCIe hard IP blocks.
    # Only the block wired to `pcie_x8` 1 is enabled by default in the 5SGSMD5K1F40C1 device
    # database, so a fit on the `pcie_x8` 0 pins fails with "Error (175020): The Fitter cannot place
    # logic Receiver channel ... PIN_AV2". Connector 0 is still the half to use: a x16 card in an
    # x8-wired slot only has edge lanes 0-7 connected, so a design on connector 1 trains at Width x0.
    # Platform.build() makes Quartus place it, see _PCIE_HIP0_ENABLE below.
    #
    # The reference QSF assigns differential negatives as an attribute of the positive signal
    # (`-to "PCIE1_SERIAL_RX[0](n)"`), which LiteX cannot emit. Only the positives are given here,
    # which is what Quartus wants for transceiver pins; the negatives are kept in comments.
    ("pcie_x8", 0,
        # rx_n: AV1 AT1 AP1 AM1 AH1 AF1 AD1 AB1
        Subsignal("rx_p", Pins("AV2 AT2 AP2 AM2 AH2 AF2 AD2 AB2"), IOStandard("1.5-V PCML")),
        # tx_n: AU3 AR3 AN3 AL3 AG3 AE3 AC3 AA3
        Subsignal("tx_p", Pins("AU4 AR4 AN4 AL4 AG4 AE4 AC4 AA4"), IOStandard("1.5-V PCML")),
        Subsignal("perst_n", Pins("AB28"), IOStandard("2.5 V")),
        # clk_n: AF5 (HCSL, 100 MHz)
        Subsignal("clk_p",   Pins("AF6"),  IOStandard("HCSL")),
    ),
    ("pcie_x8", 1,
        # rx_n: AV39 AT39 AP39 AM39 AH39 AF39 AD39 AB39
        Subsignal("rx_p", Pins("AV38 AT38 AP38 AM38 AH38 AF38 AD38 AB38"), IOStandard("1.5-V PCML")),
        # tx_n: AU37 AR37 AN37 AL37 AG37 AE37 AC37 AA37
        Subsignal("tx_p", Pins("AU36 AR36 AN36 AL36 AG36 AE36 AC36 AA36"), IOStandard("1.5-V PCML")),
        Subsignal("perst_n", Pins("AC28"), IOStandard("2.5 V")),
        # clk_n: AF35 (HCSL, 100 MHz)
        Subsignal("clk_p",   Pins("AF34"), IOStandard("HCSL")),
    ),

    # QSFP+: 2 cages, 4 lanes each.
    # Weakest provenance in this file: every QSFP transceiver line is commented out in the reference
    # QSF, so that design never exercised them. Transcribed but unused, not hardware-proven.
    ("qsfp", 0,
        # rx_n: V1 T1 P1 M1
        Subsignal("rx_p", Pins("V2 T2 P2 M2"), IOStandard("1.5-V PCML")),
        # tx_n: U3 R3 N3 L3
        Subsignal("tx_p", Pins("U4 R4 N4 L4"), IOStandard("1.5-V PCML")),
    ),
    ("qsfp", 1,
        # rx_n: K1 H1 F1 D1
        Subsignal("rx_p", Pins("K2 H2 F2 D2"), IOStandard("1.5-V PCML")),
        # tx_n: J3 G3 E3 C3
        Subsignal("tx_p", Pins("J4 G4 E4 C4"), IOStandard("1.5-V PCML")),
    ),

    # QSFP transceiver reference clock. LVDS, 1.551 ns period in the reference SDC => 644.53 MHz.
    # clk_n: T6. This assignment is NOT commented out in the reference QSF.
    ("qsfp_refclk", 0, Pins("T7"), IOStandard("LVDS")),
]

# DDR3L --------------------------------------------------------------------------------------------

# 9x SK Hynix H5TC4G83BFR (4 Gb x8) => 72 DQ = 64 data + 8 ECC, 4 GiB addressable.
#
# No target drives these pins yet. Transcribed from the reference design's QSF, where they appear as
# `memory_mem_*`, the conduit of an Altera UniPHY `altera_mem_if_ddr3_emif`. The terminations are
# what that IP's `*_p0_pin_assignments.tcl` emits at fit time, so the script does not have to be
# injected mid-flow. Byte lanes are one per line, DQ group 0 first; group 8 is the ECC device.

_ddram_dq = [
    "R32 P32 M33 T31 N34 P34 L34 L33",
    "F32 G33 G32 K33 J33 G34 K34 J34",
    "D33 C33 B32 A32 A34 A35 A36 A37",
    "G31 H31 E31 F30 C30 D30 A31 B31",
    "E28 H28 G28 C28 B28 A28 B29 A29",
    "G26 F26 H26 D27 B26 A26 C26 C27",
    "G24 F24 G25 D24 C24 C25 B25 A25",
    "H23 G23 H22 C22 B22 A22 B23 A23",
    "F20 E20 G20 C20 C21 E21 B20 A20",  # ECC.
]
_ddram_dqs_p = "N32 F33 E34 D31 H29 G27 E24 F23 G21".split()
_ddram_dqs_n = "M32 E33 D34 C31 G29 F27 E25 E23 F21".split()
_ddram_dm    = "N33 H34 C34 E30 D28 E27 D25 D22 D21".split()

def _ddram_io(name, nb_byte_lanes):
    """Build a DDR3 resource with `nb_byte_lanes` byte lanes (8 = 64-bit, 9 = 72-bit with ECC)."""
    n = nb_byte_lanes
    ac_term  = Misc(("OUTPUT_TERMINATION", "SERIES 40 OHM WITHOUT CALIBRATION"))
    dat_term = [Misc(("INPUT_TERMINATION",  "PARALLEL 40 OHM WITH CALIBRATION")),
                Misc(("OUTPUT_TERMINATION", "SERIES 40 OHM WITH CALIBRATION"))]
    return (name, 0,
        Subsignal("a", Pins(
            "J27 J21 J29 L28 P26 M26 N25 P25",
            "N22 N26 K27 L27 N27 M27 N21 K28"), IOStandard("SSTL-135"), ac_term),
        Subsignal("ba",      Pins("J28 K21 L26"), IOStandard("SSTL-135"), ac_term),
        Subsignal("ras_n",   Pins("L21"),         IOStandard("SSTL-135"), ac_term),
        Subsignal("cas_n",   Pins("L24"),         IOStandard("SSTL-135"), ac_term),
        Subsignal("we_n",    Pins("P23"),         IOStandard("SSTL-135"), ac_term),
        Subsignal("cs_n",    Pins("N23"),         IOStandard("SSTL-135"), ac_term),
        Subsignal("cke",     Pins("K24"),         IOStandard("SSTL-135"), ac_term),
        Subsignal("odt",     Pins("M21"),         IOStandard("SSTL-135"), ac_term),
        Subsignal("reset_n", Pins("L20"),         IOStandard("SSTL-135"),
            Misc(("OUTPUT_TERMINATION", "SERIES 40 OHM WITH CALIBRATION"))),
        Subsignal("dm",      Pins(" ".join(_ddram_dm[:n])), IOStandard("SSTL-135"),
            Misc(("OUTPUT_TERMINATION", "SERIES 40 OHM WITH CALIBRATION"))),
        Subsignal("dq",      Pins(" ".join(_ddram_dq[:n])), IOStandard("SSTL-135"), *dat_term),
        Subsignal("dqs_p",   Pins(" ".join(_ddram_dqs_p[:n])),
            IOStandard("DIFFERENTIAL 1.35-V SSTL"), *dat_term),
        Subsignal("dqs_n",   Pins(" ".join(_ddram_dqs_n[:n])),
            IOStandard("DIFFERENTIAL 1.35-V SSTL"), *dat_term),
        Subsignal("clk_p",   Pins("J23"), IOStandard("DIFFERENTIAL 1.35-V SSTL"), ac_term),
        Subsignal("clk_n",   Pins("J24"), IOStandard("DIFFERENTIAL 1.35-V SSTL"), ac_term),
        Misc(("PACKAGE_SKEW_COMPENSATION", "OFF")),
    )

_io += [
    _ddram_io("ddram",     8),  # 64-bit, no ECC. Default.
    _ddram_io("ddram_ecc", 9),  # 72-bit, 64 data + 8 ECC.
]

# PCIe Hard IP on Connector 0 ----------------------------------------------------------------------

# Quartus asks its device database (libddb_dev.so) whether each hard block of the device is enabled.
# Preloaded into Quartus, this reports the PCIe hard IP block wired to `pcie_x8` 0 as enabled and
# forwards every other query unchanged. Nothing on disk is modified and the bitstream is an ordinary
# one. Altera does not list this block for the part, so it is used as found on these cards. The
# global id and the symbol were identified by Ruurd Keizer: https://github.com/ruurdk/sv_second_pcie_hip.

_PCIE_HIP0_GLOBAL_ID = 1174964

_PCIE_HIP0_ENABLE = r"""
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

#define SYMBOL "_ZNK12DEV_DIE_INFO20is_global_id_enabledEj"

typedef bool (*is_enabled_fn)(const void *self, unsigned id);

static is_enabled_fn real_is_enabled;

/* Resolved on first use: every process Quartus starts inherits the preload, most never load the database. */
static bool resolve(void)
{
    void *lib;
    if (real_is_enabled != NULL)
        return true;
    lib = dlopen("libddb_dev.so", RTLD_LAZY | RTLD_LOCAL | RTLD_NOLOAD);
    if (lib == NULL)
        lib = dlopen("libddb_dev.so", RTLD_LAZY | RTLD_LOCAL);
    if (lib == NULL) {
        fprintf(stderr, "pcie_hip0_enable: %s\n", dlerror());
        return false;
    }
    real_is_enabled = (is_enabled_fn)dlsym(lib, SYMBOL);
    if (real_is_enabled == NULL) {
        fprintf(stderr, "pcie_hip0_enable: %s not found in this Quartus version.\n", SYMBOL);
        return false;
    }
    return true;
}

bool _ZNK12DEV_DIE_INFO20is_global_id_enabledEj(const void *self, unsigned id)
{
    if (id == GLOBAL_ID)
        return true;
    /* Answering for blocks it cannot ask about would corrupt placement: stop instead. */
    if (!resolve())
        abort();
    return real_is_enabled(self, id);
}
"""

def _build_pcie_hip0_enable(build_dir):
    src = os.path.abspath(os.path.join(build_dir, "pcie_hip0_enable.c"))
    so  = os.path.abspath(os.path.join(build_dir, "pcie_hip0_enable.so"))
    os.makedirs(build_dir, exist_ok=True)
    with open(src, "w") as f:
        f.write(_PCIE_HIP0_ENABLE)
    cc  = os.environ.get("CC", "cc")
    cmd = [cc, "-shared", "-fPIC", "-O2", f"-DGLOBAL_ID={_PCIE_HIP0_GLOBAL_ID}u", "-o", so, src, "-ldl"]
    if shutil.which(cc) is None or subprocess.call(cmd) != 0:
        raise OSError("pcie_x8 0 needs a C compiler to build " + so + ": " + " ".join(cmd))
    return so

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name   = "clk125"
    default_clk_period = 1e9/125e6

    def __init__(self, toolchain="quartus"):
        AlteraPlatform.__init__(self, "5SGSMD5K1F40C1", _io, toolchain=toolchain)

        # Safety: this is a board we have no schematic for, so never drive unused pins. This is a
        # deliberate choice rather than something transcribed from the reference design (which
        # relied on the Quartus default), and it matches the Stratix V default behaviour.
        self.add_platform_command(
            "set_global_assignment -name RESERVE_ALL_UNUSED_PINS \"AS INPUT TRI-STATED WITH WEAK PULL-UP\"")

        # Passive heatsink in a server chassis; the reference design assumes forced airflow.
        self.add_platform_command(
            "set_global_assignment -name POWER_PRESET_COOLING_SOLUTION \"23 MM HEAT SINK WITH 200 LFPM AIRFLOW\"")

    def create_programmer(self):
        # The onboard FT232H (0403:6014) is wired to the FPGA JTAG, per
        # https://github.com/j-marjanovic/jtag-quartus-ft232h. Untested via openFPGALoader; the
        # documented path is OpenOCD-init followed by quartus_pgm.
        return OpenFPGALoader(cable="ft232")

    def build(self, *args, **kwargs):
        # A design on `pcie_x8` 0 runs Quartus with _PCIE_HIP0_ENABLE preloaded. The environment is
        # restored afterwards, so later tools (programmer, flash) do not inherit it.
        uses_hip0 = any(r[0] == "pcie_x8" and r[1] == 0 for r, _ in self.constraint_manager.matched)
        if not (uses_hip0 and kwargs.get("run", True)):
            return AlteraPlatform.build(self, *args, **kwargs)
        so      = _build_pcie_hip0_enable(kwargs.get("build_dir", "build"))
        quartus = shutil.which("quartus_map")
        libdir  = os.path.join(os.path.dirname(os.path.dirname(quartus)), "linux64") if quartus else None
        saved   = {k: os.environ.get(k) for k in ["LD_PRELOAD", "LD_LIBRARY_PATH"]}
        os.environ["LD_PRELOAD"]      = ":".join(p for p in [so, saved["LD_PRELOAD"]] if p)
        os.environ["LD_LIBRARY_PATH"] = ":".join(p for p in [libdir, saved["LD_LIBRARY_PATH"]] if p)
        try:
            return AlteraPlatform.build(self, *args, **kwargs)
        finally:
            for k, v in saved.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

    def do_finalize(self, fragment):
        AlteraPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk125", loose=True), 1e9/125e6)
