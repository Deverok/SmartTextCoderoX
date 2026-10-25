"""Logging field shape — T-005."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from stcx_core.logging import REQUIRED_FIELDS, bind, get_logger


def test_ACC_LOG_01_jsonl_fields(tmp_path: Path) -> None:
    # Fresh logger name to avoid handler reuse across tests
    logger = get_logger(f"stcx.test.{tmp_path.name}", log_dir=tmp_path)
    logger.info(
        "hello",
        extra=bind(logger, run_id="r1", step="ST01", unit_id="S1", event="test", extra={"k": 1}),
    )
    for h in logger.handlers:
        h.flush()
    lines = (tmp_path / "app.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert lines
    payload = json.loads(lines[0])
    for field in REQUIRED_FIELDS:
        assert field in payload
    # tear down
    logging.getLogger(f"stcx.test.{tmp_path.name}").handlers.clear()
