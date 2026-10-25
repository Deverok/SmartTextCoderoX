"""stcx-tool CLI skeleton (spec §16.1)."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from stcx_contracts.envelope import ToolEnvelope, tool_error, tool_ok
from stcx_contracts.errors import ErrorCode, StcxError
from stcx_core.paths import find_repo_root
from stcx_steps.codebook import parse_codebook, render_codebook, validate_codebook
from stcx_steps.samples import parse_sample_txt, render_sample_txt

ToolFn = Callable[..., ToolEnvelope]


def codebook_parse(text: str | None = None, file: str | None = None, **_: Any) -> ToolEnvelope:
    if file:
        path = Path(file)
        text = path.read_text(encoding="utf-8-sig")
        source = str(path)
    elif text is not None:
        source = "<stdin>"
    else:
        return tool_error([{"code": ErrorCode.DATA_102.value, "msg": "需要 --file 或 --text"}])
    result = parse_codebook(text, source_file=source)
    if not result["ok"]:
        return tool_error(
            result["errors"], data={"codebook": result["codebook"]}, warnings=result["warnings"]
        )
    return tool_ok(
        {"codebook": result["codebook"]},
        warnings=result["warnings"],
    )


def codebook_validate(file: str, **_: Any) -> ToolEnvelope:
    path = Path(file)
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    errs = validate_codebook(data)
    if errs:
        return tool_error(errs)
    return tool_ok({"valid": True})


def codebook_render(file: str, **_: Any) -> ToolEnvelope:
    path = Path(file)
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    txt = render_codebook(data)
    return tool_ok({"text": txt})


def samples_parse_txt(file: str, **_: Any) -> ToolEnvelope:
    path = Path(file)
    try:
        sample = parse_sample_txt(path.read_text(encoding="utf-8-sig"), source_file=str(path))
    except StcxError as exc:
        return tool_error([exc.as_dict()])
    return tool_ok({"sample": sample})


def samples_render_txt(file: str, **_: Any) -> ToolEnvelope:
    path = Path(file)
    sample = json.loads(path.read_text(encoding="utf-8-sig"))
    return tool_ok({"text": render_sample_txt(sample)})


def fs_hash(file: str, **_: Any) -> ToolEnvelope:
    import hashlib

    path = Path(file)
    if not path.is_file():
        return tool_error([{"code": ErrorCode.DATA_102.value, "msg": f"文件不存在: {file}"}])
    h = hashlib.sha256(path.read_bytes()).hexdigest()
    return tool_ok({"path": str(path), "sha256": h})


def txt_detect_type(file: str | None = None, text: str | None = None, **_: Any) -> ToolEnvelope:
    content = text
    name = file or ""
    if file:
        content = Path(file).read_text(encoding="utf-8-sig")
    if content is None:
        return tool_error([{"code": ErrorCode.DATA_102.value, "msg": "需要 --file 或 --text"}])
    if "［元数据］" in content:
        return tool_ok({"type": "sample"})
    if "@维度:" in content or "@组别:" in content or "/#这是一道" in content:
        return tool_ok({"type": "codebook"})
    if content.lstrip().startswith("# STCX-TXT:"):
        marker = content.lstrip().split("\n", 1)[0]
        return tool_ok({"type": marker.split(":", 1)[-1].strip().split("@")[0]})
    if name.endswith("编码规则.txt") or "类目" in name:
        return tool_ok({"type": "codebook"})
    return tool_error(
        [
            {
                "code": ErrorCode.DATA_108.value,
                "msg": "无法判定 TXT 类型",
                "next_action": "添加 # STCX-TXT 标记或按命名约定重命名",
            }
        ]
    )


def run_status(workspace: str, **_: Any) -> ToolEnvelope:
    root = find_repo_root()
    current = root / "data" / workspace / "CURRENT"
    run_id = current.read_text(encoding="utf-8").strip() if current.is_file() else None
    return tool_ok({"workspace": workspace, "current_run": run_id})


REGISTRY: dict[str, ToolFn] = {
    "codebook.parse": codebook_parse,
    "codebook.validate": codebook_validate,
    "codebook.render": codebook_render,
    "samples.parse_txt": samples_parse_txt,
    "samples.render_txt": samples_render_txt,
    "fs.hash": fs_hash,
    "txt.detect_type": txt_detect_type,
    "run.status": run_status,
}


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="stcx-tool",
        description="SmartTextCoderoX tool CLI (domain.action).",
    )
    p.add_argument("tool", nargs="?", help="Tool id, e.g. codebook.parse")
    p.add_argument("--file", "-f", default=None)
    p.add_argument("--text", default=None)
    p.add_argument("--workspace", "-w", default=None)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--list", action="store_true", help="List registered tools")
    return p


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.list or args.tool is None:
        if args.tool is None and not args.list:
            parser.print_help()
            print("\nRegistered tools:")
        for name in sorted(REGISTRY):
            print(f"  {name}")
        raise SystemExit(0)
    if args.tool not in REGISTRY:
        print(
            json.dumps(
                tool_error(
                    [
                        {
                            "code": ErrorCode.TOOL_501.value,
                            "msg": f"未知工具: {args.tool}",
                            "next_action": (
                                "使用 --list 查看；已注册: " + ", ".join(sorted(REGISTRY))
                            ),
                        }
                    ]
                ),
                ensure_ascii=False,
                indent=2,
            ),
            file=sys.stderr,
        )
        raise SystemExit(2)
    if args.dry_run:
        print(
            json.dumps(
                tool_ok({"tool": args.tool, "dry_run": True}),
                ensure_ascii=False,
                indent=2,
            )
        )
        raise SystemExit(0)
    kwargs: dict[str, Any] = {
        "file": args.file,
        "text": args.text,
        "workspace": args.workspace,
    }
    result = REGISTRY[args.tool](**{k: v for k, v in kwargs.items() if v is not None})
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["status"] != "error" else 1)


if __name__ == "__main__":
    main()
