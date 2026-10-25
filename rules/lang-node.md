# Node.js / 工具链规范

> 本文件是 Node 规范的**唯一正文**。`.cursor/rules/node.mdc` 只是按 `globs: package.json, **/*.mjs …` 触发的入口。
> 相关：`rules/lang-electron.md`（桌面壳）、`rules/security-cost.md`（依赖许可与体积）。

## 运行环境与包管理

- Node **≥ 20**；只用 **pnpm**（`pnpm-lock.yaml` 必须提交）；禁止混用 npm/yarn。
- 项目默认 `"type": "module"`（ESM）；需要 CommonJS 的例外要写明理由。
- `package.json` 的 `scripts` 必须是可复现的单一入口；禁止在 CI 里跑临时拼的一次性命令。

## 依赖

- 依赖最小化：新增依赖必须在 PR 说明用途、体积、许可证（与 `rules/security-cost.md` 一致）。
- 禁止引入 AGPL/传染性许可依赖到主链路。
- 锁定大版本；升级必须单独提交并跑全量测试。

## 目录与脚本

- 仓库级脚本放 `script/`（dev / ci / maintenance / dataset），**不参与运行时**。
- 构建产物放 `bin/`（不进 git）；运行产物放运行区（`cache/ data/ logs/ reports/ results/ temp/`）。
- 脚本禁止硬编码绝对路径；用 `process.env.STCX_*` 或参数传入。

## 子进程与 sidecar

- 启动 Python sidecar：`spawn(..., { stdio: ['pipe','pipe','pipe'] })`，协议为 **NDJSON（JSON-RPC 2.0 over stdio）**。
- 必须处理：启动失败（可执行文件缺失/权限）、协议版本不匹配、超时、非零退出、崩溃重启、退出时清理子进程（防止孤儿进程）。
- **禁止**用 shell 字符串拼接传参（注入风险）；用数组参数。
- 捕获 stderr 并落盘到 `logs/`；用户可见错误必须是"码 + 人话 + 下一步"。

## 打包相关

- Electron 打包用 `electron-builder`；sidecar 与资源放 `extraResources`，路径用 `process.resourcesPath` 解析（**不要**用相对路径）。
- 必须显式声明随包资源：字体、停用词、词典、ffmpeg、示例数据；首次启动做自检。
- Python sidecar 用 PyInstaller **onedir**（不用 onefile）。

## 代码质量

- TypeScript：`strict: true`；禁止 `any`（确需时 `unknown` + 收窄）。
- ESLint + Prettier 必须全绿；提交前跑 `pnpm lint && pnpm typecheck && pnpm test`。
- 禁止 `console.log` 留在产物代码里（用统一 logger；构建时剔除）。
- 异步：优先 `async/await`；禁止裸 `.then()` 链里吞错误；所有 Promise 必须有 `catch` 或上层兜底。
