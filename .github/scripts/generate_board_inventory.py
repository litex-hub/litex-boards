#!/usr/bin/env python3

from __future__ import annotations

import argparse
import ast
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TARGETS_DIR = ROOT / "litex_boards" / "targets"
PLATFORMS_DIR = ROOT / "litex_boards" / "platforms"
INVENTORY_PATH = ROOT / "docs" / "boards_inventory.md"
TARGET_TESTS_PATH = ROOT / "test" / "test_targets.py"

FEATURE_OPTIONS = {
    "--with-ethernet": "Ethernet",
    "--with-etherbone": "Etherbone",
    "--with-sdcard": "SDCard",
    "--with-spi-sdcard": "SPI SDCard",
    "--with-spi-flash": "SPI Flash",
    "--with-pcie": "PCIe",
    "--with-sata": "SATA",
    "--with-video-terminal": "Video Terminal",
    "--with-video-framebuffer": "Video Framebuffer",
    "--with-video-colorbars": "Video Colorbars",
    "--with-usb": "USB",
    "--with-usb-host": "USB Host",
}


@dataclass(frozen=True)
class BoardInfo:
    target: str
    platforms: tuple[str, ...]
    toolchains: tuple[str, ...]
    sys_clk_freq: str
    features: tuple[str, ...]
    target_test: str


def _expr_text(node: ast.AST | None) -> str:
    if node is None:
        return ""
    try:
        return ast.unparse(node)
    except Exception:
        return ""


def _string_value(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
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


def _option_names(call: ast.Call) -> tuple[str, ...]:
    names = []
    for arg in call.args:
        value = _string_value(arg)
        if value is None:
            break
        if value.startswith("--"):
            names.append(value)
    return tuple(names)


def collect_target_options(path: Path) -> dict[str, ast.Call]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    options: dict[str, ast.Call] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if _call_name(node) not in {"add_target_argument", "add_argument"}:
            continue
        for name in _option_names(node):
            options[name] = node
    return options


def collect_platform_imports(path: Path) -> tuple[str, ...]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    platforms: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "litex_boards.platforms":
            platforms.update(alias.name for alias in node.names)
        elif (
            isinstance(node, ast.ImportFrom)
            and node.module is not None
            and node.module.startswith("litex_boards.platforms.")
        ):
            platforms.add(node.module.removeprefix("litex_boards.platforms."))
    return tuple(sorted(platforms))


def collect_platform_toolchains(platforms: tuple[str, ...]) -> tuple[str, ...]:
    toolchains: set[str] = set()
    for platform in platforms:
        path = PLATFORMS_DIR / f"{platform}.py"
        if not path.exists():
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef) or node.name != "__init__":
                continue
            for arg, default in zip(reversed(node.args.args), reversed(node.args.defaults)):
                if arg.arg == "toolchain":
                    value = _string_value(default)
                    if value is not None:
                        toolchains.add(value)
    return tuple(sorted(toolchains))


def _collect_structured_target_exclusions(path: Path) -> dict[str, str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == "TARGET_EXCLUSIONS" for target in node.targets):
            continue
        value = ast.literal_eval(node.value)
        return {
            name: record["reason"]
            for name, record in value.items()
            if isinstance(record, dict) and "reason" in record
        }
    return {}


def _collect_legacy_target_exclusions(path: Path) -> dict[str, str]:
    exclusions: dict[str, str] = {}
    in_targets = False
    line_re = re.compile(r'^\s*"(?P<name>[^"]+)",\s*# Reason:\s*(?P<reason>.+?)\s*$')
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("excluded_targets"):
            in_targets = True
            continue
        if in_targets and line.strip() == "]":
            break
        if not in_targets:
            continue
        match = line_re.match(line)
        if match:
            exclusions[match.group("name")] = match.group("reason")
    return exclusions


def collect_target_test_exclusions(path: Path = TARGET_TESTS_PATH) -> dict[str, str]:
    return _collect_structured_target_exclusions(path) or _collect_legacy_target_exclusions(path)


def collect_board_info(target_path: Path, target_test_exclusions: dict[str, str] | None = None) -> BoardInfo:
    if target_test_exclusions is None:
        target_test_exclusions = collect_target_test_exclusions()
    options = collect_target_options(target_path)
    platforms = collect_platform_imports(target_path)
    sys_clk = "default"
    if "--sys-clk-freq" in options:
        sys_clk = _expr_text(_keyword(options["--sys-clk-freq"], "default")) or "default"
    features = tuple(label for option, label in FEATURE_OPTIONS.items() if option in options)
    return BoardInfo(
        target=target_path.stem,
        platforms=platforms,
        toolchains=collect_platform_toolchains(platforms),
        sys_clk_freq=sys_clk,
        features=features,
        target_test=target_test_exclusions.get(target_path.stem, "included"),
    )


def collect_inventory(targets_dir: Path = TARGETS_DIR) -> list[BoardInfo]:
    target_test_exclusions = collect_target_test_exclusions()
    return [
        collect_board_info(path, target_test_exclusions)
        for path in sorted(targets_dir.glob("*.py"))
        if path.name != "__init__.py"
    ]


def _cell(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "-"


def render_inventory(boards: list[BoardInfo]) -> str:
    lines = [
        "# LiteX-Boards Inventory",
        "",
        "Generated from target and platform modules. Refresh with:",
        "",
        "```sh",
        "python3 .github/scripts/generate_board_inventory.py --write",
        "```",
        "",
        "| Target | Platform module(s) | Toolchain(s) | Default sys clk | Common features | Target no-compile test |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for board in boards:
        lines.append(
            f"| `{board.target}` | {_cell(board.platforms)} | {_cell(board.toolchains)} | "
            f"`{board.sys_clk_freq}` | {_cell(board.features)} | {board.target_test} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate LiteX-Boards inventory documentation")
    parser.add_argument("--check", action="store_true", help="Exit non-zero if the inventory is out of date")
    parser.add_argument("--write", action="store_true", help="Write docs/boards_inventory.md")
    args = parser.parse_args()

    rendered = render_inventory(collect_inventory())
    if args.check:
        if not INVENTORY_PATH.exists():
            return 1
        return 0 if INVENTORY_PATH.read_text(encoding="utf-8") == rendered else 1

    if args.write or not args.check:
        INVENTORY_PATH.write_text(rendered, encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
