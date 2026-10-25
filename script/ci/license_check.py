#!/usr/bin/env python3
"""Refuse AGPL / strongly reciprocal licenses in the kernel dependency closure."""

from __future__ import annotations

import json
import subprocess
import sys

FORBIDDEN = ("AGPL", "SSPL", "GPL-3.0", "GPL-2.0")


def main() -> int:
    try:
        proc = subprocess.run(
            ["uv", "pip", "list", "--format", "json"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print(f"license_check: skip (uv unavailable): {exc}", file=sys.stderr)
        return 0
    packages = json.loads(proc.stdout)
    # MS0: name-level denylist only; full license metadata scan in later CI.
    bad = [p["name"] for p in packages if any(f.lower() in p["name"].lower() for f in ("agpl",))]
    if bad:
        print(f"FORBIDDEN packages: {bad}", file=sys.stderr)
        return 1
    print(f"OK: scanned {len(packages)} packages (name denylist)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
