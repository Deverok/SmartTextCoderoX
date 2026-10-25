"""CLI skeleton — T-006."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _run(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def test_ACC_CLI_01_stcx_step_help(repo_root: Path) -> None:
    # Prefer console script via python -c after install; fallback to module path
    proc = subprocess.run(
        [sys.executable, "-c", "from stcx_app.cli_step import main; main(['--help'])"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    assert "stcx-step" in proc.stdout or "workspace" in proc.stdout


def test_ACC_CLI_02_stcx_tool_help(repo_root: Path) -> None:
    proc = subprocess.run(
        [sys.executable, "-c", "from stcx_app.cli_tool import main; main(['--help'])"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0


def test_ACC_CLI_03_step_dry_run(repo_root: Path) -> None:
    proc = subprocess.run(
        [
            sys.executable,
            "-c",
            "from stcx_app.cli_step import main; main(['ST01','--workspace','v1','--dry-run'])",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert "dry_run" in proc.stdout


def test_ACC_CLI_04_missing_input_guidance(repo_root: Path) -> None:
    proc = subprocess.run(
        [
            sys.executable,
            "-c",
            "from stcx_app.cli_step import main; main(['ST06','--workspace','v1'])",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode != 0
    assert "RUN-201" in proc.stderr
    assert "input_stage" in proc.stderr
