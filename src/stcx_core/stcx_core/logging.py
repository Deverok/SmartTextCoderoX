"""Structured JSONL + human-readable logging (spec code-structure §7)."""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REQUIRED_FIELDS = ("ts", "level", "run_id", "step", "unit_id", "event", "message", "extra")


class JsonlFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname.lower(),
            "run_id": getattr(record, "run_id", None),
            "step": getattr(record, "step", None),
            "unit_id": getattr(record, "unit_id", None),
            "event": getattr(record, "event", record.name),
            "message": record.getMessage(),
            "extra": getattr(record, "extra_data", {}),
        }
        return json.dumps(payload, ensure_ascii=False)


class HumanFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        run_id = getattr(record, "run_id", "-")
        step = getattr(record, "step", "-")
        event = getattr(record, "event", record.name)
        return f"{record.levelname} run={run_id} step={step} event={event} {record.getMessage()}"


def get_logger(
    name: str = "stcx",
    *,
    log_dir: Path | None = None,
    level: int = logging.INFO,
) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(level)
    logger.propagate = False

    human = logging.StreamHandler(sys.stderr)
    human.setFormatter(HumanFormatter())
    logger.addHandler(human)

    if log_dir is not None:
        log_dir.mkdir(parents=True, exist_ok=True)
        jsonl_path = log_dir / "app.jsonl"
        human_path = log_dir / "app.log"
        jh = logging.FileHandler(jsonl_path, encoding="utf-8")
        jh.setFormatter(JsonlFormatter())
        logger.addHandler(jh)
        hh = logging.FileHandler(human_path, encoding="utf-8")
        hh.setFormatter(HumanFormatter())
        logger.addHandler(hh)

    return logger


def bind(
    logger: logging.Logger,
    *,
    run_id: str | None = None,
    step: str | None = None,
    unit_id: str | None = None,
    event: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build ``extra`` kwargs for logger.log(..., extra=...)."""
    return {
        "run_id": run_id,
        "step": step,
        "unit_id": unit_id,
        "event": event or "event",
        "extra_data": extra or {},
    }
