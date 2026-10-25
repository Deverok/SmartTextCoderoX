# Vue 3 规范（SmartTextCoderoX GUI 渲染层）

> 本文件是 Vue 规范的**唯一正文**。`.cursor/rules/vue.mdc` 只是按 `globs: **/*.vue, **/*.tsx` 触发的入口，不重复正文。
> 相关：`rules/lang-node.md`（工具链）、`rules/lang-electron.md`（进程与 IPC）。

## 技术选型

- **Vue 3 + `<script setup lang="ts">` + Composition API**；禁止 Options API、禁止 Vue 2 写法（`this`、`filters`）。
- 构建用 Vite；状态用 **Pinia**；路由用 Vue Router（如需要）。
- 组件文件用 **PascalCase**（`CategoryTree.vue`），页面放 `views/`，复用组件放 `components/`；一个组件一个目录（含 `index.ts` 时统一导出）。

## 组件规范

- `defineProps<Props>()` / `withDefaults` / `defineEmits<Emits>()` 必须带类型；禁止 `any`。
- props 只读：禁止直接修改 props；需要派生状态用 `computed`。
- 副作用（请求、订阅、定时器）必须放 `onMounted`/`onUnmounted` 并在卸载时清理。
- 组件超过 200 行视为需要拆分（提取子组件或组合式函数 `useXxx()`）。
- 禁止在模板里写复杂表达式；抽到 `computed` 或方法。

## 状态与数据

- 服务端数据（统计表、编码结果、日志）**不放进 Pinia 当缓存**：用查询层 + 分页/虚拟滚动。
- 大列表（≥ 1 万行）必须分页、虚拟滚动或服务端聚合；**禁止**把全量数据一次性塞进渲染进程内存（规格 §8.3）。
- 表单状态放组件本地；跨页面共享才进 Pinia；每个 store 单一职责、可单测。

## 与内核交互

- **只允许**通过 preload 暴露的白名单 API（如 `window.stcx`）与主进程通信；**禁止**在渲染进程直接 `require('fs')`、`child_process`、`fetch` 内核端口或读密钥。
- 调用遵循协议（规格 §9.3）：`invoke`/`handle` 或 NDJSON 事件流；通道名必须是常量（统一放 `shared/channels.ts`）。
- 所有调用必须处理四类状态：加载中 / 成功 / 业务错误（带错误码）/ 网络或进程崩溃；错误提示必须含**错误码 + 人话 + 下一步动作**。
- 长任务（编码、转录、统计）必须支持进度、取消、续跑 UI；禁止阻塞式等待。

## 界面与文案

- 界面默认**中文**；专业英文术语保留原文并在首次出现处给中英对照（如 `Krippendorff's Alpha（克里彭多夫 α）`）。
- 文案集中管理（i18n 文件或常量文件），禁止在模板里散落中文长句。
- 中文排版：标题/正文用同一套字号阶梯；数字用等宽字体；表格列右对齐数字、左对齐文本。
- 类目树（维度 ▸ 组别 ▸ 题目 ▸ 选项）必须可折叠；层级改动走主进程命令并提示"将产生新 run"。

## 样式

- 使用 scoped CSS / CSS 变量；禁止全局污染与 `!important` 滥用。
- 配色取自 `config/default/palette.json`（单一来源）；不要在每个组件里写死颜色。
- 图表在 GUI 内优先用轻量 SVG/Canvas 组件；需要导出时由内核侧渲染 PNG/SVG/PDF（规格 §4.8）。

## 测试

- 组件测试用 Vitest + `@vue/test-utils`；关键路径用 Playwright E2E（导入→校验→编码→复核→信度→报告）。
- 测试里禁止依赖真实后端：IPC 用 mock，返回固定 cassette。
