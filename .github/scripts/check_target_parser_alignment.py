#!/usr/bin/env python3

from __future__ import annotations

import re
from pathlib import Path


TARGETS_DIR = Path("litex_boards/targets")

CALL_RE = re.compile(r"^(?P<indent>\s*)(?P<recv>(?:parser|\w+opts))\.add_(?:target_)?argument\(")
def _line_info(line: str):
    m = CALL_RE.match(line)
    if not m or "help=" not in line or ")" not in line:
        return None
    # Keep the checker strict on simple single-option lines only.
    if line.count('"--') != 1:
        return None
    return {
        "indent": len(m.group("indent")),
        "receiver": m.group("recv"),
        "sig": tuple(name for name in ("action=", "default=", "type=", "choices=") if name in line),
        "help_col": line.index("help="),
    }


def check_file(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    issues = []
    i = 0
    while i < len(lines):
        info = _line_info(lines[i])
        if info is None:
            i += 1
            continue

        block = [(i + 1, info)]
        j = i + 1
        while j < len(lines):
            nxt = _line_info(lines[j])
            if nxt is None:
                break
            if (
                nxt["receiver"] != info["receiver"]
                or nxt["indent"] != info["indent"]
                or nxt["sig"] != info["sig"]
            ):
                break
            block.append((j + 1, nxt))
            j += 1

        if len(block) >= 2:
            help_cols = {entry["help_col"] for _, entry in block}
            if len(help_cols) > 1:
                locs = ", ".join(str(lno) for lno, _ in block)
                issues.append(f"{path}:{block[0][0]}: help alignment mismatch in lines {locs}")

        i = j
    return issues


def main() -> int:
    issues = []
    for path in sorted(TARGETS_DIR.glob("*.py")):
        if path.name == "__init__.py":
            continue
        issues.extend(check_file(path))

    if issues:
        print("\n".join(issues))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
