#!/usr/bin/env python3

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


GOWIN_TARGETS = [
    "brisbaneSilicon_brs_100_gw1nr9",
    "lckfb_ljpi",
    "modretro_chromatic",
    "myminieye_runber",
    "sipeed_slogic16u3",
    "sipeed_tang_console",
    "sipeed_tang_mega_138k",
    "sipeed_tang_mega_138k_pro",
    "sipeed_tang_mega_60k",
    "sipeed_tang_nano",
    "sipeed_tang_nano_20k",
    "sipeed_tang_nano_4k",
    "sipeed_tang_nano_9k",
    "sipeed_tang_primer_20k",
    "sipeed_tang_primer_25k",
    "trenz_tec0117",
]

GOWIN_OPTIONAL_CASES = [
    ("modretro_chromatic",            ["--with-lcd-colorbars"]),
    ("sipeed_tang_console",           ["--with-lcd-colorbars"]),
    ("sipeed_tang_mega_138k",         ["--with-lcd-colorbars", "--with-spi-sdcard"]),
    ("sipeed_tang_mega_138k_pro",     ["--with-hdmi-out-colorbars", "--with-rgb-led"]),
    ("sipeed_tang_mega_60k",          ["--with-audio", "--with-camera", "--with-spi-sdcard"]),
    ("sipeed_tang_nano_20k",          ["--with-video-colorbars"]),
    ("sipeed_tang_nano_4k",           ["--with-hyperram"]),
    ("sipeed_tang_nano_9k",           ["--with-video-terminal", "--with-spi-sdcard"]),
    ("sipeed_tang_primer_20k",        ["--with-etherbone"]),
    ("sipeed_tang_primer_25k",        ["--with-usb-acm"]),
]


def run_target(target: str, output_dir: Path, extra_args=None) -> subprocess.CompletedProcess:
    if extra_args is None:
        extra_args = []
    cmd = [
        sys.executable,
        "-m",
        f"litex_boards.targets.{target}",
        "--build",
        "--no-compile",
        "--uart-name=stub",
        "--cpu-type=vexriscv",
        "--cpu-variant=minimal",
        "--output-dir",
        str(output_dir / target),
    ] + extra_args
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run no-compile builds for Gowin targets")
    parser.add_argument("--output-dir", type=Path, default=Path("/tmp/litex_boards_gowin_matrix"))
    args = parser.parse_args()

    shutil.rmtree(args.output_dir, ignore_errors=True)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    failures = []
    for target in GOWIN_TARGETS:
        result = run_target(target, args.output_dir)
        if result.returncode:
            failures.append((target, result.stdout))
            print(f"FAIL {target}")
        else:
            print(f"PASS {target}")

    for target, extra_args in GOWIN_OPTIONAL_CASES:
        output_dir = args.output_dir / f"{target}-optional"
        result = run_target(target, output_dir, extra_args=extra_args)
        if result.returncode:
            failures.append((f"{target} {extra_args}", result.stdout))
            print(f"FAIL {target} {extra_args}")
        else:
            print(f"PASS {target} {extra_args}")

    if failures:
        print("")
        for target, output in failures:
            print(f"--- {target} ---")
            print(output[-4000:])
        return 1

    print("")
    print(f"All {len(GOWIN_TARGETS)} Gowin targets and {len(GOWIN_OPTIONAL_CASES)} optional cases built successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
