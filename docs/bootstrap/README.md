# 开发启动包（Bootstrap Kit）

**用途**：把这套规格交给一名**全新的 AI 程序开发工程师**（Claude Code / Cursor / Codex / DSH / 任何 Coding Agent），让它从零开始、按规格把项目做出来，而不是自由发挥。

**对应规格版本**：需求规格说明书 **v2.4.1**（仓库内：`docs/需求规格说明书.md`）
**规格是唯一需求来源**：本目录与 `rules/`、`.cursor/rules/`、`AGENTS.md` 都是它的派生物；若冲突，**以规格为准**，并回来修改派生文件。

---

## 一、仓库内位置（已并入，不再是独立启动包）

| 文件/目录 | 仓库位置 | 作用 |
|---|---|---|
| 需求规格说明书 | `docs/需求规格说明书.md` | 唯一需求来源（v2.4.1，210 KB+） |
| 仓库级 Agent 规则 | `AGENTS.md` | 必读顺序、命令、质量门、红线摘要、DoD |
| 项目约束规则（8 份） | `rules/{data-contract, code-structure, agent-harness, testing-acceptance, forbidden, collaboration, security-cost, task-breakdown}.md` | 业务与流程约束：数据契约、结构、Harness、验收、红线、协作、安全成本、任务拆解 |
| 语言/框架规范正文（4 份） | `rules/lang-{python,vue,node,electron}.md` | **正文单源**：怎么写 Python / Vue / Node / Electron 代码 |
| Cursor 规则入口（6 份 `.mdc`） | `.cursor/rules/*.mdc` | 2 份 alwaysOn（`project`、`git`）+ 4 份**薄壳**（按 `globs` 触发并指向 `rules/lang-*.md`） |
| 启动提示词 | `docs/bootstrap/user-prompt.md` | 给新 AI 开发工程师整段粘贴用 |
| 本说明 | `docs/bootstrap/README.md` | 你正在读的文件 |

> 早期版本是一个独立目录 `stcx-bootstrap/`；现已按上面结构合并进本仓库，`stcx-bootstrap/` 不再存在。

---

## 二、两层规则的分工：`.cursor/rules` vs `rules/`

两个目录**不是重复，而是两种生效机制**，各管一段。

| 维度 | `.cursor/rules/*.mdc` | `rules/*.md` |
|---|---|---|
| 生效机制 | **Cursor 自动注入**（`alwaysApply` / `globs` / `description` 决定何时进上下文） | **无自动机制**：靠 `AGENTS.md` 指定必读、人或 Agent 主动打开 |
| 受众 | 仅 Cursor（IDE 内） | 任何 Agent（Cursor / Claude Code / Codex / DSH）+ 人 |
| 格式要求 | 必须是 `.mdc` + frontmatter；官方明确 `.md` 放这里会被忽略 | 普通 Markdown，无约束 |
| 目录可见性 | 点目录，部分工具/脚本默认跳过（本仓库实测：`grep` 默认不扫 `.cursor/`） | 普通目录，所有工具可见 |
| 内容定位 | 「怎么写代码」：语言/框架层规范 | 「做什么、怎么验收、什么不许做」：项目业务与流程 |
| 数量 | 6（2 alwaysOn + 4 薄壳） | 12（8 约束 + 4 语言正文） |

### 为什么不全合并

- **全并进 `.cursor/`**：非 Cursor 工具看不到；点目录被部分工具忽略；项目宪法类规则只能 `alwaysApply`（每次对话塞满）或靠 `globs`（该生效时不生效）。
- **全并进 `rules/`**：Cursor 失去"按文件类型自动挂载"能力，语言规范要么全量注入、要么从不注入。

### 当前采用的模式：正文单源 + 薄壳入口

```
rules/lang-python.md   ← 唯一正文（人读、任何 Agent 读）
        ▲
        │ @rules/lang-python.md（Agent 用工具读取）
.cursor/rules/python.mdc  ← 只有 frontmatter + 5 条硬约束 + 指针（按 globs 触发）
```

- **正文永远只存在 `rules/`**；`.mdc` 不复制正文，只放"必须常驻的 3–5 条硬约束 + 指向正文"。
- `project.mdc`、`git.mdc` 是项目宪法/提交流程，**本来就该 always-on**，所以保留完整内容，不做薄壳。
- 好处：改一次即可；Cursor 仍能按文件类型自动挂载；非 Cursor 工具直接读 `rules/`。

### 维护纪律（防重复）

1. 任何规则要修改时，**先改 `rules/` 正文**，再检查对应 `.mdc` 的摘要是否需要同步（只改要点，不粘贴正文）。
2. `.mdc` 正文超过 10 行 = 违规信号，说明又在复制正文了。
3. 新增语言规范：先加 `rules/lang-<x>.md`，再加 `.cursor/rules/<x>.mdc` 薄壳（frontmatter + ≤5 条硬约束）。
4. 若发现同一条规则需要改两处，**说明薄壳失效**，应把该条移入正文并只保留一条硬约束摘要。

---

## 三、两种协作方式

### 方式 A：直接用 Cursor 打开本仓库（推荐）

1. Cursor → Open Folder → 选择本仓库根目录。
2. 它会自动读取 `AGENTS.md` 与 `.cursor/rules/*.mdc`：
   - `project.mdc`、`git.mdc`：`alwaysApply: true`，每次对话都注入；
   - `python.mdc` / `vue.mdc` / `node.mdc` / `electron.mdc`：按 `globs` 命中对应文件时注入，并指向 `rules/lang-*.md` 正文。
3. 让它先读 `docs/需求规格说明书.md`，再按 `rules/task-breakdown.md` 输出 MS0 拆解计划。

### 方式 B：把提示词粘给任意 Agent

1. 打开 `docs/bootstrap/user-prompt.md`，改三处占位（仓库路径、本机环境、当前里程碑）。
2. 整段粘贴，要求它先输出 MS0 计划，不要直接写代码。

任何一种方式都遵循同一条验收标准：**每次交付给四段式回复（做了什么 / 证据 / 未决 / 下一步），没有证据的"已完成"不接受。**

---

## 四、与工作区的关系（记忆同步）

- `docs/需求规格说明书.md` 是本仓库内的**唯一权威副本**，纳入 git。
- 工作区里原有的旧路径已改为**软链接**指向本文件，因此：
  - 在仓库里改规格 → 旧路径立即可见；
  - 在旧路径改规格 → 实际写入的就是仓库文件。
- 同理，规则与提示词的权威位置都在本仓库，不要在别处维护第二份副本。

---

## 五、维护规则

- 规格升版时，必须同步检查：`AGENTS.md`、`rules/*.md`、`.cursor/rules/*.mdc`、本文件里的章节号、错误码、工具名、路径是否仍然成立。
- 派生文件**不得**引入规格中没有的新要求；如有必要，先改规格再改派生。
- 规则保持**短、可执行、可断言**：每条要么能写成测试，要么能写成检查项。
- `.mdc` 的 `globs` 必须与实际目录结构一致（例如 GUI 放 `apps/gui/` 时，`vue.mdc` 的 globs 需同步）。
- 规则文件一律**不带序号**：新增按主题命名（`rules/<topic>.md`；语言规范用 `rules/lang-<x>.md`），并在 `AGENTS.md` 的必读顺序里登记。
