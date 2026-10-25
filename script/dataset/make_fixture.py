#!/usr/bin/env python3
"""Generate minimal synthetic fixture under data/_example/ (spec §11.2).

TODO(DECISION): O2 — replace with golden user data when available.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow running without install during bootstrap
_REPO = Path(__file__).resolve().parents[2]
if str(_REPO / "src" / "stcx_steps") not in sys.path:
    sys.path.insert(0, str(_REPO / "src" / "stcx_steps"))
    sys.path.insert(0, str(_REPO / "src" / "stcx_contracts"))
    sys.path.insert(0, str(_REPO / "src" / "stcx_core"))

from stcx_steps.codebook import parse_codebook, render_codebook  # noqa: E402
from stcx_steps.samples import parse_sample_txt, render_sample_txt  # noqa: E402

CODEBOOK_TXT = """# STCX-TXT: codebook@1.0
# Synthetic fixture — no real PII (MS0 / §11.2)

@维度: 信息可信度
@组别: 信源身份

()信息源可信度/#这是一道单选题#/
<isRequired>
医生*/#选项#/
  <关键词=医生 OR 医师 OR 专家>
  <提示词=医疗专业人员发言>
  <示例词=我是整形外科医生>
媒体/#选项#/
  <关键词=记者 OR 媒体 OR 报社>
其他/#选项#/
  <isOther>

[]涉及主题/#这是一道多选题#/
安全/#选项#/
  <关键词=安全 OR 风险 OR 副作用>
效果/#选项#/
  <关键词=效果 OR 改善 OR 变美>
价格/#选项#/
  <关键词=价格 OR 费用 OR 便宜>
未标示/#选项#/
  <isOther>

@维度: 呈现形式
@组别: 交互

(_)内容形式/#这是一道下拉题(单选题)#/
图文/#选项#/
  <关键词=图文 OR 配图>
视频/#选项#/
  <关键词=视频 OR 直播 OR vlog>
其他/#选项#/
  <isOther>

[_]可见元素/#这是一道下拉题(多选题)#/
标题/#选项#/
  <关键词=标题 OR 头条>
评论/#选项#/
  <关键词=评论 OR 留言>
无/#选项#/
  <isOther>
"""

SAMPLE_TXT = """［元数据］
样本ID：S0001
来源：合成平台A
账号类型：专业账号
［正文］
大家好，我是整形外科医生。今天聊聊医美安全与效果，价格方面也简单说明。
"""

SAMPLE2_TXT = """［元数据］
样本ID：S0002
来源：合成平台B
账号类型：媒体账号
［正文］
本报记者调查发现，部分机构宣传存在夸大效果的问题。
"""


def generate(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    codebook_path = out / "编码规则.txt"
    codebook_path.write_text(CODEBOOK_TXT, encoding="utf-8")

    parsed = parse_codebook(CODEBOOK_TXT, source_file="data/_example/编码规则.txt")
    if not parsed["ok"]:
        raise SystemExit(f"fixture codebook has errors: {parsed['errors']}")
    (out / "codebook.json").write_text(
        json.dumps(parsed["codebook"], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    rendered = render_codebook(parsed["codebook"])
    (out / "编码规则.rendered.txt").write_text(rendered, encoding="utf-8")

    samples_dir = out / "samples"
    samples_dir.mkdir(exist_ok=True)
    samples = []
    for name, txt in (("S0001.txt", SAMPLE_TXT), ("S0002.txt", SAMPLE2_TXT)):
        p = samples_dir / name
        p.write_text(txt, encoding="utf-8")
        sample = parse_sample_txt(txt, source_file=name)
        # roundtrip check
        again = parse_sample_txt(render_sample_txt(sample), source_file=name)
        if again["sample_id"] != sample["sample_id"] or again["text"] != sample["text"]:
            raise SystemExit(f"sample roundtrip failed for {name}")
        samples.append(sample)
        (samples_dir / f"{sample['sample_id']}.json").write_text(
            json.dumps(sample, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    (out / "samples.jsonl").write_text(
        "\n".join(json.dumps(s, ensure_ascii=False) for s in samples) + "\n",
        encoding="utf-8",
    )

    # Degenerate / multi-select placeholders for later REL tests
    (out / "expected").mkdir(exist_ok=True)
    (out / "expected" / "README.md").write_text(
        "Expected artifacts placeholders for regression (filled in MS1+).\n",
        encoding="utf-8",
    )
    (out / "README.md").write_text(
        "# data/_example\n\n"
        "Synthetic fixture for offline tests (spec §11.2).\n\n"
        "- **License**: generated content; no third-party copyright.\n"
        "- **PII**: none (synthetic).\n"
        "- **TODO(DECISION) O2**: replace with user golden data when available.\n"
        "- Regenerate: `uv run python script/dataset/make_fixture.py --out data/_example`\n",
        encoding="utf-8",
    )
    print(f"Wrote fixture to {out}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=_REPO / "data" / "_example")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        print(f"would write fixture to {args.out}")
        return
    generate(args.out)


if __name__ == "__main__":
    main()
