#!/usr/bin/env python3

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TARGETS_DIR = ROOT / "litex_boards" / "targets"
PLATFORMS_DIR = ROOT / "litex_boards" / "platforms"
KNOWN_ISSUES_PATH = ROOT / ".github" / "scripts" / "board_consistency_known_issues.txt"

COMMON_OPTION_DEFAULTS = {
    "--eth-ip": '"192.168.1.50"',
    "--remote-ip": '"192.168.1.100"',
}

COMMON_ACTION_OPTIONS = {
    "--with-ethernet",
    "--with-etherbone",
    "--with-sdcard",
    "--with-spi-sdcard",
    "--with-spi-flash",
    "--eth-dynamic-ip",
}


@dataclass(frozen=True)
class OptionInfo:
    path: Path
    line: int
    names: tuple[str, ...]
    dest: str | None
    action: str | None
    default: str | None
    default_value: object
    help: str | None


def _expr_text(node: ast.AST) -> str:
    try:
        return ast.unparse(node)
    except Exception:
        return "<unknown>"


def _string_value(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _literal_value(node: ast.AST | None) -> object:
    if node is None:
        return None
    try:
        return ast.literal_eval(node)
    except Exception:
        return None


def _keyword(call: ast.Call, name: str) -> ast.AST | None:
    for kw in call.keywords:
        if kw.arg == name:
            return kw.value
    return None


def _call_name(node: ast.Call) -> str | None:
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    if isinstance(node.func, ast.Name):
        return node.func.id
    return None


def collect_options(path: Path) -> list[OptionInfo]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    options = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if _call_name(node) not in {"add_target_argument", "add_argument"}:
            continue
        names = []
        for arg in node.args:
            value = _string_value(arg)
            if value is None:
                break
            if value.startswith("--"):
                names.append(value)
        if not names:
            continue
        action = _string_value(_keyword(node, "action"))
        help_text = _string_value(_keyword(node, "help"))
        default_node = _keyword(node, "default")
        options.append(OptionInfo(
            path=path,
            line=node.lineno,
            names=tuple(names),
            dest=_string_value(_keyword(node, "dest")),
            action=action,
            default=_expr_text(default_node) if default_node is not None else None,
            default_value=_literal_value(default_node),
            help=help_text,
        ))
    return options


def collect_platform_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom):
            continue
        if node.module == "litex_boards.platforms":
            imports.update(alias.name for alias in node.names)
        elif node.module is not None and node.module.startswith("litex_boards.platforms."):
            imports.add(node.module.removeprefix("litex_boards.platforms."))
    return imports


def target_uses_litex_parser(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == "LiteXArgumentParser":
            return True
    return False


def audit_target(path: Path) -> list[str]:
    issues: list[str] = []
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        rel = path
    if not target_uses_litex_parser(path):
        issues.append(f"{rel}: target should use LiteXArgumentParser")

    imports = collect_platform_imports(path)
    if path.stem != "simple" and not imports:
        issues.append(f"{rel}: no litex_boards.platforms import found")

    options = collect_options(path)
    by_name = {name: option for option in options for name in option.names}

    for name, expected_default in COMMON_OPTION_DEFAULTS.items():
        option = by_name.get(name)
        if (
            option is not None
            and option.default_value is not None
            and option.default_value != expected_default.strip('"')
        ):
            issues.append(
                f"{rel}:{option.line}: {name} default is {option.default}, expected {expected_default}"
            )

    for name in COMMON_ACTION_OPTIONS:
        option = by_name.get(name)
        if option is not None and option.action not in {"store_true", None}:
            issues.append(
                f"{rel}:{option.line}: {name} should normally be a store_true option"
            )

    if "--local-ip" in by_name and "--eth-ip" not in by_name:
        option = by_name["--local-ip"]
        issues.append(f"{rel}:{option.line}: keep --eth-ip when adding --local-ip compatibility")

    if "--with-etherbone" in by_name and "--eth-dynamic-ip" in by_name:
        text = path.read_text(encoding="utf-8")
        if "with_etherbone and args.eth_dynamic_ip" not in text and "add_mutually_exclusive_group" not in text:
            issues.append(
                f"{rel}: document or enforce --with-etherbone/--eth-dynamic-ip interaction"
            )

    return issues


def collect_issues(targets_dir: Path = TARGETS_DIR) -> list[str]:
    issues: list[str] = []
    for path in sorted(targets_dir.glob("*.py")):
        if path.name == "__init__.py":
            continue
        issues.extend(audit_target(path))
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit LiteX-Boards target/platform consistency")
    parser.add_argument("--check", action="store_true", help="Fail when current issues differ from the known baseline")
    parser.add_argument("--strict", action="store_true", help="Return non-zero when audit issues are found")
    parser.add_argument("--write-known", action="store_true", help="Refresh the known-issues baseline")
    args = parser.parse_args()

    issues = collect_issues()
    rendered = "\n".join(issues) + ("\n" if issues else "")

    if args.write_known:
        KNOWN_ISSUES_PATH.write_text(rendered, encoding="utf-8")
        return 0

    if args.check:
        expected = KNOWN_ISSUES_PATH.read_text(encoding="utf-8") if KNOWN_ISSUES_PATH.exists() else ""
        if rendered == expected:
            return 0
        print("Board consistency audit differs from known baseline.")
        if rendered:
            print(rendered, end="")
        return 1

    if issues:
        print(rendered, end="")
    else:
        print("No board consistency issues found.")
    return 1 if args.strict and issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
