import importlib.util
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def load_script(name):
    path = ROOT / ".github" / "scripts" / name
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[path.stem] = module
    spec.loader.exec_module(module)
    return module


def load_test_targets():
    path = ROOT / "test" / "test_targets.py"
    spec = importlib.util.spec_from_file_location("test_targets_metadata", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["test_targets_metadata"] = module
    spec.loader.exec_module(module)
    return module


def test_board_inventory_is_current():
    script = ROOT / ".github" / "scripts" / "generate_board_inventory.py"
    result = subprocess.run([sys.executable, str(script), "--check"], check=False)
    assert result.returncode == 0


def test_board_audit_non_strict_is_report_only():
    script = ROOT / ".github" / "scripts" / "audit_board_consistency.py"
    result = subprocess.run([sys.executable, str(script)], check=False)
    assert result.returncode == 0


def test_board_audit_matches_known_baseline():
    script = ROOT / ".github" / "scripts" / "audit_board_consistency.py"
    result = subprocess.run([sys.executable, str(script), "--check"], check=False)
    assert result.returncode == 0


def test_stale_exclusion_checker_selects_default_build_probes():
    checker = load_script("check_stale_board_exclusions.py")
    assert checker.is_probe_eligible({"category": "missing_default_clock"})
    assert checker.is_probe_eligible({"category": "known_build_failure"})
    assert checker.is_probe_eligible({"category": "untested"})
    assert not checker.is_probe_eligible({"category": "external_toolchain"})
    assert not checker.is_probe_eligible({"category": "generic_target"})
    assert not checker.is_probe_eligible({"category": "not_real_platform"})


def test_stale_exclusion_checker_detects_passing_probe():
    checker = load_script("check_stale_board_exclusions.py")
    probe = checker.Probe(
        kind     = "target",
        name     = "demo",
        category = "known_build_failure",
        reason   = "Demo.",
        cmd      = (sys.executable, "-c", ""),
    )

    result = checker.run_probe(probe, timeout=10)
    assert result.stale


def test_board_audit_understands_platform_module_imports(tmp_path):
    audit = load_script("audit_board_consistency.py")
    target = tmp_path / "demo.py"
    target.write_text(
        """
from litex.build.parser import LiteXArgumentParser
from litex_boards.platforms.demo import Platform

def main():
    parser = LiteXArgumentParser(platform=Platform)
    parser.add_target_argument("--eth-ip", default="192.168.1.50")
""",
        encoding="utf-8",
    )

    assert audit.collect_platform_imports(target) == {"demo"}
    assert audit.audit_target(target) == []


def test_board_audit_flags_local_ip_without_eth_ip(tmp_path):
    audit = load_script("audit_board_consistency.py")
    target = tmp_path / "demo.py"
    target.write_text(
        """
from litex.build.parser import LiteXArgumentParser
from litex_boards.platforms import demo

def main():
    parser = LiteXArgumentParser(platform=demo.Platform)
    parser.add_target_argument("--local-ip", default="192.168.1.50")
""",
        encoding="utf-8",
    )

    issues = audit.audit_target(target)
    assert any("keep --eth-ip" in issue for issue in issues)


def test_board_inventory_extracts_common_metadata(tmp_path, monkeypatch):
    inventory = load_script("generate_board_inventory.py")
    platforms = tmp_path / "platforms"
    platforms.mkdir()
    (platforms / "demo.py").write_text(
        """
class Platform:
    def __init__(self, toolchain="trellis"):
        pass
""",
        encoding="utf-8",
    )
    monkeypatch.setattr(inventory, "PLATFORMS_DIR", platforms)

    target = tmp_path / "demo.py"
    target.write_text(
        """
from litex_boards.platforms.demo import Platform

def main():
    parser.add_target_argument("--sys-clk-freq", default=60e6, type=float)
    parser.add_target_argument("--with-ethernet", action="store_true")
    parser.add_target_argument("--with-sdcard", action="store_true")
""",
        encoding="utf-8",
    )

    board = inventory.collect_board_info(target, {"demo": "No default clock."})
    assert board.platforms == ("demo",)
    assert board.toolchains == ("trellis",)
    assert board.features == ("Ethernet", "SDCard")
    assert board.target_test == "No default clock."


def test_board_inventory_reads_target_exclusion_reasons(tmp_path):
    inventory = load_script("generate_board_inventory.py")
    tests = tmp_path / "test_targets.py"
    tests.write_text(
        '''
TARGET_EXCLUSIONS = {
    "demo": {
        "category": "missing_default_clock",
        "reason": "No default clock.",
    },
}
''',
        encoding="utf-8",
    )

    assert inventory.collect_target_test_exclusions(tests) == {"demo": "No default clock."}


def test_board_inventory_marks_external_toolchain_exclusions(tmp_path):
    inventory = load_script("generate_board_inventory.py")
    tests = tmp_path / "test_targets.py"
    tests.write_text(
        '''
TARGET_EXCLUSIONS = {
    "demo": {
        "category": "external_toolchain",
        "reason": "Require Efinity toolchain.",
    },
}
''',
        encoding="utf-8",
    )

    assert inventory.collect_target_test_exclusions(tests) == {
        "demo": "toolchain-gated: Require Efinity toolchain.",
    }


def test_target_exclusions_use_structured_metadata():
    targets = load_test_targets()
    for exclusions in [targets.PLATFORM_EXCLUSIONS, targets.TARGET_EXCLUSIONS]:
        for name, record in exclusions.items():
            assert name
            assert set(record) >= {"category", "reason"}
            assert record["category"] in targets.EXCLUSION_CATEGORIES
            assert record["reason"].endswith(".")
