"""Config load + Schema validate + fail-fast (spec §2.7 / code-structure §4)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from stcx_contracts.errors import ErrorCode, StcxError
from stcx_contracts.schema_validate import SchemaValidator

from stcx_core.paths import WorkspacePaths, find_repo_root

REQUIRED_DEFAULT_FILES = (
    "app.json",
    "llm.yaml",
    "palette.json",
    "words.json",
    "distribution.json",
    "reliability.json",
    "report.json",
    "naming.json",
    "codebook.json",
)

MERGED_REQUIRED_KEYS = (
    "llm",
    "reliability",
    "distribution",
    "words",
    "palette",
    "naming",
    "pipeline",
    "budget",
    "offline_mode",
)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise StcxError(
            ErrorCode.DATA_103,
            detail=f"JSON 解析失败: {path}: {exc}",
            loc={"path": str(path)},
        ) from exc
    if not isinstance(data, dict):
        raise StcxError(
            ErrorCode.DATA_103,
            detail=f"配置根必须是 object: {path}",
            loc={"path": str(path)},
        )
    return data


def _read_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise StcxError(
            ErrorCode.DATA_103,
            detail=f"YAML 根必须是 object: {path}",
            loc={"path": str(path)},
        )
    return data


def _load_file(path: Path) -> dict[str, Any]:
    if path.suffix.lower() in {".yaml", ".yml"}:
        return _read_yaml(path)
    return _read_json(path)


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for key, value in overlay.items():
        if key in out and isinstance(out[key], dict) and isinstance(value, dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def load_defaults(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or find_repo_root()
    default_dir = root / "config" / "default"
    missing = [name for name in REQUIRED_DEFAULT_FILES if not (default_dir / name).is_file()]
    if missing:
        raise StcxError(
            ErrorCode.CFG_001,
            detail=f"缺少默认配置文件: {', '.join(missing)}",
            next_action="在 config/default/ 补齐缺失文件后重试",
            loc={"dir": str(default_dir), "missing": missing},
        )

    app = _load_file(default_dir / "app.json")
    llm = _load_file(default_dir / "llm.yaml")
    palette = _load_file(default_dir / "palette.json")
    words = _load_file(default_dir / "words.json")
    distribution = _load_file(default_dir / "distribution.json")
    reliability = _load_file(default_dir / "reliability.json")
    report = _load_file(default_dir / "report.json")
    naming = _load_file(default_dir / "naming.json")
    codebook = _load_file(default_dir / "codebook.json")

    budget = llm.get("budget")
    if not isinstance(budget, dict):
        raise StcxError(
            ErrorCode.CFG_001,
            detail="缺少配置项 llm.budget",
            next_action="在 config/default/llm.yaml 中声明 budget",
        )

    offline_mode = app.get("offline_mode")
    if not isinstance(offline_mode, bool):
        raise StcxError(
            ErrorCode.CFG_001,
            detail="缺少配置项 app.offline_mode（布尔）",
            next_action="在 config/default/app.json 中声明 offline_mode",
        )

    return {
        "app": app,
        "llm": llm,
        "palette": palette,
        "words": words,
        "distribution": distribution,
        "reliability": reliability,
        "report": report,
        "naming": naming,
        "codebook": codebook,
        "budget": budget,
        "offline_mode": offline_mode,
        "pipeline": {"schema_version": "1.0", "nodes": []},
    }


def load_config(
    workspace: str,
    *,
    repo_root: Path | None = None,
    validate: bool = True,
) -> dict[str, Any]:
    """Load default + version overlay. Fail-fast on missing required keys."""
    paths = WorkspacePaths.create(workspace, repo_root=repo_root)
    merged = load_defaults(paths.repo_root)

    version_dir = paths.config_dir
    if version_dir.is_dir():
        for name in ("distribution.json", "pipeline.yaml", "变量配置.json"):
            candidate = version_dir / name
            if not candidate.is_file():
                continue
            overlay = _load_file(candidate)
            key = {
                "distribution.json": "distribution",
                "pipeline.yaml": "pipeline",
                "变量配置.json": "variables",
            }[name]
            if key in merged and isinstance(merged[key], dict):
                merged[key] = _deep_merge(merged[key], overlay)
            else:
                merged[key] = overlay

    for key in MERGED_REQUIRED_KEYS:
        if key not in merged:
            raise StcxError(
                ErrorCode.CFG_001,
                detail=f"缺少必需配置项: {key}",
                next_action=f"在 config/default 或 config/{workspace} 中补齐 {key}",
                loc={"key": key, "workspace": workspace},
            )

    if validate:
        SchemaValidator("config", schema_dir=paths.schema_dir).validate(merged)
    return merged
