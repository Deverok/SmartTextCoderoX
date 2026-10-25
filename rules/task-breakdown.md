# 任务拆解规则、任务模板与 DoD

> 依据：规格 §12（里程碑）、§14（验收总表）、§4.0.6（环节可单独运行）、§16（工具规格）。
> 目的：让每个任务都**可独立验收**，避免"大爆炸式交付"。

## 1. 优先级铁律

```
契约与骨架  >  确定性闭环（全离线）  >  AI 编码  >  生成智能体与裁决  >  多模态  >  GUI  >  扩展与导出
   MS0            MS1                       MS2         MS3                  MS4      MS5      MS6
```

- **不得跳级**：MS1 未全绿前不进入 MS2（AI 环节依赖契约与统计/信度可用）。
- MS5（GUI）不得早于 MS1 完成：GUI 只是壳，壳里没有可跑的内核就无意义。
- 每个里程碑内部的顺序：**Schema → 失败用例 → 实现 → 校验器 → 集成**。

## 2. 任务粒度标准

一个任务应当满足全部四条，否则继续拆：

1. 能在 **半天到两天** 内完成（对 AI 开发工程师而言）；
2. 有**唯一**的验收出口（一个命令 + 一个 `ACC-*` 或一组）；
3. 不跨包地大范围改动（最多涉及 2 个包）；
4. 完成后**不阻塞**其他任务的语义（接口先冻结）。

## 3. 任务模板（每个任务开始时必须写出）

```markdown
### T-<编号> <一句话标题>

- 里程碑：MSx
- 关联规格：§<章节> / 验收项：ACC-<...>
- 目标：<可观察的结果，不写"优化""完善">
- 输入（契约）：<文件/接口，含 Schema>
- 输出（契约）：<文件/接口，含 Schema>
- 依赖：<任务 ID / 无>
- 实现要点：<关键算法或流程，3–6 条>
- 不做（Out of scope）：<明确排除的东西>
- DoD：
  - [ ] <可运行命令> 通过
  - [ ] <失败用例> 存在且先失败后通过
  - [ ] manifest/日志/错误码齐备
  - [ ] ACC 追溯表已更新
- 证据形式：<命令 + 测试名 + 产物路径>
- 风险：<已知不确定项，含规格 §15.4 的哪一条>
```

## 4. DoD 通用清单（所有任务）

- [ ] 契约先于实现；有失败用例
- [ ] 幂等测试通过（适用时）；往返测试通过（适用时）
- [ ] 值域/必答/完整性校验通过
- [ ] 降级路径有 flag 与测试（适用时）
- [ ] `uv run ruff check . && uv run mypy src && uv run pytest` 全绿
- [ ] 离线可跑（断网 + cassette）
- [ ] `CHANGELOG.md` 更新；`docs/dev/acceptance-traceability.md` 更新
- [ ] 交付回复四段式

## 5. 里程碑开工清单（照抄执行）

### MS0 契约与骨架
1. `T-001` 目录树与分区落地 + `verify_workspace` 检查器
2. `T-002` 三 Schema + 各一正一反例
3. `T-003` uv workspace 多包骨架 + 依赖方向测试
4. `T-004` 配置加载 + Schema 校验 + fail-fast
5. `T-005` 日志（JSONL + 人读）与错误码常量表
6. `T-006` `stcx-step` / `stcx-tool` 骨架（`--help` / `--dry-run` / `--workspace` / 缺输入指引）
7. `T-007` CI（lint+type+unit+离线集成）+ 覆盖率
8. `T-008` `make_fixture` 最小合成数据 + 往返测试
9. `T-009` `docs/dev/acceptance-traceability.md` 初版

### MS1 确定性闭环（示例任务）
- `T-010` `codebook.parse/validate/render` + `CB-*` 全码
- `T-011` `samples.read/validate/render_txt/parse_txt` + 三段式往返
- `T-012` `clean.run` 规则链 + 清洗报告 + 幂等
- `T-013` `code.keyword` 关键词/布尔引擎 + 值域校验
- `T-014` `reliability.compute/bootstrap/diagnose` + 附录 C 用例
- `T-015` `stats.*`（含层级汇总与多选双口径）
- `T-016` `words.*` + 字体自检
- `T-017` `viz.render` + 中文无方框断言
- `T-018` `report.assemble/verify` + 数字一致性拦截用例
- `T-019` 端到端离线集成 + 两次运行哈希一致

## 6. 单个任务的交付范例（供对照）

```markdown
### T-010 编码规则解析与校验（CB-* 全码）

- 里程碑：MS0/MS1 交界；关联：§2.3、§16.1；验收：ACC-M1-01…05
- 目标：把模板语法 TXT 解析为规范 JSON，并输出带行号的校验报告；四种题型与层级标记均可解析
- 输入：config/{version}/编码规则.txt（UTF-8，含 BOM 容忍）
- 输出：clean/codebook.json、clean/codebook_validation.json、views/编码类目表.txt
- 依赖：T-002（Schema）
- 实现要点：EBNF 递归下降；`@维度/@组别` 作用域栈；`*` 记 required_marker_option；大小写不敏感 flag；渲染规范化（全角/半角、缩进 2 空格）
- 不做：docx/xlsx 转换（属 A1）
- DoD：
  - [ ] 用户既有 `类目模版.txt` 解析通过（ACC-M1-01）
  - [ ] 三种拼写变体均可解析（ACC-M1-02）
  - [ ] TXT↔JSON 往返一致（ACC-M1-03）
  - [ ] CB-001…CB-113 每个码至少 1 用例（ACC-M1-04）
  - [ ] 未知属性报 CB-007 且带行号
- 证据：`uv run pytest tests/test_codebook_parse.py -q` → N passed（列出 ACC 编号）
```

## 7. 升级与回退

- 任务失败（DoD 未满足）：**不得**标记完成；写清卡点与已尝试方案，交回用户决策。
- 需求缺口：走 `rules/collaboration.md` 第 5 节的需求变更流程。
- 契约变更：走 `rules/collaboration.md` 第 2 节。
