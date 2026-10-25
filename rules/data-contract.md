# 数据契约与格式规则

> 依据：规格 §2 全章、§3.3、§4.0.4/§4.0.5、§16.3。
> 本文件是**强制**：违反即为缺陷，评审必须打回。

## 1. 唯一权威原则

| 数据面 | 权威格式 | 说明 |
|---|---|---|
| 跨环节数据传递 | **JSONL / JSON** | 唯一机器权威；下游只按路径 + 哈希读取 |
| 人工编辑、审核、上传下载 | **TXT** | 标准样本 TXT（三段式）与编码规则 TXT（模板语法） |
| 分析交付、人机交换 | **CSV（+XLSX）** | 中文列名，同目录输出 `*.schema.json` 记录列名↔字段映射 |
| 报告 | **Markdown** | DOCX/PDF 属 MS6 |

- **禁止**新增第四种内部格式；**禁止**用 TXT 或 CSV 作为跨环节的机器权威。
- 每个产物必须有**唯一生产者**，路径可预测（规格 §4.0.5）。

## 2. 三种 Schema 必先行（契约优先）

| Schema | 文件 | 关键点 |
|---|---|---|
| `codebook` | `config/schema/codebook.schema.json` | 含 `hierarchy{dimensions[]{groups[]}}`；category 带 `dimension_id/group_id/hierarchy_path/required/required_marker_option/ai_coded/min_selections/max_selections/show_if` |
| `sample` | `config/schema/sample.schema.json` | `sample_id + metadata{} + text + source{type,file,sha256,...} + flags[]` |
| `codes` | `config/schema/codes.schema.json` | `unit_id/sample_id/field_id/coder_id/values[]/confidence/evidence[]/evidence_source/provenance{...}/flags[]/layer` |

另需：`config`、`manifest`、`audit`、`reliability_output`、`words_config`。

- Schema 变更 = **合同变更**：递增版本号、提供迁移脚本、更新 `docs/dev/migrations.md`。
- 实现前必须先写"**一个正例 + 一个反例**"的校验用例。

## 3. 编码规则文件（TXT，人工权威）

- 语法见规格 §2.3.2（EBNF）；题型双写（前缀括号 + 行内标签），冲突时**行内标签优先并报 `CB-004`**。
- 层级用作用域标记：`@维度: X` / `@组别: Y`；缺省归入 `未分类`（`CB-112`）。
- 必选标记：`*` 紧贴选项名（= 该题目必答）；与 `<isRequired>` 等价。
- 兜底项用 `<isOther>`（**不要**用 `*` 兼职）。
- 关键词书写：`AND/OR/NOT` 全大写 + 两侧各一个半角空格；半角标点；英文短语加双引号。
- **往返无损**：`render(parse(txt))` 与 `parse(render(json))` 都必须有测试。

## 4. 标准样本 TXT（人工面）

三段固定顺序：`［元数据］` → `［正文］` → `［编码结果］` →（可选）`［编码依据］`。

- 段标记全角，解析器**同时接受半角**；行格式 `字段：值`（半角 `:` 也接受）。
- 多值用 ` | `；未判定哨兵 `<未编码>`；缺段报 `DATA-106`；一文件一样本，多样本须 `［样本开始］/［样本结束］`（否则 `DATA-107`）。
- **幂等**：重渲染前必须删除旧的 `［编码结果］/［编码依据］` 段，禁止重复追加。
- TXT 文件族 8 类必须可区分（规格 §2.4.2）：段标记 → 首行 `［…］` → 文件名约定 → 仍不明确则 `DATA-108` 拒解析。

## 5. 分层与不可变（L0/L1/L2）

- **L0**：各编码员原始判定，**只写不改**；重跑 = 新 run 目录。
- **L1**：复核/裁决后的值，**仅追加**；每条改动必带 `reason + rule_ref + operator`。
- **L2**：权重与口径，不改编码值。
- 人工编码保护：L1 已有人工值的单元，自动编码不得覆盖（除非显式 `allow_auto_overwrite`）。

## 6. 幂等与断点续跑

每个环节必须声明幂等键，命中即跳过且不重复计费：

| 环节 | 幂等键 |
|---|---|
| 编码规则解析 | `sha256(源文件)` |
| 清洗 | `sha256(输入) + 清洗配置哈希` |
| 关键词编码 | `(unit_id, field_id, coder_id, codebook_hash)` |
| LLM 编码 | `(sample_id, coder_id, codebook_hash, prompt_hash, skill_hashes)` |
| 信度 | `sha256(输入) + 系数实现版本 + seed` |
| 统计 | `sha256(输入) + 口径` |
| 可视化 | `sha256(输入) + 配色/字体版本` |

## 7. manifest（每步必写）

必填：`step / run_id / started_at / finished_at / inputs[{path,sha256}] / outputs[{path,sha256}] / config_hash / codebook_hash / prompt_hash / code_version / engine / model / model_version / temperature / seed / stats / cost / resumable`。

- 缺任何必填项 = 该步视为未完成，后续步骤不得消费其输出。
- 含时间的内容（图表、LLM 输出）列入"可复现性豁免项"，必须显式声明。

## 8. 命名、精度、哨兵（统一口径）

| 项 | 规则 |
|---|---|
| 机器可读文件名 | ASCII 蛇形（`codebook.json`、`samples.jsonl`） |
| 用户可见产物名 | 允许中文，映射由 `config/default/naming.json` 定义 |
| ID | `sample_id` / `field_id` / `value_id` / `coder_id` / `run_id` 全 ASCII；四层 ID 前缀 `D_ / G_ / F_ / O_` |
| 时间 | ISO 8601 带时区（默认 `Asia/Shanghai`）；文件名时间戳 `YYYYMMDDTHHMMSS` |
| 数字 | 占比 2 位小数；信度 3 位小数；高精度值另存 JSON 侧车 |
| 空值 | JSON 用 `null`；CSV 空单元格；未判定哨兵 `<未编码>` |
| 布尔 | JSON `true/false`；CSV `1/0` |
| 换行 | 内部 `\n`；CSV 写 `\r\n` |
| 编码 | UTF-8（无 BOM 优先）；读取容忍 BOM/GBK 并记录探测结果 |

## 9. 禁止事项（数据面）

1. 绕过契约读写自定义格式。
2. 用内存/全局/环境变量传递业务数据。
3. 读取未在 `inputs` 声明的文件。
4. 把 `temp/`、`cache/` 当输入。
5. 跨 run 覆盖同名产物（必须带 `run_id`）。
6. 静默丢弃非法值（必须写 `_invalid.jsonl` 并入复核队列）。
