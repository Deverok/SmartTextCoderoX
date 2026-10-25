# Local bootstrap for Windows (PowerShell)
$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
uv sync --group dev
uv run python script/dataset/make_fixture.py --out data/_example
uv run python script/maintenance/verify_workspace.py
Write-Host "Bootstrap OK"