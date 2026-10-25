"""Config load fail-fast — T-004."""

from __future__ import annotations

from pathlib import Path

import pytest
from stcx_contracts.errors import StcxError
from stcx_core.config import load_config


def test_ACC_CFG_01_load_v1_ok(repo_root: Path) -> None:
    cfg = load_config("v1", repo_root=repo_root)
    assert cfg["offline_mode"] is True
    assert "budget" in cfg
    assert "llm" in cfg


def test_ACC_CFG_02_missing_default_fails(repo_root: Path, tmp_path: Path) -> None:
    # Build a fake repo without defaults
    fake = tmp_path / "repo"
    (fake / "config" / "schema").mkdir(parents=True)
    (fake / "config" / "default").mkdir(parents=True)
    (fake / "AGENTS.md").write_text("x", encoding="utf-8")
    with pytest.raises(StcxError) as ei:
        load_config("v1", repo_root=fake, validate=False)
    assert ei.value.code == "CFG-001"


def test_ACC_CFG_03_illegal_workspace_name(repo_root: Path) -> None:
    with pytest.raises(StcxError) as ei:
        load_config("bad name!", repo_root=repo_root)
    assert ei.value.code == "RUN-203"
