"""Error code catalog (spec §2.3.4 / §10.5 / §16.4).

User-facing errors are always: code + human message + next action.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ErrorCode(str, Enum):
    # Codebook errors
    CB_001 = "CB-001"
    CB_002 = "CB-002"
    CB_003 = "CB-003"
    CB_004 = "CB-004"
    CB_005 = "CB-005"
    CB_006 = "CB-006"
    CB_007 = "CB-007"
    CB_008 = "CB-008"
    # Codebook warnings
    CB_101 = "CB-101"
    CB_102 = "CB-102"
    CB_103 = "CB-103"
    CB_104 = "CB-104"
    CB_105 = "CB-105"
    CB_106 = "CB-106"
    CB_107 = "CB-107"
    CB_108 = "CB-108"
    CB_109 = "CB-109"
    CB_110 = "CB-110"
    CB_111 = "CB-111"
    CB_112 = "CB-112"
    CB_113 = "CB-113"
    # Data
    DATA_101 = "DATA-101"
    DATA_102 = "DATA-102"
    DATA_103 = "DATA-103"
    DATA_104 = "DATA-104"
    DATA_105 = "DATA-105"
    DATA_106 = "DATA-106"
    DATA_107 = "DATA-107"
    DATA_108 = "DATA-108"
    DATA_201 = "DATA-201"
    DATA_202 = "DATA-202"
    # Tools
    TOOL_301 = "TOOL-301"
    TOOL_302 = "TOOL-302"
    TOOL_401 = "TOOL-401"
    TOOL_402 = "TOOL-402"
    TOOL_501 = "TOOL-501"
    TOOL_601 = "TOOL-601"
    TOOL_602 = "TOOL-602"
    TOOL_603 = "TOOL-603"
    TOOL_604 = "TOOL-604"
    # Run
    RUN_201 = "RUN-201"
    RUN_202 = "RUN-202"
    RUN_203 = "RUN-203"
    # LLM
    LLM_401 = "LLM-401"
    LLM_402 = "LLM-402"
    LLM_429 = "LLM-429"
    LLM_451 = "LLM-451"
    # Reliability
    REL_301 = "REL-301"
    REL_302 = "REL-302"
    REL_303 = "REL-303"
    # Report
    REP_401 = "REP-401"
    REP_402 = "REP-402"
    # Package / env
    PKG_501 = "PKG-501"
    PKG_502 = "PKG-502"
    PKG_503 = "PKG-503"
    # Config
    CFG_001 = "CFG-001"


@dataclass(frozen=True, slots=True)
class ErrorDef:
    code: ErrorCode
    level: str  # error | warning
    message: str
    next_action: str


_CATALOG: dict[ErrorCode, ErrorDef] = {
    ErrorCode.CB_001: ErrorDef(
        ErrorCode.CB_001, "error", "题目无选项或选项数 < 2", "为该题至少补充两个选项后重试"
    ),
    ErrorCode.CB_002: ErrorDef(
        ErrorCode.CB_002, "error", "同一题目内选项显示名重复", "修改重复的选项名后重试"
    ),
    ErrorCode.CB_003: ErrorDef(
        ErrorCode.CB_003,
        "error",
        "全局题目显示名重复或多题共用同一 field_id",
        "改题名或拆分 field_id",
    ),
    ErrorCode.CB_004: ErrorDef(
        ErrorCode.CB_004,
        "error",
        "前缀题型标记与行内标签冲突",
        "以行内标签为准并人工确认后统一前缀",
    ),
    ErrorCode.CB_005: ErrorDef(
        ErrorCode.CB_005,
        "error",
        "必答题的所有选项均为空判定（无关键词且无提示词）",
        "为至少一个选项补充关键词或提示词",
    ),
    ErrorCode.CB_006: ErrorDef(
        ErrorCode.CB_006, "error", "属性行格式非法", "检查 <属性=值> 配对与转义后重试"
    ),
    ErrorCode.CB_007: ErrorDef(
        ErrorCode.CB_007, "error", "出现未知属性名或未知 flag", "改用受支持属性或更正拼写"
    ),
    ErrorCode.CB_008: ErrorDef(
        ErrorCode.CB_008, "error", "非注释/题目/选项/属性的游离文本", "删除或改为注释行"
    ),
    ErrorCode.CB_101: ErrorDef(
        ErrorCode.CB_101, "warning", "选项缺少关键词（仅有提示词）", "建议补充 3–5 个关键词"
    ),
    ErrorCode.CB_102: ErrorDef(
        ErrorCode.CB_102, "warning", "关键词数量不在 3–5 个之间", "调整关键词数量到偏好区间"
    ),
    ErrorCode.CB_103: ErrorDef(
        ErrorCode.CB_103, "warning", "同一题目内两选项关键词集合存在交集", "检查互斥性并去重关键词"
    ),
    ErrorCode.CB_104: ErrorDef(
        ErrorCode.CB_104, "warning", "题目下缺少其他/未标示类选项", "补充 <isOther> 兜底选项"
    ),
    ErrorCode.CB_105: ErrorDef(
        ErrorCode.CB_105,
        "warning",
        "布尔运算符未大写或两侧未留半角空格",
        "改为 AND/OR/NOT 且两侧各一空格",
    ),
    ErrorCode.CB_106: ErrorDef(
        ErrorCode.CB_106, "warning", "同一题目内多个选项带 *", "只保留一个 * 或改用 <isRequired>"
    ),
    ErrorCode.CB_107: ErrorDef(
        ErrorCode.CB_107,
        "warning",
        "题目未声明必选且无可判定信号",
        "补充关键词/提示词或显式标记必选/可选",
    ),
    ErrorCode.CB_108: ErrorDef(
        ErrorCode.CB_108, "warning", "is_other 选项被显式赋予关键词", "确认该选项是否为真正兜底项"
    ),
    ErrorCode.CB_109: ErrorDef(
        ErrorCode.CB_109, "error", "层级标记顺序非法：@组别 早于任何 @维度", "先写 @维度 再写 @组别"
    ),
    ErrorCode.CB_110: ErrorDef(
        ErrorCode.CB_110, "error", "空维度或空组别：作用域后无题目", "删除空标记或补充题目"
    ),
    ErrorCode.CB_111: ErrorDef(
        ErrorCode.CB_111, "warning", "某维度下仅 1 个类目", "确认维度切分是否过细"
    ),
    ErrorCode.CB_112: ErrorDef(
        ErrorCode.CB_112, "warning", "题目未归属任何维度（归入未分类）", "显式添加 @维度/@组别"
    ),
    ErrorCode.CB_113: ErrorDef(
        ErrorCode.CB_113,
        "warning",
        "不同维度/组别下存在同名题目",
        "改题名或配置层级分隔符后再导出单层表",
    ),
    ErrorCode.DATA_101: ErrorDef(
        ErrorCode.DATA_101, "error", "文本编码探测失败", "另存为 UTF-8 或提供编码提示后重试"
    ),
    ErrorCode.DATA_106: ErrorDef(
        ErrorCode.DATA_106, "error", "样本 TXT 缺少必需段", "补齐［元数据］［正文］等段后重试"
    ),
    ErrorCode.DATA_107: ErrorDef(
        ErrorCode.DATA_107,
        "error",
        "单文件含多样本但未用样本边界包裹",
        "使用［样本开始］/［样本结束］",
    ),
    ErrorCode.DATA_108: ErrorDef(
        ErrorCode.DATA_108, "error", "无法判定 TXT 类型", "按命名约定重命名或添加 # STCX-TXT 标记"
    ),
    ErrorCode.DATA_201: ErrorDef(
        ErrorCode.DATA_201, "error", "必填元数据缺失", "按变量配置补齐元数据字段"
    ),
    ErrorCode.DATA_202: ErrorDef(
        ErrorCode.DATA_202, "warning", "文本超长被截断", "检查截断 flag 并确认是否接受"
    ),
    ErrorCode.TOOL_301: ErrorDef(
        ErrorCode.TOOL_301, "error", "编码值不在词表", "修正编码值或更新编码规则"
    ),
    ErrorCode.TOOL_302: ErrorDef(
        ErrorCode.TOOL_302, "error", "必答题留空", "为必答题给出至少一个编码值"
    ),
    ErrorCode.RUN_201: ErrorDef(
        ErrorCode.RUN_201,
        "error",
        "依赖步骤未完成或缺少输入",
        "先运行上游步骤，或向 input_stage 放置已校验文件",
    ),
    ErrorCode.RUN_202: ErrorDef(
        ErrorCode.RUN_202, "error", "run 目录已存在但哈希不符", "使用新 run_id 或 --attach-run 核对"
    ),
    ErrorCode.RUN_203: ErrorDef(
        ErrorCode.RUN_203,
        "error",
        "工作区名非法",
        "使用正则 ^[A-Za-z0-9_\\-\\u4e00-\\u9fa5]{1,64}$",
    ),
    ErrorCode.CFG_001: ErrorDef(
        ErrorCode.CFG_001,
        "error",
        "缺少必需配置项",
        "在 config/default 或 config/{version} 中补齐该键",
    ),
    ErrorCode.PKG_501: ErrorDef(
        ErrorCode.PKG_501,
        "error",
        "缺少 ffmpeg",
        "将 ffmpeg 放到 lib/bin/ffmpeg 或加入 PATH 后重试",
    ),
    ErrorCode.PKG_502: ErrorDef(
        ErrorCode.PKG_502, "error", "缺少中文字体", "将 OFL 字体放入 lib/fonts/ 后重试"
    ),
    ErrorCode.PKG_503: ErrorDef(
        ErrorCode.PKG_503, "error", "sidecar 不可执行", "检查 bin/runtime 权限与架构"
    ),
    ErrorCode.LLM_401: ErrorDef(
        ErrorCode.LLM_401, "error", "模型认证失败", "检查 STCX_LLM_*_API_KEY 后重试"
    ),
    ErrorCode.LLM_402: ErrorDef(ErrorCode.LLM_402, "error", "模型余额不足", "充值或切换离线路由"),
    ErrorCode.LLM_429: ErrorDef(ErrorCode.LLM_429, "error", "模型限流", "降低并发或稍后重试"),
    ErrorCode.LLM_451: ErrorDef(
        ErrorCode.LLM_451, "error", "内容审核拒答", "检查样本并记入失败清单，勿静默丢弃"
    ),
    ErrorCode.REL_301: ErrorDef(
        ErrorCode.REL_301, "warning", "信度退化（P_e=1 或数据不足）", "检查类目分布或补充样本"
    ),
    ErrorCode.REL_302: ErrorDef(
        ErrorCode.REL_302, "error", "编码员不足 2", "增加第二个独立编码员后再算信度"
    ),
    ErrorCode.REL_303: ErrorDef(
        ErrorCode.REL_303, "warning", "信度口径不适用", "改用适用口径或排除该字段"
    ),
    ErrorCode.REP_401: ErrorDef(
        ErrorCode.REP_401, "error", "报告数字不一致", "修复统计源后重新装配报告"
    ),
    ErrorCode.REP_402: ErrorDef(
        ErrorCode.REP_402, "error", "报告章节缺失", "检查报告模板与装配清单"
    ),
    ErrorCode.TOOL_401: ErrorDef(
        ErrorCode.TOOL_401, "error", "裁决缺少 rule_ref", "为每条裁决补充规则依据"
    ),
    ErrorCode.TOOL_402: ErrorDef(
        ErrorCode.TOOL_402, "error", "超出 max_audit_ratio 熔断", "降低改动比例或提高阈值后重试"
    ),
    ErrorCode.TOOL_501: ErrorDef(
        ErrorCode.TOOL_501, "error", "目标导出格式不支持", "改用受支持格式或安装扩展模块"
    ),
    ErrorCode.TOOL_601: ErrorDef(
        ErrorCode.TOOL_601, "error", "决策概率与选项不等长", "检查模型输出对齐后再校准"
    ),
    ErrorCode.TOOL_602: ErrorDef(
        ErrorCode.TOOL_602, "error", "ECE 超限（概率不可信）", "重新校准或禁用决策编码器"
    ),
    ErrorCode.TOOL_603: ErrorDef(
        ErrorCode.TOOL_603, "error", "准入未达标", "决策编码器自动降级为 prefilter"
    ),
    ErrorCode.TOOL_604: ErrorDef(
        ErrorCode.TOOL_604, "error", "校准文件与编码规则哈希不匹配", "规则升版后须重新校准"
    ),
    ErrorCode.DATA_102: ErrorDef(
        ErrorCode.DATA_102, "error", "输入文件不存在", "检查路径或先运行上游步骤"
    ),
    ErrorCode.DATA_103: ErrorDef(
        ErrorCode.DATA_103, "error", "Schema 校验失败", "对照 config/schema 修正字段后重试"
    ),
    ErrorCode.DATA_104: ErrorDef(
        ErrorCode.DATA_104, "error", "样本 ID 重复", "去重 sample_id 后重试"
    ),
    ErrorCode.DATA_105: ErrorDef(
        ErrorCode.DATA_105, "error", "人读视图解析失败", "检查 TXT 段标记与字段格式"
    ),
}


def error_catalog() -> dict[str, dict[str, str]]:
    """Return serializable catalog for docs sync tests."""
    out: dict[str, dict[str, str]] = {}
    for code, defn in _CATALOG.items():
        out[code.value] = {
            "level": defn.level,
            "message": defn.message,
            "next_action": defn.next_action,
        }
    return out


def lookup(code: ErrorCode | str) -> ErrorDef:
    key = ErrorCode(code) if not isinstance(code, ErrorCode) else code
    if key not in _CATALOG:
        return ErrorDef(key, "error", f"未知错误码 {key}", "查阅 docs/dev/error-codes.md")
    return _CATALOG[key]


class StcxError(Exception):
    """Typed application error with code + message + next action."""

    def __init__(
        self,
        code: ErrorCode | str,
        *,
        detail: str | None = None,
        loc: dict[str, Any] | None = None,
        next_action: str | None = None,
    ) -> None:
        defn = lookup(code)
        self.code = defn.code.value
        self.level = defn.level
        self.message = detail or defn.message
        self.next_action = next_action or defn.next_action
        self.loc = loc or {}
        super().__init__(f"[{self.code}] {self.message} → {self.next_action}")

    def as_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "level": self.level,
            "msg": self.message,
            "next_action": self.next_action,
            "loc": self.loc,
        }
