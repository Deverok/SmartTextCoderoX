"""Codebook TXT parse / validate / render (spec §2.3)."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from stcx_contracts.errors import ErrorCode
from stcx_contracts.schema_validate import SchemaValidator

COMMENT_RE = re.compile(r"^\s*#")
SCOPE_RE = re.compile(r"^@(?P<kind>维度|组别)\s*:\s*(?P<name>.+?)\s*$")
QUESTION_RE = re.compile(
    r"^(?P<prefix>\(\)|\[\]|\(_\)|\[_\])\s*(?P<title>.+?)/#这是一道(?P<qtype>[^#]+)#/\s*(?P<flags>.*)$"
)
OPTION_RE = re.compile(r"^(?P<name>.+?)(?P<star>\*)?/#选项#/\s*$")
ATTR_RE = re.compile(r"^\s*<(?P<body>.+)>\s*$")

PREFIX_TO_TYPE = {
    "()": "single_choice",
    "[]": "multiple_choice",
    "(_)": "dropdown_single",
    "[_]": "dropdown_multiple",
}
TYPE_TO_PREFIX = {v: k for k, v in PREFIX_TO_TYPE.items()}
TYPE_TO_LABEL = {
    "single_choice": "单选题",
    "multiple_choice": "多选题",
    "dropdown_single": "下拉题(单选题)",
    "dropdown_multiple": "下拉题(多选题)",
}
LABEL_TO_TYPE = {v: k for k, v in TYPE_TO_LABEL.items()}

KNOWN_FLAGS = {"isrequired", "isaicoded", "isother", "isexclusive"}
FLAG_SPELLING_VARIANTS = {
    "isrequired": "isRequired",
    "isaicoded": "isAiCoded",
    "isother": "isOther",
    "isexclusive": "isExclusive",
    "isrquired": "isRequired",  # known typo
}
ATTR_KEYS = {"关键词", "提示词", "示例词", "编码值", "规则"}
IS_OTHER_LABELS_DEFAULT = {"其他", "其它", "未标示", "无", "不适用", "unknown", "NA", "na"}
UNCLASSIFIED_DIM = "未分类"
UNCLASSIFIED_DIM_ID = "D_unclassified"
UNCLASSIFIED_GROUP = "未分类"
UNCLASSIFIED_GROUP_ID = "G_unclassified"

BOOL_OP_RE = re.compile(r"\s+(AND|OR|NOT)\s+")


@dataclass
class Issue:
    code: str
    level: str
    msg: str
    line: int | None = None
    next_action: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "level": self.level,
            "msg": self.msg,
            "loc": {"line": self.line} if self.line is not None else {},
            "next_action": self.next_action,
        }


@dataclass
class OptionDraft:
    value: str
    starred: bool = False
    keywords: list[str] = field(default_factory=list)
    keyword_expr: str | None = None
    hint: str | None = None
    example: str | None = None
    is_other: bool = False
    is_exclusive: bool = False
    order_index: int = 0
    line: int = 0


@dataclass
class QuestionDraft:
    title: str
    qtype: str
    prefix: str
    required: bool = False
    ai_coded: bool = False
    prompt: str | None = None
    required_marker_option: str | None = None
    options: list[OptionDraft] = field(default_factory=list)
    dimension: str = UNCLASSIFIED_DIM
    group: str = UNCLASSIFIED_GROUP
    order_index: int = 0
    line: int = 0


def _slug(text: str, prefix: str, *, used: set[str] | None = None) -> str:
    """Build ASCII id; keep uniqueness when labels are non-ASCII (Chinese)."""
    raw = re.sub(r"[^A-Za-z0-9]+", "_", text.strip()).strip("_")
    if not raw:
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:10]
        raw = f"h{digest}"
    base = f"{prefix}_{raw[:48]}"
    if used is None:
        return base
    candidate = base
    n = 2
    while candidate in used:
        candidate = f"{base}_{n}"
        n += 1
    used.add(candidate)
    return candidate


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canonical_hash(obj: Any) -> str:
    blob = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _normalize_flag(raw: str) -> tuple[str | None, bool]:
    """Return (canonical_flag_lower, is_spelling_variant_warning)."""
    key = raw.strip().lower()
    if key in FLAG_SPELLING_VARIANTS:
        canonical = FLAG_SPELLING_VARIANTS[key].lower()
        warn = key not in {"isrequired", "isaicoded", "isother", "isexclusive"}
        return canonical, warn
    if key in KNOWN_FLAGS:
        return key, False
    return None, False


def _parse_attr_body(body: str) -> tuple[str, str | None]:
    if "=" not in body:
        return body.strip(), None
    key, _, value = body.partition("=")
    return key.strip(), value


def _split_keywords(expr: str) -> tuple[list[str], bool]:
    """Split keyword expr; return (keywords, bad_bool_warning)."""
    bad = False
    if re.search(r"(?i)\b(and|or|not)\b", expr):
        for m in re.finditer(r"(?i)\b(and|or|not)\b", expr):
            token = m.group(0)
            start = m.start()
            end = m.end()
            left_ok = start > 0 and expr[start - 1] == " "
            right_ok = end < len(expr) and expr[end] == " "
            if token != token.upper() or not left_ok or not right_ok:
                bad = True
                break
    parts = BOOL_OP_RE.split(expr)
    keywords = [p.strip() for p in parts if p.strip() and p.upper() not in {"AND", "OR", "NOT"}]
    if len(keywords) <= 1 and " OR " not in expr and " AND " not in expr:
        keywords = [k.strip() for k in re.split(r"[，,]", expr) if k.strip()]
    return keywords, bad


def parse_codebook(
    text: str,
    *,
    source_file: str = "编码规则.txt",
    asterisk_semantics: str = "question_required",
    auto_detect_is_other: bool = True,
    is_other_labels: set[str] | None = None,
) -> dict[str, Any]:
    """Parse template TXT → codebook dict + issues (errors/warnings)."""
    other_labels = is_other_labels or IS_OTHER_LABELS_DEFAULT
    # Normalize newlines; strip BOM
    raw = text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    lines = raw.split("\n")

    issues: list[Issue] = []
    questions: list[QuestionDraft] = []
    dim_order: list[str] = []
    group_order: dict[str, list[str]] = {}
    current_dim = UNCLASSIFIED_DIM
    current_group = UNCLASSIFIED_GROUP
    seen_dim = False
    current_q: QuestionDraft | None = None
    current_opt: OptionDraft | None = None
    q_index = 0

    def flush_opt() -> None:
        nonlocal current_opt
        if current_q is not None and current_opt is not None:
            current_opt.order_index = len(current_q.options) + 1
            current_q.options.append(current_opt)
        current_opt = None

    def flush_q() -> None:
        nonlocal current_q, q_index
        flush_opt()
        if current_q is not None:
            q_index += 1
            current_q.order_index = q_index
            questions.append(current_q)
        current_q = None

    for lineno, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        if COMMENT_RE.match(line) or line.strip().startswith("# STCX-TXT"):
            continue

        scope = SCOPE_RE.match(line.strip())
        if scope:
            flush_q()
            kind = scope.group("kind")
            name = scope.group("name").strip()
            if kind == "维度":
                seen_dim = True
                current_dim = name
                current_group = UNCLASSIFIED_GROUP
                if name not in dim_order:
                    dim_order.append(name)
                    group_order.setdefault(name, [])
            else:
                if not seen_dim:
                    issues.append(
                        Issue(
                            ErrorCode.CB_109.value,
                            "error",
                            "@组别 出现在任何 @维度 之前",
                            lineno,
                            "先写 @维度 再写 @组别",
                        )
                    )
                current_group = name
                group_order.setdefault(current_dim, [])
                if name not in group_order[current_dim]:
                    group_order[current_dim].append(name)
            continue

        qmatch = QUESTION_RE.match(line.strip())
        if qmatch:
            flush_q()
            prefix = qmatch.group("prefix")
            title = qmatch.group("title").strip()
            # Strip optional leading (n) numbering
            title = re.sub(r"^\(\d+\)\s*", "", title)
            qtype_label = qmatch.group("qtype").strip()
            flags_tail = qmatch.group("flags") or ""
            prefix_type = PREFIX_TO_TYPE.get(prefix)
            label_type = LABEL_TO_TYPE.get(qtype_label)
            if prefix_type and label_type and prefix_type != label_type:
                issues.append(
                    Issue(
                        ErrorCode.CB_004.value,
                        "error",
                        f"前缀 {prefix} 与行内标签 {qtype_label} 冲突",
                        lineno,
                        "以行内标签为准并人工确认",
                    )
                )
            qtype = label_type or prefix_type or "single_choice"
            current_q = QuestionDraft(
                title=title,
                qtype=qtype,
                prefix=prefix,
                dimension=current_dim,
                group=current_group,
                line=lineno,
            )
            if current_dim == UNCLASSIFIED_DIM:
                issues.append(
                    Issue(
                        ErrorCode.CB_112.value,
                        "warning",
                        "题目未归属任何维度（归入未分类）",
                        lineno,
                        "显式添加 @维度/@组别",
                    )
                )
            for fm in re.finditer(r"<([^>]+)>", flags_tail):
                flag_name, warn = _normalize_flag(fm.group(1))
                if flag_name is None and "=" not in fm.group(1):
                    issues.append(
                        Issue(
                            ErrorCode.CB_007.value,
                            "error",
                            f"未知 flag: {fm.group(1)}",
                            lineno,
                            "改用 isRequired/isAiCoded 等",
                        )
                    )
                elif flag_name == "isrequired":
                    current_q.required = True
                    if warn:
                        issues.append(
                            Issue(
                                ErrorCode.CB_007.value,
                                "warning",
                                f"flag 拼写变体已接受: {fm.group(1)}",
                                lineno,
                                "建议改为 <isRequired>",
                            )
                        )
                elif flag_name == "isaicoded":
                    current_q.ai_coded = True
            continue

        omatch = OPTION_RE.match(line.strip())
        if omatch and current_q is not None:
            flush_opt()
            name = omatch.group("name").strip()
            starred = omatch.group("star") is not None
            current_opt = OptionDraft(value=name, starred=starred, line=lineno)
            if auto_detect_is_other and name in other_labels:
                current_opt.is_other = True
            if starred:
                current_q.required = True
            continue

        amatch = ATTR_RE.match(line)
        if amatch:
            body = amatch.group("body")
            if ">" in body and body.count("<") != body.count(">"):
                issues.append(
                    Issue(
                        ErrorCode.CB_006.value,
                        "error",
                        "属性行格式非法（未配对 >）",
                        lineno,
                        "检查 <> 配对",
                    )
                )
                continue
            key, value = _parse_attr_body(body)
            flag_name, warn = _normalize_flag(key)
            if value is None and flag_name:
                target_q = current_q
                target_opt = current_opt
                if flag_name == "isrequired" and target_q:
                    target_q.required = True
                elif flag_name == "isaicoded" and target_q:
                    target_q.ai_coded = True
                elif flag_name == "isother" and target_opt:
                    target_opt.is_other = True
                elif flag_name == "isexclusive" and target_opt:
                    target_opt.is_exclusive = True
                elif flag_name is None:
                    issues.append(
                        Issue(
                            ErrorCode.CB_007.value,
                            "error",
                            f"未知属性名: {key}",
                            lineno,
                            "改用受支持属性",
                        )
                    )
                if warn:
                    issues.append(
                        Issue(
                            "CB-007",
                            "warning",
                            f"flag 拼写变体已接受: {key}",
                            lineno,
                            "建议改为规范拼写",
                        )
                    )
                continue
            if key not in ATTR_KEYS:
                issues.append(
                    Issue(
                        ErrorCode.CB_007.value,
                        "error",
                        f"未知属性名: {key}",
                        lineno,
                        "改用 关键词/提示词/示例词/编码值/规则",
                    )
                )
                continue
            if value is None or value == "":
                issues.append(
                    Issue(
                        ErrorCode.CB_006.value,
                        "error",
                        f"属性值非法: <{key}=>",
                        lineno,
                        "提供非空属性值",
                    )
                )
                continue
            if current_opt is None and current_q is not None and key == "提示词":
                current_q.prompt = value
                continue
            if current_opt is None:
                issues.append(
                    Issue(
                        ErrorCode.CB_008.value,
                        "error",
                        "属性行缺少所属选项/题目",
                        lineno,
                        "将属性放在题目或选项下方",
                    )
                )
                continue
            if key == "关键词":
                kws, bad = _split_keywords(value)
                current_opt.keywords = kws
                current_opt.keyword_expr = value.strip()
                if bad:
                    issues.append(
                        Issue(
                            ErrorCode.CB_105.value,
                            "warning",
                            "布尔运算符书写不规范",
                            lineno,
                            "使用大写 AND/OR/NOT 且两侧半角空格",
                        )
                    )
                if not kws:
                    issues.append(
                        Issue(
                            ErrorCode.CB_006.value,
                            "error",
                            "关键词为空",
                            lineno,
                            "提供至少一个关键词",
                        )
                    )
            elif key == "提示词":
                current_opt.hint = value
            elif key == "示例词":
                current_opt.example = value
            continue

        # Free-floating text
        issues.append(
            Issue(
                ErrorCode.CB_008.value,
                "error",
                f"游离文本: {line.strip()[:40]}",
                lineno,
                "删除或改为注释",
            )
        )

    flush_q()

    # Empty scope checks
    dim_with_questions = {q.dimension for q in questions}
    for d in dim_order:
        if d not in dim_with_questions:
            issues.append(
                Issue(
                    ErrorCode.CB_110.value,
                    "error",
                    f"空维度: {d}",
                    None,
                    "删除空标记或补充题目",
                )
            )

    # Build hierarchy + categories
    if UNCLASSIFIED_DIM not in dim_order and any(
        q.dimension == UNCLASSIFIED_DIM for q in questions
    ):
        dim_order.insert(0, UNCLASSIFIED_DIM)
        group_order.setdefault(UNCLASSIFIED_DIM, [UNCLASSIFIED_GROUP])

    dimensions: list[dict[str, Any]] = []
    dim_ids: dict[str, str] = {}
    group_ids: dict[tuple[str, str], str] = {}
    used_ids: set[str] = {UNCLASSIFIED_DIM_ID, UNCLASSIFIED_GROUP_ID}
    for di, dlabel in enumerate(dim_order, start=1):
        if dlabel == UNCLASSIFIED_DIM:
            did = UNCLASSIFIED_DIM_ID
        else:
            did = _slug(dlabel, "D", used=used_ids)
        dim_ids[dlabel] = did
        groups_out: list[dict[str, Any]] = []
        groups = group_order.get(dlabel, [])
        # ensure groups that appear on questions exist
        for q in questions:
            if q.dimension == dlabel and q.group not in groups:
                groups.append(q.group)
        if not groups:
            groups = [UNCLASSIFIED_GROUP]
        for gi, glabel in enumerate(groups, start=1):
            if glabel == UNCLASSIFIED_GROUP and dlabel == UNCLASSIFIED_DIM:
                gid = UNCLASSIFIED_GROUP_ID
            else:
                gid = _slug(f"{dlabel}_{glabel}", "G", used=used_ids)
            group_ids[(dlabel, glabel)] = gid
            groups_out.append({"group_id": gid, "label": glabel, "order_index": gi})
        dimensions.append(
            {
                "dimension_id": did,
                "label": dlabel,
                "order_index": di,
                "groups": groups_out,
            }
        )

    # Per-dimension category count for CB-111
    dim_cat_count: dict[str, int] = {}
    for q in questions:
        dim_cat_count[q.dimension] = dim_cat_count.get(q.dimension, 0) + 1
    for d, n in dim_cat_count.items():
        if n == 1 and d != UNCLASSIFIED_DIM:
            issues.append(
                Issue(
                    ErrorCode.CB_111.value,
                    "warning",
                    f"维度「{d}」下仅 1 个类目",
                    None,
                    "确认维度切分是否过细",
                )
            )

    title_counts: dict[str, int] = {}
    for q in questions:
        title_counts[q.title] = title_counts.get(q.title, 0) + 1
    for title, n in title_counts.items():
        if n > 1:
            issues.append(
                Issue(
                    ErrorCode.CB_003.value,
                    "error",
                    f"全局题目显示名重复: {title}",
                    None,
                    "改题名",
                )
            )

    # Cross-dimension same title warning CB-113
    by_title: dict[str, set[str]] = {}
    for q in questions:
        by_title.setdefault(q.title, set()).add(q.dimension)
    for title, dims in by_title.items():
        if len(dims) > 1:
            issues.append(
                Issue(
                    ErrorCode.CB_113.value,
                    "warning",
                    f"不同维度下存在同名题目: {title}",
                    None,
                    "改题名或配置分隔符",
                )
            )

    categories: list[dict[str, Any]] = []
    for q in questions:
        field_id = _slug(q.title, "F", used=used_ids)
        did = dim_ids.get(q.dimension, UNCLASSIFIED_DIM_ID)
        gid = group_ids.get((q.dimension, q.group), UNCLASSIFIED_GROUP_ID)

        if len(q.options) < 2:
            issues.append(
                Issue(
                    ErrorCode.CB_001.value,
                    "error",
                    f"题目「{q.title}」选项数 < 2",
                    q.line,
                    "至少补充两个选项",
                )
            )

        opt_names = [o.value for o in q.options]
        if len(opt_names) != len(set(opt_names)):
            issues.append(
                Issue(
                    ErrorCode.CB_002.value,
                    "error",
                    f"题目「{q.title}」选项显示名重复",
                    q.line,
                    "修改重复选项名",
                )
            )

        star_count = sum(1 for o in q.options if o.starred)
        if star_count > 1:
            issues.append(
                Issue(
                    ErrorCode.CB_106.value,
                    "warning",
                    f"题目「{q.title}」多个选项带 *",
                    q.line,
                    "只保留一个 *",
                )
            )

        has_other = any(o.is_other for o in q.options)
        if not has_other:
            issues.append(
                Issue(
                    ErrorCode.CB_104.value,
                    "warning",
                    f"题目「{q.title}」缺少其他/未标示类选项",
                    q.line,
                    "补充 <isOther> 选项",
                )
            )

        # keyword set intersections
        kw_sets = [(o.value, set(o.keywords)) for o in q.options if o.keywords]
        for i in range(len(kw_sets)):
            for j in range(i + 1, len(kw_sets)):
                inter = kw_sets[i][1] & kw_sets[j][1]
                if inter:
                    issues.append(
                        Issue(
                            ErrorCode.CB_103.value,
                            "warning",
                            f"题目「{q.title}」选项关键词交集: {sorted(inter)}",
                            q.line,
                            "去重关键词",
                        )
                    )

        empty_signals = all((not o.keywords and not o.hint and not q.prompt) for o in q.options)
        if q.required and empty_signals:
            issues.append(
                Issue(
                    ErrorCode.CB_005.value,
                    "error",
                    f"必答题「{q.title}」所有选项均为空判定",
                    q.line,
                    "补充关键词或提示词",
                )
            )
        if not q.required and empty_signals:
            issues.append(
                Issue(
                    ErrorCode.CB_107.value,
                    "warning",
                    f"题目「{q.title}」未声明必选且无可判定信号",
                    q.line,
                    "补充内容或标记必选",
                )
            )

        options_out: list[dict[str, Any]] = []
        required_marker: str | None = None
        for o in q.options:
            vid = _slug(o.value, "O", used=used_ids)
            if o.starred and required_marker is None:
                required_marker = vid
            if o.keywords:
                n = len(o.keywords)
                if n < 3 or n > 5:
                    issues.append(
                        Issue(
                            ErrorCode.CB_102.value,
                            "warning",
                            f"选项「{o.value}」关键词数量={n} 不在 3–5",
                            o.line,
                            "调整到 3–5 个",
                        )
                    )
            if not o.keywords and o.hint and not o.is_other:
                issues.append(
                    Issue(
                        ErrorCode.CB_101.value,
                        "warning",
                        f"选项「{o.value}」缺少关键词（仅有提示词）",
                        o.line,
                        "建议补充关键词",
                    )
                )
            if o.is_other and o.keywords:
                issues.append(
                    Issue(
                        ErrorCode.CB_108.value,
                        "warning",
                        f"is_other 选项「{o.value}」带有关键词",
                        o.line,
                        "确认是否为真正兜底项",
                    )
                )
            options_out.append(
                {
                    "value_id": vid,
                    "value": o.value,
                    "hint": o.hint,
                    "example": o.example,
                    "keywords": o.keywords,
                    "keyword_expr": o.keyword_expr,
                    "is_other": o.is_other,
                    "is_exclusive": o.is_exclusive,
                    "order_index": o.order_index,
                }
            )

        categories.append(
            {
                "field_id": field_id,
                "label": q.title,
                "dimension_id": did,
                "group_id": gid,
                "hierarchy_path": [q.dimension, q.group, q.title],
                "type": q.qtype,
                "required": q.required,
                "required_marker_option": required_marker,
                "ai_coded": q.ai_coded,
                "prompt": q.prompt,
                "min_selections": None,
                "max_selections": None,
                "show_if": None,
                "order_index": q.order_index,
                "options": options_out,
            }
        )

    hierarchy = {"dimensions": dimensions}
    codebook_body = {"hierarchy": hierarchy, "categories": categories}
    codebook_hash = _canonical_hash(codebook_body)
    source_sha = _sha256_text(raw)

    codebook: dict[str, Any] = {
        "meta": {
            "schema_version": "1.0",
            "codebook_version": "v1",
            "title": source_file,
            "locale": "zh-CN",
            "created_at": datetime.now(timezone.utc).astimezone().isoformat(),
            "source_file": source_file,
            "source_sha256": source_sha,
            "codebook_hash": codebook_hash,
            "asterisk_semantics": asterisk_semantics,
        },
        "hierarchy": hierarchy,
        "categories": categories,
    }

    errors = [i for i in issues if i.level == "error"]
    warnings = [i for i in issues if i.level == "warning"]
    return {
        "codebook": codebook,
        "issues": [i.as_dict() for i in issues],
        "errors": [i.as_dict() for i in errors],
        "warnings": [i.as_dict() for i in warnings],
        "ok": len(errors) == 0,
    }


def validate_codebook(
    codebook: dict[str, Any],
    *,
    schema_dir: str | None = None,
) -> list[dict[str, Any]]:
    """Schema-validate codebook; return list of error dicts (empty if ok)."""
    try:
        SchemaValidator("codebook", schema_dir=schema_dir).validate(codebook)
    except Exception as exc:  # noqa: BLE001 — convert to issue list
        return [{"code": ErrorCode.DATA_103.value, "level": "error", "msg": str(exc)}]
    return []


def render_codebook(codebook: dict[str, Any]) -> str:
    """Render codebook JSON → normalized template TXT (2-space indented attrs)."""
    lines: list[str] = ["# STCX-TXT: codebook@1.0"]
    dims = codebook.get("hierarchy", {}).get("dimensions", [])
    cats = codebook.get("categories", [])

    known: set[tuple[str, str]] = set()
    for dim in sorted(dims, key=lambda d: d["order_index"]):
        lines.append(f"@维度: {dim['label']}")
        groups = sorted(dim.get("groups", []), key=lambda g: g["order_index"])
        for group in groups:
            lines.append(f"@组别: {group['label']}")
            known.add((dim["dimension_id"], group["group_id"]))
            group_cats = [
                c
                for c in cats
                if c.get("dimension_id") == dim["dimension_id"]
                and c.get("group_id") == group["group_id"]
            ]
            group_cats.sort(key=lambda c: c.get("order_index", 0))
            for cat in group_cats:
                lines.extend(_render_question(cat))

    orphans = [c for c in cats if (c.get("dimension_id"), c.get("group_id")) not in known]
    if orphans:
        lines.append(f"@维度: {UNCLASSIFIED_DIM}")
        lines.append(f"@组别: {UNCLASSIFIED_GROUP}")
        for cat in orphans:
            lines.extend(_render_question(cat))

    return "\n".join(lines).rstrip() + "\n"


def _render_question(cat: dict[str, Any]) -> list[str]:
    qtype = cat["type"]
    prefix = TYPE_TO_PREFIX[qtype]
    label = TYPE_TO_LABEL[qtype]
    lines = [f"{prefix}{cat['label']}/#这是一道{label}#/"]
    if cat.get("required") and not cat.get("required_marker_option"):
        lines.append("<isRequired>")
    if cat.get("ai_coded"):
        lines.append("<isAiCoded>")
    if cat.get("prompt"):
        lines.append(f"  <提示词={cat['prompt']}>")
    marker = cat.get("required_marker_option")
    for opt in sorted(cat.get("options", []), key=lambda o: o.get("order_index", 0)):
        star = "*" if marker and opt.get("value_id") == marker else ""
        # If required via marker on this option
        if cat.get("required") and marker and opt.get("value_id") == marker:
            star = "*"
        lines.append(f"{opt['value']}{star}/#选项#/")
        if opt.get("is_other"):
            lines.append("  <isOther>")
        if opt.get("is_exclusive"):
            lines.append("  <isExclusive>")
        if opt.get("hint"):
            lines.append(f"  <提示词={opt['hint']}>")
        expr = opt.get("keyword_expr") or (
            " OR ".join(opt["keywords"]) if opt.get("keywords") else None
        )
        if expr:
            lines.append(f"  <关键词={expr}>")
        if opt.get("example"):
            lines.append(f"  <示例词={opt['example']}>")
    return lines
