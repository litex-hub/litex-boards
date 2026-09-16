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


def run_target(target: str, output_dir: Path) -> subprocess.CompletedProcess:
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
    ]
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

    if failures:
        print("")
        for target, output in failures:
            print(f"--- {target} ---")
            print(output[-4000:])
        return 1

    print("")
    print(f"All {len(GOWIN_TARGETS)} Gowin targets built successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
