# Electron 规范（SmartTextCoderoX 桌面壳）

> 本文件是 Electron 规范的**唯一正文**。`.cursor/rules/electron.mdc` 只是按 `globs: **/main/**, **/preload/**, electron-builder.*` 触发的入口。
> 相关：`rules/lang-vue.md`（渲染层）、`rules/lang-node.md`（工具链）、`rules/security-cost.md`（密钥与打包）。

## 进程模型（硬性）

```
Electron 主进程（Node）  ←→  Python sidecar（spawn，NDJSON/JSON-RPC）
        ↕ IPC（preload 白名单）
Vue 渲染进程（纯 UI）
```

- 窗口必须：`contextIsolation: true`、`nodeIntegration: false`、`sandbox: true`；**禁止**关闭 `contextIsolation`。
- 渲染进程**不得**直接访问文件系统、子进程、网络密钥；一切系统能力经 preload 暴露的白名单 API。
- preload 只做"转发 + 参数校验"，不得包含业务逻辑。

## IPC 契约

- 使用 `ipcMain.handle` / `ipcRenderer.invoke`；通道名必须是常量（`shared/channels.ts`），**禁止**散落字符串。
- 每个通道必须：入参 Schema 校验、超时、错误映射为 `{code, message, hint}`、日志记录（不记原文/密钥）。
- 长任务（编码/转录/统计/信度）走事件流：`run.progress / run.log / run.warning / run.error / run.done`；必须支持取消与续跑。
- 协议握手时校验版本；GUI 与内核版本不匹配要明确报错，而不是行为异常。

## 密钥

- 密钥只经 Electron `safeStorage` 或 `.env`（git 忽略）；**禁止**写入配置文件、日志、manifest。
- 渲染进程永远拿不到明文密钥；需要展示时只显示"已配置/未配置"。

## sidecar 生命周期

- 启动：解析 `process.resourcesPath` 下 onedir 可执行 → 握手 → 校验协议版本 → 就绪。
- 异常：启动失败给可操作指引；崩溃时自动重启（有限次）并保留现场日志；退出时 `kill` 子进程（防孤儿）。
- 首次启动自检：字体、ffmpeg、sidecar 可执行、模型配置完整性；缺项必须在 UI 上给出修复步骤。

## 文件与路径

- 文件选择、拖拽、打开目录一律在主进程做（`dialog`）；渲染进程只接收结果。
- 运行区根可配置（`STCX_WORKSPACES_ROOT`）；打包后不得假设仓库根存在。
- 用户数据目录用 `app.getPath('userData')`；不要在安装目录里写运行产物。

## 打包与分发

- `electron-builder`：Windows NSIS、macOS dmg、Linux AppImage/deb；Python sidecar 与资源放 `extraResources`。
- 随包资源必须显式声明（字体/停用词/词典/ffmpeg/示例数据），否则打包后必坏。
- 体积预算 `[SHOULD]` < 300 MB；本地模型按需下载，不随包。
- macOS 注意文件名 NFD 与签名/公证；Windows 注意 SmartScreen 提示。

## 调试与日志

- 主进程日志写 `logs/{version}/{run_id}/app.jsonl`；渲染进程错误通过 IPC 上报主进程统一落盘。
- 开发期才允许打开的调试端口必须默认关闭，并写入文档。
- 禁止任何遥测/崩溃上报（规格 §1.5）。
