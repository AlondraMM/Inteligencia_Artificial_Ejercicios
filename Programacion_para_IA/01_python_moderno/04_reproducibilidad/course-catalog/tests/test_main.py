"""Exercise the actual CLI from a directory outside the project."""

import json
import subprocess
import sys
from pathlib import Path

MAIN_SCRIPT = Path(__file__).resolve().parents[1] / "main.py"


def test_missing_catalog_has_error_exit_and_no_stdout(tmp_path: Path) -> None:
    missing_catalog = tmp_path / "missing.json"

    result = subprocess.run(
        [sys.executable, str(MAIN_SCRIPT), "python", "--catalog", str(missing_catalog)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )

    assert result.returncode == 1
    assert result.stdout == ""
    assert "Catalog search failed" in result.stderr
    assert "FileNotFoundError" in result.stderr
    assert str(missing_catalog) in result.stderr


def test_default_catalog_works_outside_project(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(MAIN_SCRIPT), " PYTHON "],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )

    assert result.returncode == 0
    courses = json.loads(result.stdout)
    assert [course["code"] for course in courses] == ["PY01", "PY02"]
