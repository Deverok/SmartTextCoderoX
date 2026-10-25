#!/usr/bin/env python3
"""Verify workspace / repo layout integrity (spec §3.0 / §3.1).

Exit 0 on success; non-zero with human-readable issues on failure.
Detects: missing required dirs, unexpected write probe into static zone
when --probe-static-writable is set.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

STATIC_TOP = (
    "bin",
    "config",
    "docs",
    "lib",
    "models",
    "module",
    "prompt",
    "script",
    "src",
)
RUNTIME_TOP = ("cache", "data", "logs", "reports", "results", "temp")
CONFIG_SUB = ("default", "schema")
DOCS_SUB = ("user", "dev", "methodology", "api", "assets")
SCRIPT_SUB = ("dev", "ci", "maintenance", "dataset")
SRC_PACKAGES = (
    "stcx_contracts",
    "stcx_core",
    "stcx_steps",
    "stcx_agents",
    "stcx_analytics",
    "stcx_viz",
    "stcx_reporting",
    "stcx_app",
)


def _repo_root_from(start: Path) -> Path:
    cur = start.resolve()
    for p in (cur, *cur.parents):
        if (p / "pyproject.toml").exists() or (p / "AGENTS.md").exists():
            return p
    return cur


def verify(root: Path, *, probe_static_writable: bool = False) -> list[str]:
    issues: list[str] = []
    for name in (*STATIC_TOP, *RUNTIME_TOP):
        path = root / name
        if not path.is_dir():
            issues.append(f"MISSING_DIR: {name}/")

    for sub in CONFIG_SUB:
        if not (root / "config" / sub).is_dir():
            issues.append(f"MISSING_DIR: config/{sub}/")

    for sub in DOCS_SUB:
        if not (root / "docs" / sub).is_dir():
            issues.append(f"MISSING_DIR: docs/{sub}/")

    for sub in SCRIPT_SUB:
        if not (root / "script" / sub).is_dir():
            issues.append(f"MISSING_DIR: script/{sub}/")

    if not (root / "data" / "_example").is_dir():
        issues.append("MISSING_DIR: data/_example/")

    src = root / "src"
    if src.is_dir():
        for pkg in SRC_PACKAGES:
            if not (src / pkg).is_dir():
                issues.append(f"MISSING_PKG: src/{pkg}/")

    if probe_static_writable:
        probe = root / "config" / ".stcx_write_probe"
        try:
            probe.write_text("probe", encoding="utf-8")
            probe.unlink(missing_ok=True)
            issues.append(
                "STATIC_WRITABLE: config/ is writable at runtime — "
                "static zone must be read-only in production installs "
                "(ACC-WS-01)."
            )
        except OSError:
            pass

    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repository or install root (default: auto-detect).",
    )
    parser.add_argument(
        "--probe-static-writable",
        action="store_true",
        help="Fail if static zone directories are writable (install check).",
    )
    parser.add_argument(
        "--expect-broken",
        action="store_true",
        help="Invert exit code (for tests that deliberately break layout).",
    )
    args = parser.parse_args(argv)
    root = args.root or _repo_root_from(Path.cwd())
    issues = verify(root, probe_static_writable=args.probe_static_writable)
    if issues:
        for item in issues:
            print(item, file=sys.stderr)
        return 0 if args.expect_broken else 1
    print(f"OK: workspace layout at {root}")
    return 1 if args.expect_broken else 0


if __name__ == "__main__":
    raise SystemExit(main())
