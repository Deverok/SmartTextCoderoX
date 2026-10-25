"""Package dependency direction — T-003."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

FORBIDDEN = {
    "stcx_contracts": set(),
    "stcx_core": {
        "stcx_steps",
        "stcx_agents",
        "stcx_analytics",
        "stcx_viz",
        "stcx_reporting",
        "stcx_app",
    },
    "stcx_analytics": {"stcx_agents"},
}


def _imports_in(package_dir: Path) -> set[str]:
    found: set[str] = set()
    for py in package_dir.rglob("*.py"):
        tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    found.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                found.add(node.module.split(".")[0])
    return found


@pytest.mark.parametrize("pkg,forbidden", list(FORBIDDEN.items()))
def test_ACC_DEP_01_no_forbidden_imports(repo_root: Path, pkg: str, forbidden: set[str]) -> None:
    pkg_root = repo_root / "src" / pkg / pkg
    imports = _imports_in(pkg_root)
    bad = imports & forbidden
    assert not bad, f"{pkg} imports forbidden modules: {bad}"


def test_ACC_DEP_02_analytics_does_not_import_agents(repo_root: Path) -> None:
    imports = _imports_in(repo_root / "src" / "stcx_analytics" / "stcx_analytics")
    assert "stcx_agents" not in imports
