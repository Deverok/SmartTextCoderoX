"""Schema positive/negative cases — ACC-SCHEMA / MS0 T-002."""

from __future__ import annotations

from pathlib import Path

import pytest
from stcx_contracts.errors import StcxError
from stcx_contracts.schema_validate import SCHEMA_NAMES, SchemaValidator

ZERO_HASH = "0" * 64


def _minimal_codebook() -> dict:
    return {
        "meta": {
            "schema_version": "1.0",
            "codebook_version": "v1",
            "title": "t",
            "locale": "zh-CN",
            "created_at": "2026-10-25T00:00:00+08:00",
            "source_file": "x.txt",
            "source_sha256": ZERO_HASH,
            "codebook_hash": ZERO_HASH,
            "asterisk_semantics": "question_required",
        },
        "hierarchy": {
            "dimensions": [
                {
                    "dimension_id": "D_a",
                    "label": "A",
                    "order_index": 1,
                    "groups": [{"group_id": "G_a", "label": "g", "order_index": 1}],
                }
            ]
        },
        "categories": [
            {
                "field_id": "F_a",
                "label": "题",
                "dimension_id": "D_a",
                "group_id": "G_a",
                "hierarchy_path": ["A", "g", "题"],
                "type": "single_choice",
                "required": True,
                "required_marker_option": "O_1",
                "ai_coded": False,
                "prompt": None,
                "min_selections": None,
                "max_selections": None,
                "show_if": None,
                "order_index": 1,
                "options": [
                    {"value_id": "O_1", "value": "一", "order_index": 1},
                    {"value_id": "O_2", "value": "二", "order_index": 2},
                ],
            }
        ],
    }


def _minimal_sample() -> dict:
    return {
        "sample_id": "S0001",
        "metadata": {"来源": "x"},
        "text": "hello",
        "source": {"type": "text", "file": "a.txt", "sha256": ZERO_HASH},
        "flags": [],
    }


def _minimal_codes() -> dict:
    return {
        "unit_id": "S0001",
        "sample_id": "S0001",
        "field_id": "F_a",
        "coder_id": "keyword:v1",
        "values": ["O_1"],
        "provenance": {
            "run_id": "r1",
            "model": None,
            "model_version": None,
            "prompt_hash": None,
            "codebook_hash": ZERO_HASH,
            "temperature": None,
            "ts": "2026-10-25T00:00:00+08:00",
            "tokens": None,
            "invocation_id": "inv1",
        },
        "hierarchy_path": ["A", "g", "题"],
        "flags": [],
        "layer": "L0",
        "evidence_source": "keyword_span",
    }


def _minimal_manifest() -> dict:
    return {
        "step": "ST01",
        "run_id": "r1",
        "started_at": "2026-10-25T00:00:00+08:00",
        "finished_at": "2026-10-25T00:00:01+08:00",
        "inputs": [{"path": "a", "sha256": ZERO_HASH}],
        "outputs": [{"path": "b", "sha256": ZERO_HASH}],
        "config_hash": "x",
        "prompt_hash": None,
        "codebook_hash": ZERO_HASH,
        "code_version": "git:deadbee",
        "engine": "deterministic",
        "model": None,
        "model_version": None,
        "temperature": None,
        "seed": 42,
        "stats": {},
        "cost": {"currency": "CNY", "amount": 0, "estimated": True},
        "resumable": True,
        "notes": [],
    }


def _minimal_audit() -> dict:
    return {
        "audit_id": "A000001",
        "run_id": "r1",
        "unit_id": "S0001",
        "field_id": "F_a",
        "kind": "review",
        "before": ["O_1"],
        "after": ["O_2"],
        "method": "B1",
        "rule_ref": "rule:x",
        "operator": "human:tester",
        "ts": "2026-10-25T00:00:00+08:00",
    }


def _minimal_config() -> dict:
    return {
        "llm": {},
        "reliability": {},
        "distribution": {},
        "words": {},
        "palette": {},
        "naming": {},
        "pipeline": {},
        "budget": {},
        "offline_mode": True,
    }


POSITIVES = {
    "codebook": _minimal_codebook,
    "sample": _minimal_sample,
    "codes": _minimal_codes,
    "config": _minimal_config,
    "manifest": _minimal_manifest,
    "audit": _minimal_audit,
}


@pytest.mark.parametrize("name", SCHEMA_NAMES)
def test_ACC_SCHEMA_01_positive(name: str, schema_dir: Path) -> None:
    assert (schema_dir / f"{name}.schema.json").is_file()
    SchemaValidator(name, schema_dir=schema_dir).validate(POSITIVES[name]())


@pytest.mark.parametrize("name", SCHEMA_NAMES)
def test_ACC_SCHEMA_02_negative_missing_required(name: str, schema_dir: Path) -> None:
    with pytest.raises(StcxError) as ei:
        SchemaValidator(name, schema_dir=schema_dir).validate({})
    assert ei.value.code == "DATA-103"
