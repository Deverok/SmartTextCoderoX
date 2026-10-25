"""Error catalog ↔ docs/dev/error-codes.md — T-005."""

from __future__ import annotations

import re
from pathlib import Path

from stcx_contracts.errors import ErrorCode, error_catalog


def test_ACC_ERR_01_catalog_matches_docs(repo_root: Path) -> None:
    docs = (repo_root / "docs" / "dev" / "error-codes.md").read_text(encoding="utf-8")
    catalog = error_catalog()
    for code in catalog:
        assert code in docs, f"{code} missing from error-codes.md"
    for code in ErrorCode:
        assert code.value in catalog, f"{code.value} missing from catalog"


def test_ACC_ERR_02_docs_codes_are_known(repo_root: Path) -> None:
    docs = (repo_root / "docs" / "dev" / "error-codes.md").read_text(encoding="utf-8")
    known = set(error_catalog())
    found = set(re.findall(r"\b(?:CB|DATA|TOOL|RUN|LLM|REL|REP|PKG|CFG)-\d{3}\b", docs))
    assert found <= known
