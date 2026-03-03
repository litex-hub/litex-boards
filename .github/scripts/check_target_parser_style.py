#!/usr/bin/env python3

from __future__ import annotations

import ast
from pathlib import Path


TARGETS_DIR = Path("litex_boards/targets")


def _call_name(node: ast.Call) -> str | None:
    func = node.func
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _first_string_arg(node: ast.Call) -> str | None:
    if not node.args:
        return None
    arg0 = node.args[0]
    if isinstance(arg0, ast.Constant) and isinstance(arg0.value, str):
        return arg0.value
    return None


def _keyword_positions(node: ast.Call) -> dict[str, int]:
    return {kw.arg: i for i, kw in enumerate(node.keywords) if kw.arg is not None}


def _collect_group_defs(tree: ast.AST) -> dict[str, tuple[int, int]]:
    groups: dict[str, tuple[int, int]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        value = node.value
        if not isinstance(target, ast.Name) or not isinstance(value, ast.Call):
            continue
        if _call_name(value) != "add_mutually_exclusive_group":
            continue
        groups[target.id] = (value.lineno, 0)
    return groups


def _count_group_members(tree: ast.AST, groups: dict[str, tuple[int, int]]) -> dict[str, tuple[int, int]]:
    counts = dict(groups)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if _call_name(node) != "add_argument":
            continue
        if not isinstance(node.func, ast.Attribute):
            continue
        owner = node.func.value
        if not isinstance(owner, ast.Name) or owner.id not in counts:
            continue
        lineno, count = counts[owner.id]
        counts[owner.id] = (lineno, count + 1)
    return counts


def check_target(path: Path) -> list[str]:
    issues: list[str] = []
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        call_name = _call_name(node)
        if call_name not in {"add_target_argument", "add_argument"}:
            continue

        option = _first_string_arg(node)
        if option is None or not option.startswith("--"):
            continue

        kw_pos = _keyword_positions(node)
        if "choices" in kw_pos and "help" in kw_pos and kw_pos["choices"] > kw_pos["help"]:
            issues.append(
                f"{path}:{node.lineno}: keep keyword order as choices=... before help=... for {option}"
            )

    groups = _collect_group_defs(tree)
    groups = _count_group_members(tree, groups)
    for group_name in ("sdopts", "ethopts"):
        if group_name not in groups:
            continue
        lineno, count = groups[group_name]
        if count == 0:
            issues.append(f"{path}:{lineno}: remove empty mutually-exclusive group '{group_name}'")
        if count == 1:
            issues.append(
                f"{path}:{lineno}: avoid single-entry mutually-exclusive group '{group_name}'"
            )

    return issues


def main() -> int:
    issues: list[str] = []
    for path in sorted(TARGETS_DIR.glob("*.py")):
        if path.name == "__init__.py":
            continue
        issues.extend(check_target(path))

    if issues:
        print("\n".join(issues))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
