# AGENTS.md — SmartTextCoderoX 仓库规则（面向 AI 开发工程师）

> 本文件是仓库根规则。**需求规格说明书（v2.4.1）是唯一需求来源**；本文件只补充"怎么干活"，不定义需求。
> 冲突时：规格 > 本文件 > 你的习惯。

## 0. 项目身份

- 仓库名 / 产品名：**SmartTextCoderoX**
- Python 发行包前缀：**STCX-** ｜ 导入名：`stcx_*` ｜ CLI：`stcx-step`、`stcx-tool`
- 环境变量前缀：`STCX_`（工作区根：`STCX_WORKSPACES_ROOT`）
- TXT 机器标记：`# STCX-TXT: <type>@1.0`

## 1. 开工前必读（顺序固定）

1. `docs/需求规格说明书.md`（v2.4.1，唯一需求来源）
2. 本文件
3. `rules/` 共 12 份：**8 份项目约束**（`data-contract` → `task-breakdown`）+ **4 份语言规范正文**（`rules/lang-{python,vue,node,electron}.md`）
4. 若涉及智能体：`rules/agent-harness.md` 必须逐条落实
5. 若使用 Cursor：`.cursor/rules/*.mdc` 按 globs 自动生效（`project.mdc`、`git.mdc` 为 alwaysApply；其余 4 份是**薄壳**，只放摘要并指向 `rules/lang-*.md` 正文）

## 2. 常用命令（约定，实现后必须一致）

```powershell
uv sync --frozen                       # 安装/同步依赖
uv run ruff check . ; uv run mypy src  # 静态检查（内核必须过）
uv run pytest                          # 全量测试（离线）
uv run stcx-step ST01 --workspace v1   # 单独运行一个环节
uv run stcx-tool codebook.validate --file config/v1/编码规则.txt
uv run python script/dataset/make_fixture --out data/_example
```

任何新增命令必须同时提供 `--help` 与 `--dry-run`（有副作用的命令）。

## 3. 目录纪律（详见规格 §3.0/§3.1）

| 区域 | 目录 | 规则 |
|---|---|---|
| 静态区 | `bin/ config/ docs/ lib/ models/ module/ prompt/ script/ src/` | **运行时只读**；写入静态区 = 缺陷 |
| 运行区 | `cache/ data/ logs/ reports/ results/ temp/` | 按 `{version}` 与 `run_id` 隔离；不进 git（`data/_example/` 例外） |

- 机器可读文件用 **ASCII 蛇形命名**；中文名只用于用户可见产物（规格 §2.7）。
- **禁止**把 `temp/`、`cache/` 的内容当作任何环节的输入。

## 4. 质量门（提交前必须全绿）

| 门 | 命令 | 通过标准 |
|---|---|---|
| 格式与静态检查 | `uv run ruff check . && uv run ruff format --check .` | 0 error |
| 类型 | `uv run mypy src` | 内核包 0 error（严格模式） |
| 单元与契约测试 | `uv run pytest -q` | 全绿 |
| 离线集成 | `uv run pytest -m integration` | 全绿，**断网可跑** |
| 许可审计 | `uv run python script/ci/license_check` | 无 AGPL/传染性许可进入内核链路 |
| 覆盖率 | `uv run pytest --cov=src` | 关键算法 100% 分支；整体 `[SHOULD]` ≥ 85% |

## 5. 编码约定（摘要，详见 `rules/code-structure.md`）

- 依赖方向单向：`bridge/cli → app → {engines, agents, analytics, viz, reporting} → io → core`；**`analytics` 不得依赖 `agents`**。
- 配置化一切：路径、模型名、端点、字段名、阈值、并发、预算。
- fail-fast：缺配置、缺字体、缺 ffmpeg、Schema 不符 → 立即报错，禁止静默默认。
- 日志：结构化 JSONL（`ts/level/run_id/step/unit_id/event/message/extra`）+ 人读版本；**默认不写样本文本原文**。
- 错误：`码 + 人话 + 下一步动作` 三件套；码表见 `docs/dev/error-codes.md`。

## 6. 数据与复现（摘要，详见 `rules/data-contract.md`）

- L0 只写不改；改动一律进 L1 并记审计；分析口径变化进 L2。
- 每步写 manifest：输入/输出哈希、配置哈希、编码规则哈希、提示词哈希、代码版本、模型与参数、统计、成本。
- 每个环节必须能**单独运行**（`--attach-run` 可并入已有 run），缺输入时只提示不自动跑上游。

## 7. 提交与协作（摘要，详见 `rules/collaboration.md`）

- 分支：`feat/<ms>-<slug>`、`fix/<slug>`、`docs/<slug>`；禁止直推 `main`。
- 提交信息：`<type>(<scope>): <what> — <why>`，一次提交只做一件事。
- **每个 PR 必须附验收证据**（测试名/命令/输出）；无证据不合并。
- 修改合同（Schema）必须附迁移脚本与版本号递增。

## 8. 红线（完整清单见 `rules/forbidden.md`）

1. 改数据来达标（随机改值 / 按达标调参 / 隐藏不达标结果）。
2. 硬编码路径、模型名、端点、字段名。
3. 绕过契约传数据（内存、全局、环境变量、未声明输入、`temp//cache/`）。
4. 静默降级（上下文超限、缺字体、缺 ffmpeg、解析失败）。
5. 编造证据或引用未实测结论。
6. 设计依赖本地大模型权重的默认路径。

## 9. 遇到规格未覆盖的情况

1. 查规格 §15.1（已闭环决策）→ §15.2（追加决策）。
2. 仍无答案 → 按 §15.4 的建议默认实现 + 留 `TODO(DECISION)` + 配置位。
3. 在交付回复的【未决与风险】里明确列出，**不得静默决定**。

## 10. 定义（DoD）通用清单

任何任务完成前自查：

- [ ] 契约先于实现，且有失败用例
- [ ] 全部新增行为有测试，且测试名含对应 `ACC-*` 编号
- [ ] 幂等与往返测试通过（适用时）
- [ ] manifest / 日志 / 错误码齐备
- [ ] 静态检查、类型检查、测试全绿；离线可跑
- [ ] `CHANGELOG.md` 已更新
- [ ] 交付回复四段式（做了什么 / 证据 / 未决 / 下一步）
