#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
uv run pytest -q
uv run pytest -m integration -q
