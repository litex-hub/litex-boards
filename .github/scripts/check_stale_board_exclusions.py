#!/usr/bin/env python3

from __future__ import annotations

import argparse
import ast
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEST_TARGETS_PATH = ROOT / "test" / "test_targets.py"

SKIPPED_CATEGORIES = {
    "external_toolchain",
    "generic_target",
    "not_real_platform",
}


@dataclass(frozen=True)
class Probe:
    kind: str
    name: str
    category: str
    reason: str
    cmd: tuple[str, ...]


@dataclass(frozen=True)
class ProbeResult:
    probe: Probe
    returncode: int
    output: str

    @property
    def stale(self) -> bool:
        return self.returncode == 0


def collect_exclusion_metadata(path: Path = TEST_TARGETS_PATH):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    values = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in {
                "EXCLUSION_CATEGORIES",
                "PLATFORM_EXCLUSIONS",
                "TARGET_EXCLUSIONS",
            }:
                values[target.id] = ast.literal_eval(node.value)
    return values


def is_probe_eligible(record: dict[str, str]) -> bool:
    return record["category"] not in SKIPPED_CATEGORIES


def collect_probes(output_dir: Path) -> list[Probe]:
    metadata = collect_exclusion_metadata()
    probes = []

    for name, record in sorted(metadata["TARGET_EXCLUSIONS"].items()):
        if not is_probe_eligible(record):
            continue
        probes.append(Probe(
            kind     = "target",
            name     = name,
            category = record["category"],
            reason   = record["reason"],
            cmd      = (
                sys.executable,
                "-m", f"litex_boards.targets.{name}",
                "--cpu-type=vexriscv",
                "--cpu-variant=minimal",
                "--uart-name=stub",
                "--build",
                "--no-compile",
                "--output-dir", str(output_dir / "targets" / name),
            ),
        ))

    for name, record in sorted(metadata["PLATFORM_EXCLUSIONS"].items()):
        if not is_probe_eligible(record):
            continue
        probes.append(Probe(
            kind     = "platform",
            name     = name,
            category = record["category"],
            reason   = record["reason"],
            cmd      = (
                sys.executable,
                "-m", "litex_boards.targets.simple",
                f"litex_boards.platforms.{name}",
                "--build",
                "--no-compile",
                "--uart-name=stub",
                "--output-dir", str(output_dir / "platforms" / name),
            ),
        ))

    return probes


def run_probe(probe: Probe, timeout: int) -> ProbeResult:
    result = subprocess.run(
        probe.cmd,
        stdout  = subprocess.PIPE,
        stderr  = subprocess.STDOUT,
        text    = True,
        timeout = timeout,
    )
    return ProbeResult(probe=probe, returncode=result.returncode, output=result.stdout)


def summarize_failure(result: ProbeResult) -> str:
    lines = [line for line in result.output.splitlines() if line.strip()]
    return " | ".join(lines[-4:])


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect stale LiteX-Boards build exclusions")
    parser.add_argument("--check", action="store_true", help="Exit non-zero when an exclusion now passes")
    parser.add_argument("--timeout", type=int, default=120, help="Timeout per probe in seconds")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/tmp/litex_boards_stale_exclusion_probe"),
        help="Directory used for temporary no-compile build outputs",
    )
    args = parser.parse_args()

    shutil.rmtree(args.output_dir, ignore_errors=True)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    stale = []
    for probe in collect_probes(args.output_dir):
        result = run_probe(probe, args.timeout)
        if result.stale:
            stale.append(probe)
            print(f"STALE {probe.kind} exclusion: {probe.name} ({probe.reason})")
        elif not args.check:
            summary = summarize_failure(result)
            print(f"kept {probe.kind} exclusion: {probe.name} ({probe.category}) {summary}")

    if stale:
        if args.check:
            print("")
            print("Remove the stale exclusions above or move them to a more specific gated category.")
        return 1 if args.check else 0

    print("No stale default build exclusions found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
