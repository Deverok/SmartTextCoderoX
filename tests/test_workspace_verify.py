"""Workspace layout verification — ACC-WS / T-001."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "script" / "maintenance" / "verify_workspace.py"


def test_ACC_WS_01_verify_workspace_ok(repo_root: Path) -> None:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(repo_root)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr


def test_ACC_WS_02_detects_missing_dir(repo_root: Path, tmp_path: Path) -> None:
    # Copy minimal static markers into temp broken tree
    broken = tmp_path / "broken"
    broken.mkdir()
    (broken / "AGENTS.md").write_text("x", encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(broken)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode != 0
    assert "MISSING_DIR" in proc.stderr


def test_ACC_WS_03_expect_broken_flag(repo_root: Path, tmp_path: Path) -> None:
    broken = tmp_path / "broken2"
    broken.mkdir()
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(broken), "--expect-broken"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
