# Python 规范（SmartTextCoderoX 内核）

> 本文件是 Python 规范的**唯一正文**。`.cursor/rules/python.mdc` 只是按 `globs: **/*.py` 触发的入口，不重复正文。
> 相关：`rules/code-structure.md`（多包与命名）、`rules/data-contract.md`（数据格式）。

## 运行环境

- Python **≥ 3.10**（推荐 3.11/3.12）；CI 覆盖 3.10–3.13。
- 依赖只通过 `uv` 管理：`uv add <pkg>` / `uv sync --frozen`；**不要**手动 `pip install`，不要绕过 `uv.lock`。
- 每个文件开头允许 `from __future__ import annotations`；一律使用 4 空格缩进、UTF-8、`\n` 换行。

## 包与依赖方向

- 包：`stcx_contracts`（无内部依赖）← `stcx_core` ← `stcx_steps` / `stcx_agents` / `stcx_analytics` / `stcx_viz` / `stcx_reporting` ← `stcx_app`。
- **`stcx_analytics` 不得 import `stcx_agents`**（统计与信度必须纯计算、可离线）。
- `core` 不得 import 任何上层；禁止循环导入；禁止在 `import` 时执行 IO、读环境、起线程。

## 类型与质量

- 所有公开函数/方法必须有完整类型注解；内核包必须过 `mypy --strict`。
- `ruff check` 与 `ruff format --check` 零告警；不得用 `# type: ignore` 掩盖问题（确需时写 `# type: ignore[code]  # reason`）。
- 禁止裸 `except:`；禁止 `except Exception: pass`；捕获后必须记录或转换成本项目错误码异常。
- 禁止用 `print` 输出日志；统一走 `logging` 结构化封装（JSONL，字段见 `rules/code-structure.md` §7）。

## 数据与契约

- 结构化数据一律用 **Pydantic 模型 + JSON Schema**（`config/schema/*.json`），**不要**满天飞裸 `dict`。
- 解析外部文件时先校验再使用；校验失败抛带错误码的异常（`CB-*`/`DATA-*`/`TOOL-*`），禁止静默默认。
- 路径一律 `pathlib.Path`；**禁止**字符串拼接路径、禁止硬编码绝对路径、禁止假设运行区在仓库根（用 `STCX_WORKSPACES_ROOT`）。
- 时间一律 timezone-aware（`datetime.now(ZoneInfo("Asia/Shanghai"))`）；**禁止**裸 `datetime.now()` 入产物。
- 数字精度：占比 2 位小数、信度 3 位小数；舍入用 `decimal` 或显式 `round`，并在测试里断言边界。

## 可复现

- 任何随机行为必须显式 `random.Random(seed)` / `numpy.random.default_rng(seed)`，种子写入 manifest。
- 输出排序必须稳定（显式 `sort key`）；产物内容里不得写入运行时间戳（时间只进 manifest/日志）。
- 文件写入用"临时文件 + 原子 rename"；禁止半写状态被下游读到。

## 测试

- 测试用 `pytest`；测试函数名必须包含对应 `ACC-*` 编号（如 `test_acc_m1_03_txt_json_roundtrip`）。
- 禁止在测试里发起真实网络或付费调用；智能体一律 cassette 回放，未录制即失败。
- 禁止用 `time.sleep` 掩盖并发/幂等问题。

## 工具双形态

- 每个确定性能力同时提供 Python 函数（`stcx_tool.<域>.<动作>`）与 CLI（`uv run stcx-tool ...`），**共用同一实现**。
- 返回统一信封 `{status, data, warnings[], errors[], metrics, artifacts[]}`；有副作用的命令必须支持 `--dry-run`。
- 工具**不得**调用 LLM；追加写工具必须带 `run_id` + 操作者 + 审计。
