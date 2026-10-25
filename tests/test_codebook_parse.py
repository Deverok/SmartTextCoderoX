"""Codebook parse / roundtrip / CB-* — ACC-M1-* (MS0 T-010)."""

from __future__ import annotations

import pytest
from stcx_steps.codebook import parse_codebook, render_codebook, validate_codebook

MINIMAL_OK = """# STCX-TXT: codebook@1.0
@维度: 信息可信度
@组别: 信源身份

()信息源可信度/#这是一道单选题#/
医生*/#选项#/
  <关键词=医生 OR 医师 OR 专家>
其他/#选项#/
  <isOther>
"""

FOUR_TYPES = """# STCX-TXT: codebook@1.0
@维度: D1
@组别: G1

()单选示例/#这是一道单选题#/
<isAiCoded>
A*/#选项#/
  <关键词=甲 OR 乙 OR 丙>
B/#选项#/
  <关键词=丁 OR 戊 OR 己>
其他/#选项#/
  <isOther>

[]多选示例/#这是一道多选题#/
X/#选项#/
  <关键词=一 OR 二 OR 三>
Y/#选项#/
  <关键词=四 OR 五 OR 六>
未标示/#选项#/
  <isOther>

(_)下拉单选/#这是一道下拉题(单选题)#/
P/#选项#/
  <关键词=子 OR 丑 OR 寅>
Q/#选项#/
  <关键词=卯 OR 辰 OR 巳>
其他/#选项#/
  <isOther>

[_]下拉多选/#这是一道下拉题(多选题)#/
M/#选项#/
  <关键词=东 OR 南 OR 西>
N/#选项#/
  <关键词=北 OR 中 OR 外>
无/#选项#/
  <isOther>
"""


def test_ACC_M1_01_four_types_and_isAiCoded() -> None:
    result = parse_codebook(FOUR_TYPES)
    assert result["ok"], result["errors"]
    types = {c["type"] for c in result["codebook"]["categories"]}
    assert types == {
        "single_choice",
        "multiple_choice",
        "dropdown_single",
        "dropdown_multiple",
    }
    ai = next(c for c in result["codebook"]["categories"] if c["label"] == "单选示例")
    assert ai["ai_coded"] is True


@pytest.mark.parametrize(
    "flag",
    ["<isRequired>", "<isrequired>", "<isRquired>"],
)
def test_ACC_M1_02_spelling_variants(flag: str) -> None:
    text = f"""@维度: D
@组别: G
()题/#这是一道单选题#/
{flag}
A/#选项#/
  <关键词=甲 OR 乙 OR 丙>
B/#选项#/
  <关键词=丁 OR 戊 OR 己>
其他/#选项#/
  <isOther>
"""
    result = parse_codebook(text)
    assert result["ok"], result["errors"]
    assert result["codebook"]["categories"][0]["required"] is True


def test_ACC_M1_03_txt_json_roundtrip() -> None:
    result = parse_codebook(FOUR_TYPES)
    assert result["ok"]
    rendered = render_codebook(result["codebook"])
    again = parse_codebook(rendered)
    assert again["ok"], again["errors"]
    c1 = result["codebook"]["categories"]
    c2 = again["codebook"]["categories"]
    assert [c["label"] for c in c1] == [c["label"] for c in c2]
    assert [c["type"] for c in c1] == [c["type"] for c in c2]
    # Schema validate
    assert validate_codebook(result["codebook"]) == []


def _codes_in(result: dict) -> set[str]:
    return {i["code"] for i in result["issues"]}


@pytest.mark.parametrize(
    "code,snippet",
    [
        (
            "CB-001",
            "@维度: D\n@组别: G\n()题/#这是一道单选题#/\n仅一/#选项#/\n  <关键词=a OR b OR c>\n",
        ),
        (
            "CB-002",
            "@维度: D\n@组别: G\n()题/#这是一道单选题#/\n同/#选项#/\n  <关键词=a OR b OR c>\n同/#选项#/\n  <关键词=d OR e OR f>\n",
        ),
        (
            "CB-003",
            "@维度: D\n@组别: G\n()同名/#这是一道单选题#/\nA/#选项#/\n  <关键词=a OR b OR c>\nB/#选项#/\n  <关键词=d OR e OR f>\n其他/#选项#/\n  <isOther>\n()同名/#这是一道单选题#/\nC/#选项#/\n  <关键词=g OR h OR i>\nD/#选项#/\n  <关键词=j OR k OR l>\n其他/#选项#/\n  <isOther>\n",
        ),
        (
            "CB-004",
            "@维度: D\n@组别: G\n()冲突/#这是一道多选题#/\nA/#选项#/\n  <关键词=a OR b OR c>\nB/#选项#/\n  <关键词=d OR e OR f>\n其他/#选项#/\n  <isOther>\n",
        ),
        (
            "CB-005",
            "@维度: D\n@组别: G\n()空判/#这是一道单选题#/\n<isRequired>\nA/#选项#/\nB/#选项#/\n",
        ),
        (
            "CB-006",
            "@维度: D\n@组别: G\n()题/#这是一道单选题#/\nA/#选项#/\n  <关键词=>\nB/#选项#/\n  <关键词=d OR e OR f>\n其他/#选项#/\n  <isOther>\n",
        ),
        (
            "CB-007",
            "@维度: D\n@组别: G\n()题/#这是一道单选题#/\nA/#选项#/\n  <未知属性=1>\nB/#选项#/\n  <关键词=d OR e OR f>\n其他/#选项#/\n  <isOther>\n",
        ),
        (
            "CB-008",
            "@维度: D\n@组别: G\n这是游离文本\n()题/#这是一道单选题#/\nA/#选项#/\n  <关键词=a OR b OR c>\nB/#选项#/\n  <关键词=d OR e OR f>\n其他/#选项#/\n  <isOther>\n",
        ),
        (
            "CB-109",
            "@组别: G\n@维度: D\n()题/#这是一道单选题#/\nA/#选项#/\n  <关键词=a OR b OR c>\nB/#选项#/\n  <关键词=d OR e OR f>\n其他/#选项#/\n  <isOther>\n",
        ),
        (
            "CB-110",
            "@维度: 空维\n@组别: G\n@维度: D\n@组别: G2\n()题/#这是一道单选题#/\nA/#选项#/\n  <关键词=a OR b OR c>\nB/#选项#/\n  <关键词=d OR e OR f>\n其他/#选项#/\n  <isOther>\n",
        ),
    ],
)
def test_ACC_M1_04_error_codes(code: str, snippet: str) -> None:
    result = parse_codebook(snippet)
    assert code in _codes_in(result), result["issues"]


@pytest.mark.parametrize(
    "code,snippet",
    [
        (
            "CB-101",
            "@维度: D\n@组别: G\n()题/#这是一道单选题#/\nA/#选项#/\n  <提示词=仅提示>\n  <关键词=a OR b OR c>\nB/#选项#/\n  <提示词=只有提示无关键词>\n其他/#选项#/\n  <isOther>\n",
        ),
        (
            "CB-102",
            "@维度: D\n@组别: G\n()题/#这是一道单选题#/\nA/#选项#/\n  <关键词=只有一个>\nB/#选项#/\n  <关键词=d OR e OR f>\n其他/#选项#/\n  <isOther>\n",
        ),
        (
            "CB-103",
            "@维度: D\n@组别: G\n()题/#这是一道单选题#/\nA/#选项#/\n  <关键词=共享 OR 甲 OR 乙>\nB/#选项#/\n  <关键词=共享 OR 丙 OR 丁>\n其他/#选项#/\n  <isOther>\n",
        ),
        (
            "CB-104",
            "@维度: D\n@组别: G\n()题/#这是一道单选题#/\nA/#选项#/\n  <关键词=a OR b OR c>\nB/#选项#/\n  <关键词=d OR e OR f>\n",
        ),
        (
            "CB-105",
            "@维度: D\n@组别: G\n()题/#这是一道单选题#/\nA/#选项#/\n  <关键词=a or b OR c>\nB/#选项#/\n  <关键词=d OR e OR f>\n其他/#选项#/\n  <isOther>\n",
        ),
        (
            "CB-106",
            "@维度: D\n@组别: G\n()题/#这是一道单选题#/\nA*/#选项#/\n  <关键词=a OR b OR c>\nB*/#选项#/\n  <关键词=d OR e OR f>\n其他/#选项#/\n  <isOther>\n",
        ),
        (
            "CB-107",
            "@维度: D\n@组别: G\n()题/#这是一道单选题#/\nA/#选项#/\nB/#选项#/\n",
        ),
        (
            "CB-108",
            "@维度: D\n@组别: G\n()题/#这是一道单选题#/\nA/#选项#/\n  <关键词=a OR b OR c>\n其他/#选项#/\n  <isOther>\n  <关键词=兜底 OR 词 OR 汇>\n",
        ),
        (
            "CB-111",
            "@维度: 仅一题维\n@组别: G\n()唯一/#这是一道单选题#/\nA/#选项#/\n  <关键词=a OR b OR c>\nB/#选项#/\n  <关键词=d OR e OR f>\n其他/#选项#/\n  <isOther>\n",
        ),
        (
            "CB-112",
            "()无维/#这是一道单选题#/\nA/#选项#/\n  <关键词=a OR b OR c>\nB/#选项#/\n  <关键词=d OR e OR f>\n其他/#选项#/\n  <isOther>\n",
        ),
        (
            "CB-113",
            "@维度: D1\n@组别: G\n()同名题/#这是一道单选题#/\nA/#选项#/\n  <关键词=a OR b OR c>\nB/#选项#/\n  <关键词=d OR e OR f>\n其他/#选项#/\n  <isOther>\n@维度: D2\n@组别: G\n()同名题/#这是一道单选题#/\nC/#选项#/\n  <关键词=g OR h OR i>\nD/#选项#/\n  <关键词=j OR k OR l>\n其他/#选项#/\n  <isOther>\n",
        ),
    ],
)
def test_ACC_M1_04_warning_codes(code: str, snippet: str) -> None:
    result = parse_codebook(snippet)
    assert code in _codes_in(result), result["issues"]


def test_ACC_M1_05_export_format_marker() -> None:
    """ACC-M1-05: exported TXT keeps external-platform-compatible markers.

    Full external import is a one-time manual check; here we assert isomorphic markers.
    """
    result = parse_codebook(MINIMAL_OK)
    assert result["ok"]
    txt = render_codebook(result["codebook"])
    assert "/#这是一道单选题#/" in txt
    assert "/#选项#/" in txt
    assert "@维度:" in txt
