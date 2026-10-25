"""Unified tool return envelope (spec §16.1)."""

from __future__ import annotations

from typing import Any, TypedDict


class ToolEnvelope(TypedDict):
    status: str
    data: dict[str, Any]
    warnings: list[dict[str, Any]]
    errors: list[dict[str, Any]]
    metrics: dict[str, Any]
    artifacts: list[str]


def tool_ok(
    data: dict[str, Any] | None = None,
    *,
    warnings: list[dict[str, Any]] | None = None,
    metrics: dict[str, Any] | None = None,
    artifacts: list[str] | None = None,
) -> ToolEnvelope:
    return {
        "status": "ok" if not warnings else "warning",
        "data": data or {},
        "warnings": warnings or [],
        "errors": [],
        "metrics": metrics or {},
        "artifacts": artifacts or [],
    }


def tool_error(
    errors: list[dict[str, Any]],
    *,
    data: dict[str, Any] | None = None,
    warnings: list[dict[str, Any]] | None = None,
    metrics: dict[str, Any] | None = None,
    artifacts: list[str] | None = None,
) -> ToolEnvelope:
    return {
        "status": "error",
        "data": data or {},
        "warnings": warnings or [],
        "errors": errors,
        "metrics": metrics or {},
        "artifacts": artifacts or [],
    }
