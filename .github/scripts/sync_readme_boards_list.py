#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path


README_PATH = Path("README.md")
TARGETS_DIR = Path("litex_boards/targets")
HEADER_MARKER = "[> Boards list"
SEPARATOR_LINE = "---------------"


def collect_targets() -> list[str]:
    targets = [
        path.stem
        for path in TARGETS_DIR.glob("*.py")
        if path.stem != "__init__"
    ]
    return sorted(set(targets))


def render_list(targets: list[str]) -> str:
    lines = []
    for index, target in enumerate(targets):
        branch = "└──" if index == len(targets) - 1 else "├──"
        lines.append(f"    {branch} {target}")
    return "\n".join(lines)


def update_readme(readme_text: str, generated_list: str) -> str:
    marker = f"{HEADER_MARKER}\n{SEPARATOR_LINE}\n"
    start = readme_text.find(marker)
    if start == -1:
        raise ValueError("Could not locate the boards list header in README.md")
    prefix = readme_text[: start + len(marker)]
    return prefix + generated_list + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync README board list from target modules")
    parser.add_argument("--check", action="store_true", help="Exit non-zero if README.md is out of date")
    parser.add_argument("--write", action="store_true", help="Write updated README.md")
    args = parser.parse_args()

    readme_text = README_PATH.read_text(encoding="utf-8")
    generated_list = render_list(collect_targets())
    updated = update_readme(readme_text, generated_list)

    if args.check:
        return 0 if updated == readme_text else 1

    if args.write or not args.check:
        README_PATH.write_text(updated, encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
