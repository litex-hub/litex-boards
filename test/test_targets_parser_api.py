from pathlib import Path


def test_targets_use_litex_argument_parser():
    targets_dir = Path(__file__).resolve().parent.parent / "litex_boards" / "targets"
    offenders = []
    for path in sorted(targets_dir.glob("*.py")):
        if path.name == "__init__.py":
            continue
        text = path.read_text(encoding="utf-8")
        if "argparse.ArgumentParser(" in text:
            offenders.append(path)

    assert not offenders, "Targets using argparse.ArgumentParser: " + ", ".join(str(p) for p in offenders)
