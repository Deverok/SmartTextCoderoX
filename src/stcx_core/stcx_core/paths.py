"""Workspace / runtime path resolution (spec §3.0)."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

from stcx_contracts.errors import ErrorCode, StcxError

VERSION_RE = re.compile(r"^[A-Za-z0-9_\-\u4e00-\u9fa5]{1,64}$")
ENV_WORKSPACES_ROOT = "STCX_WORKSPACES_ROOT"

RUNTIME_TOP = ("cache", "data", "logs", "reports", "results", "temp")


def find_repo_root(start: Path | None = None) -> Path:
    cur = (start or Path.cwd()).resolve()
    for p in (cur, *cur.parents):
        if (p / "AGENTS.md").exists() and (p / "config").is_dir():
            return p
        if (p / "pyproject.toml").exists() and (p / "config" / "schema").is_dir():
            return p
    raise StcxError(
        ErrorCode.CFG_001,
        detail="无法定位仓库根（缺少 AGENTS.md / config）",
        next_action="在仓库根目录运行命令",
    )


def resolve_workspaces_root(repo_root: Path | None = None) -> Path:
    """Runtime zone root. Env STCX_WORKSPACES_ROOT overrides; default = repo root."""
    root = repo_root or find_repo_root()
    env = os.environ.get(ENV_WORKSPACES_ROOT)
    if env:
        return Path(env).expanduser().resolve()
    return root.resolve()


def validate_workspace_name(version: str) -> str:
    if not VERSION_RE.match(version):
        raise StcxError(
            ErrorCode.RUN_203,
            detail=f"非法工作区名: {version!r}",
        )
    return version


@dataclass(frozen=True, slots=True)
class WorkspacePaths:
    """Resolved paths for one workspace {version}."""

    version: str
    repo_root: Path
    workspaces_root: Path

    @classmethod
    def create(cls, version: str, *, repo_root: Path | None = None) -> WorkspacePaths:
        v = validate_workspace_name(version)
        repo = repo_root or find_repo_root()
        ws = resolve_workspaces_root(repo)
        return cls(version=v, repo_root=repo, workspaces_root=ws)

    @property
    def config_dir(self) -> Path:
        return self.repo_root / "config" / self.version

    @property
    def schema_dir(self) -> Path:
        return self.repo_root / "config" / "schema"

    @property
    def default_config_dir(self) -> Path:
        return self.repo_root / "config" / "default"

    def runtime(self, top: str) -> Path:
        if top not in RUNTIME_TOP:
            raise StcxError(
                ErrorCode.CFG_001,
                detail=f"非法运行区顶层: {top}",
                next_action=f"使用其一: {', '.join(RUNTIME_TOP)}",
            )
        return self.workspaces_root / top / self.version

    @property
    def data(self) -> Path:
        return self.runtime("data")

    @property
    def logs(self) -> Path:
        return self.runtime("logs")

    @property
    def results(self) -> Path:
        return self.runtime("results")

    @property
    def reports(self) -> Path:
        return self.runtime("reports")

    @property
    def cache(self) -> Path:
        return self.runtime("cache")

    @property
    def temp(self) -> Path:
        return self.workspaces_root / "temp"

    def input_stage(self, step_id: str) -> Path:
        return self.data / "input_stage" / step_id

    def codebook_txt(self) -> Path:
        return self.config_dir / "编码规则.txt"
