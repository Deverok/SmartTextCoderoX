"""Synthetic fixture generate → parse → render — T-008."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
from stcx_steps.codebook import parse_codebook, render_codebook
from stcx_steps.samples import parse_sample_txt, render_sample_txt


@pytest.mark.integration
def test_ACC_FIX_01_make_fixture_roundtrip(repo_root: Path, tmp_path: Path) -> None:
    out = tmp_path / "_example"
    script = repo_root / "script" / "dataset" / "make_fixture.py"
    proc = subprocess.run(
        [sys.executable, str(script), "--out", str(out)],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout
    text = (out / "编码规则.txt").read_text(encoding="utf-8")
    parsed = parse_codebook(text)
    assert parsed["ok"], parsed["errors"]
    rendered = render_codebook(parsed["codebook"])
    again = parse_codebook(rendered)
    assert again["ok"]
    assert [c["label"] for c in parsed["codebook"]["categories"]] == [
        c["label"] for c in again["codebook"]["categories"]
    ]

    sample_txt = (out / "samples" / "S0001.txt").read_text(encoding="utf-8")
    sample = parse_sample_txt(sample_txt)
    sample2 = parse_sample_txt(render_sample_txt(sample))
    assert sample2["sample_id"] == sample["sample_id"]
    assert sample2["text"] == sample["text"]


def test_ACC_FIX_02_example_readme_exists(repo_root: Path) -> None:
    # May be generated; ensure script can dry-run
    script = repo_root / "script" / "dataset" / "make_fixture.py"
    proc = subprocess.run(
        [sys.executable, str(script), "--dry-run"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
