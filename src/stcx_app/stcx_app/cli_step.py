"""stcx-step CLI skeleton (spec §4.0.6)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from stcx_contracts.errors import ErrorCode, StcxError
from stcx_core.config import load_config
from stcx_core.paths import WorkspacePaths
from stcx_steps.codebook import parse_codebook, render_codebook

STEP_PRODUCERS: dict[str, dict[str, str]] = {
    "ST01": {
        "input": "config/{version}/编码规则.txt",
        "output": "data/{version}/clean/codebook.json",
        "producer": "ST01（或人工编辑编码规则.txt）",
    },
    "ST03": {
        "input": "data/{version}/origin/** 或 transcript/",
        "output": "data/{version}/clean/samples.jsonl",
        "producer": "ST03 clean.run",
    },
    "ST06": {
        "input": "data/{version}/clean/samples.jsonl + codebook.json",
        "output": "data/{version}/codes_l0/{run}/keyword.jsonl",
        "producer": "ST06 code.keyword",
    },
}


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="stcx-step",
        description="Run a single SmartTextCoderoX pipeline step (ST01–ST16).",
    )
    p.add_argument("step", nargs="?", help="Step id, e.g. ST01")
    p.add_argument("--workspace", "-w", required=False, help="Workspace / version name")
    p.add_argument("--attach-run", default=None, help="Attach to existing run_id")
    p.add_argument("--dry-run", action="store_true", help="Check inputs/cost; no writes")
    p.add_argument("--repo-root", type=Path, default=None, help="Override repo root")
    return p


def _missing_input_guidance(step: str, paths: WorkspacePaths, missing: str) -> str:
    meta = STEP_PRODUCERS.get(step, {})
    producer = meta.get("producer", "上游步骤")
    stage = paths.input_stage(step)
    return (
        f"[{ErrorCode.RUN_201.value}] 缺少输入: {missing}\n"
        f"  谁生成它: {producer}\n"
        f"  补法 1: 先运行上游步骤生成该文件\n"
        f"  补法 2: 将已校验文件放入 {stage}/ 并附 _manifest.json\n"
        f"下一步: 补齐输入后重试 `stcx-step {step} --workspace {paths.version}`"
    )


def run_step(
    step: str,
    workspace: str,
    *,
    dry_run: bool = False,
    attach_run: str | None = None,
    repo_root: Path | None = None,
) -> int:
    paths = WorkspacePaths.create(workspace, repo_root=repo_root)
    try:
        cfg = load_config(workspace, repo_root=paths.repo_root)
    except StcxError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if step == "ST01":
        src = paths.codebook_txt()
        if not src.is_file():
            print(_missing_input_guidance(step, paths, str(src)), file=sys.stderr)
            return 1
        if dry_run:
            print(
                json.dumps(
                    {
                        "status": "ok",
                        "step": step,
                        "workspace": workspace,
                        "dry_run": True,
                        "would_read": str(src),
                        "offline_mode": cfg.get("offline_mode"),
                        "attach_run": attach_run,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 0
        text = src.read_text(encoding="utf-8-sig")
        asterisk = cfg.get("codebook", {}).get("asterisk_semantics") or "question_required"
        result = parse_codebook(
            text,
            source_file=str(src.relative_to(paths.repo_root)),
            asterisk_semantics=asterisk,
        )
        if not result["ok"]:
            print(json.dumps(result["errors"], ensure_ascii=False, indent=2), file=sys.stderr)
            return 1
        out_dir = paths.data / "clean"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_json = out_dir / "codebook.json"
        out_txt = out_dir / "codebook_rendered.txt"
        out_json.write_text(
            json.dumps(result["codebook"], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        out_txt.write_text(render_codebook(result["codebook"]), encoding="utf-8")
        print(
            json.dumps(
                {
                    "status": "ok",
                    "step": step,
                    "artifacts": [str(out_json), str(out_txt)],
                    "warnings": result["warnings"],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    # Generic skeleton for other steps
    meta = STEP_PRODUCERS.get(step)
    if meta is None:
        print(
            f"未知步骤 {step}。支持: {', '.join(sorted(STEP_PRODUCERS))}（MS0 骨架）",
            file=sys.stderr,
        )
        return 2
    if dry_run:
        print(
            json.dumps(
                {
                    "status": "ok",
                    "step": step,
                    "workspace": workspace,
                    "dry_run": True,
                    "note": "MS0 stub — full implementation in later milestones",
                    "attach_run": attach_run,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    print(_missing_input_guidance(step, paths, meta["input"]), file=sys.stderr)
    return 1


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.step is None:
        parser.print_help()
        raise SystemExit(0)
    if not args.workspace:
        print("错误: 需要 --workspace <name>", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(
        run_step(
            args.step,
            args.workspace,
            dry_run=args.dry_run,
            attach_run=args.attach_run,
            repo_root=args.repo_root,
        )
    )


if __name__ == "__main__":
    main()
