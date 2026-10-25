"""Sample TXT ↔ JSON roundtrip (spec §2.4.1) — MS0 minimal."""

from __future__ import annotations

import hashlib
import re
from typing import Any

from stcx_contracts.errors import ErrorCode, StcxError

SECTION_RE = re.compile(r"^［(?P<name>[^］]+)］\s*$")
UNENCODED = "<未编码>"


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_sample_txt(text: str, *, source_file: str = "sample.txt") -> dict[str, Any]:
    raw = text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    lines = raw.split("\n")
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in lines:
        m = SECTION_RE.match(line.strip())
        if m:
            current = m.group("name")
            sections.setdefault(current, [])
            continue
        if current is None:
            if not line.strip() or line.strip().startswith("#"):
                continue
            raise StcxError(
                ErrorCode.DATA_106,
                detail="样本 TXT 在首个段标记前有游离内容",
                loc={"file": source_file},
            )
        sections[current].append(line)

    if "元数据" not in sections or "正文" not in sections:
        raise StcxError(
            ErrorCode.DATA_106,
            detail="缺少［元数据］或［正文］段",
            loc={"file": source_file, "sections": list(sections)},
        )

    metadata: dict[str, str] = {}
    sample_id = None
    for line in sections["元数据"]:
        if not line.strip():
            continue
        if "：" in line:
            k, _, v = line.partition("：")
        elif ":" in line:
            k, _, v = line.partition(":")
        else:
            continue
        key, val = k.strip(), v.strip()
        if key in {"样本ID", "sample_id"}:
            sample_id = val
        else:
            metadata[key] = val

    if not sample_id:
        raise StcxError(
            ErrorCode.DATA_106,
            detail="元数据缺少样本ID",
            loc={"file": source_file},
        )

    body = "\n".join(sections["正文"]).strip("\n")
    return {
        "sample_id": sample_id,
        "metadata": metadata,
        "text": body,
        "source": {
            "type": "text",
            "file": source_file,
            "sha256": _sha256_bytes(raw.encode("utf-8")),
        },
        "flags": [],
    }


def render_sample_txt(sample: dict[str, Any]) -> str:
    lines = ["［元数据］", f"样本ID：{sample['sample_id']}"]
    for k, v in (sample.get("metadata") or {}).items():
        lines.append(f"{k}：{v}")
    lines.append("［正文］")
    lines.append(sample.get("text") or "")
    return "\n".join(lines).rstrip() + "\n"
