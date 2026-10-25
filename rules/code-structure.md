# 代码结构、命名与配置规则

> 依据：规格 §3、§10、§16.1、§16.4。本文件是**强制**。

## 1. 分区纪律

| 区域 | 目录 | 运行时 | 入 git |
|---|---|---|---|
| 静态区 | `bin/ config/ docs/ lib/ models/ module/ prompt/ script/ src/` | **只读** | 是（`bin/` 仅 `.gitkeep`，`models/` 除外） |
| 运行区 | `cache/ data/ logs/ reports/ results/ temp/` | 读写 | 否（`data/_example/` 例外） |

- 写入静态区 = 缺陷。首次启动自检必须能发现"静态区被写"。
- 运行区可整体外置（`STCX_WORKSPACES_ROOT`）；代码不得假设运行区在仓库根。

## 2. 多包与依赖方向

```
STCX-contracts   ← 无内部依赖（Schema/模型/校验器/错误码）
STCX-core        ← contracts（配置、workspace/run、manifest、日志、成本、注册表）
STCX-steps       ← core（确定性环节与独立入口）
STCX-agents      ← core, contracts（Pydantic AI 智能体）
STCX-analytics   ← core（统计/信度/词频/抽样/分布治理）※ 不得依赖 agents
STCX-viz         ← core
STCX-reporting   ← core, analytics
STCX-app         ← 以上全部（编排执行器、GUI 协议服务、统一入口）
```

- **硬性**：`STCX-analytics` 与 `STCX-agents` 完全解耦（保证离线可用与可测试）。
- 依赖方向单向：`bridge/cli → app → {engines, agents, analytics, viz, reporting} → io → core`；`core` 不得依赖任何上层。
- 新增第三方扩展放 `module/`（运行时发现）；内核必须在**无 `module/`** 时正常启动。

## 3. 工具必须双形态（函数 + CLI）

- 形态：Python `stcx_tool.<域>.<动作>()`；CLI `uv run stcx-tool <域>.<动作>`。
- **共用同一实现**，禁止各写一套。
- 统一返回信封：`{status, data, warnings[], errors[], metrics, artifacts[]}`。
- **工具不调用 LLM**（智能体不注册为工具）。
- 追加写工具（`adjudicate.apply`、`distribution.apply`、`manifest.write`、`audit.append`）必须带 `run_id` + 操作者标识 + 审计。
- 有副作用的命令必须有 `--dry-run`。

## 4. 配置化（禁止硬编码）

以下一律来自配置，不得出现在代码字面量中：

- 路径与目录名、工作区根、`{version}`、run 目录结构
- 模型名、端点、`provider_by_modality`、`endpoint_kind`
- 编码规则字段名、状态哨兵、分隔符
- 阈值（信度门槛、分布约束、抽帧、上下文预算、并发、预算上限）
- 配色、字体、列名映射

配置分层：`config/default/`（默认值）→ `config/{version}/`（版本级）→ 环境变量（仅密钥与工作区根）。

**fail-fast**：缺配置 → 立即报错并指出缺哪一项；**禁止静默默认**（规格 §2.7 教训：时区写错会静默算错一整天）。

## 5. 命名约定

| 对象 | 规则 |
|---|---|
| Python 模块/函数/变量 | `snake_case`；类 `PascalCase`；常量 `UPPER_SNAKE` |
| 包 | `stcx_*`（导入名）、`STCX-*`（发行名） |
| 环节 ID | `ST01`…`ST16`（与规格 §4.0.3 一致，禁止自创编号） |
| 智能体 ID | `A1/A3/A4/A5/A6`（A2 已合并入 A1，保留占位） |
| 工具 ID | `<域>.<动作>`，域限于：`codebook/samples/clean/text/transcribe/code/adjudicate/reliability/distribution/sample/stats/words/viz/report/export/manifest/audit/cost/run/fs/txt/coder` |
| 错误码 | `<前缀>-<三位>`，前缀限于：`CB/DATA/TOOL/RUN/LLM/REL/REP/PKG` |
| 配置键 | `snake_case`，与 Schema 字段同名 |
| 测试文件 | `tests/**/test_<模块>.py`；测试函数名含 `ACC-*` 编号 |

## 6. 错误处理

- 三件套：**错误码 + 人话 + 下一步动作**；禁止只抛栈。
- 分类处置：可重试（限流/网络）自动退避；不可重试（认证/审核拒答/参数错误）立即失败并记录。
- 任何"降级"必须同时写 `flag` 与日志；降级路径必须有测试。

## 7. 日志

- 结构化 JSONL：`ts / level / run_id / step / unit_id / event / message / extra`。
- 人读版本同内容；GUI 实时 tail，支持按级别与步骤过滤。
- **默认不写样本文本原文**（只写 `sample_id` 与摘要哈希）；调试级开启需显式确认并告警。
- 轮转上限默认 200 MB/run。

## 8. 类型与质量

- 内核包必须过 `mypy` 严格模式；公开接口必须有类型注解。
- `ruff` 零 error；格式由 `ruff format` 统一。
- 新增依赖必须在 PR 中说明理由、体积影响与许可证（见 `rules/security-cost.md`）。

## 9. 禁止事项（代码面）

1. 硬编码路径、模型名、端点、字段名。
2. 用内存/全局单例/环境变量传业务数据。
3. `core` 反向依赖上层；`analytics` 依赖 `agents`。
4. 在静态区写入运行产物。
5. 用 `print` 代替日志；用裸 `except` 吞异常。
6. 为了通过测试而放宽断言或删除用例。
