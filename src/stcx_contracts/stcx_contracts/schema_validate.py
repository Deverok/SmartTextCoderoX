"""JSON Schema load + validate helpers."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from stcx_contracts.errors import ErrorCode, StcxError

SCHEMA_NAMES = (
    "codebook",
    "sample",
    "codes",
    "config",
    "manifest",
    "audit",
)


def default_schema_dir() -> Path:
    """Resolve config/schema relative to repo root from this package location."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "config" / "schema"
        if candidate.is_dir():
            return candidate
    raise StcxError(
        ErrorCode.CFG_001,
        detail="找不到 config/schema 目录",
        next_action="在仓库根运行，或设置正确的安装布局",
    )


@lru_cache(maxsize=16)
def load_schema(name: str, schema_dir: str | None = None) -> dict[str, Any]:
    if name not in SCHEMA_NAMES:
        raise StcxError(
            ErrorCode.DATA_103,
            detail=f"未知 Schema 名: {name}",
            next_action=f"使用其一: {', '.join(SCHEMA_NAMES)}",
        )
    root = Path(schema_dir) if schema_dir else default_schema_dir()
    path = root / f"{name}.schema.json"
    if not path.is_file():
        raise StcxError(
            ErrorCode.CFG_001,
            detail=f"缺少 Schema 文件: {path}",
            next_action="确认 MS0 Schema 已落盘到 config/schema/",
        )
    data: Any = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise StcxError(
            ErrorCode.DATA_103,
            detail=f"Schema 根必须是 object: {path}",
        )
    return data


class SchemaValidator:
    def __init__(self, name: str, *, schema_dir: str | Path | None = None) -> None:
        self.name = name
        dir_s = str(schema_dir) if schema_dir else None
        self.schema = load_schema(name, dir_s)
        self._validator = Draft202012Validator(self.schema)

    def validate(self, instance: Any) -> None:
        errors = sorted(self._validator.iter_errors(instance), key=lambda e: list(e.path))
        if errors:
            first: ValidationError = errors[0]
            path = ".".join(str(p) for p in first.absolute_path) or "<root>"
            raise StcxError(
                ErrorCode.DATA_103,
                detail=f"{self.name} Schema 校验失败 @ {path}: {first.message}",
                loc={"schema": self.name, "path": path},
                next_action="对照 config/schema 修正字段后重试",
            )

    def is_valid(self, instance: Any) -> bool:
        result: bool = bool(self._validator.is_valid(instance))
        return result
