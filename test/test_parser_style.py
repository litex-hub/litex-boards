import subprocess
import sys
from pathlib import Path


def test_target_parser_style():
    script = Path(__file__).resolve().parent.parent / ".github/scripts/check_target_parser_style.py"
    result = subprocess.run([sys.executable, str(script)], check=False)
    assert result.returncode == 0
