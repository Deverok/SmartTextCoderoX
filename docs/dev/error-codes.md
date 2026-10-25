# 错误码表

与 `stcx_contracts.errors.ErrorCode` / `error_catalog()` 一一对应。  
用户可见错误一律：**码 + 人话 + 下一步动作**。

| 码 | 级别 | 含义 | 下一步 |
|---|---|---|---|
| CB-001 | error | 题目无选项或选项数 < 2 | 为该题至少补充两个选项后重试 |
| CB-002 | error | 同一题目内选项显示名重复 | 修改重复的选项名后重试 |
| CB-003 | error | 全局题目显示名重复或多题共用同一 field_id | 改题名或拆分 field_id |
| CB-004 | error | 前缀题型标记与行内标签冲突 | 以行内标签为准并人工确认后统一前缀 |
| CB-005 | error | 必答题的所有选项均为空判定 | 为至少一个选项补充关键词或提示词 |
| CB-006 | error | 属性行格式非法 | 检查 <属性=值> 配对与转义后重试 |
| CB-007 | error | 出现未知属性名或未知 flag | 改用受支持属性或更正拼写 |
| CB-008 | error | 游离文本 | 删除或改为注释行 |
| CB-101 | warning | 选项缺少关键词（仅有提示词） | 建议补充 3–5 个关键词 |
| CB-102 | warning | 关键词数量不在 3–5 个之间 | 调整关键词数量到偏好区间 |
| CB-103 | warning | 同一题目内两选项关键词集合存在交集 | 检查互斥性并去重关键词 |
| CB-104 | warning | 题目下缺少其他/未标示类选项 | 补充 <isOther> 兜底选项 |
| CB-105 | warning | 布尔运算符未大写或两侧未留半角空格 | 改为 AND/OR/NOT 且两侧各一空格 |
| CB-106 | warning | 同一题目内多个选项带 * | 只保留一个 * 或改用 <isRequired> |
| CB-107 | warning | 题目未声明必选且无可判定信号 | 补充关键词/提示词或显式标记必选/可选 |
| CB-108 | warning | is_other 选项被显式赋予关键词 | 确认该选项是否为真正兜底项 |
| CB-109 | error | @组别 早于任何 @维度 | 先写 @维度 再写 @组别 |
| CB-110 | error | 空维度或空组别 | 删除空标记或补充题目 |
| CB-111 | warning | 某维度下仅 1 个类目 | 确认维度切分是否过细 |
| CB-112 | warning | 题目未归属任何维度 | 显式添加 @维度/@组别 |
| CB-113 | warning | 不同维度/组别下存在同名题目 | 改题名或配置层级分隔符后再导出单层表 |
| DATA-101 | error | 文本编码探测失败 | 另存为 UTF-8 或提供编码提示后重试 |
| DATA-102 | error | 输入文件不存在 | 检查路径或先运行上游步骤 |
| DATA-103 | error | Schema 校验失败 | 对照 config/schema 修正字段后重试 |
| DATA-104 | error | 样本 ID 重复 | 去重 sample_id 后重试 |
| DATA-105 | error | 人读视图解析失败 | 检查 TXT 段标记与字段格式 |
| DATA-106 | error | 样本 TXT 缺少必需段 | 补齐［元数据］［正文］等段后重试 |
| DATA-107 | error | 单文件含多样本但未用样本边界包裹 | 使用［样本开始］/［样本结束］ |
| DATA-108 | error | 无法判定 TXT 类型 | 按命名约定重命名或添加 # STCX-TXT 标记 |
| DATA-201 | error | 必填元数据缺失 | 按变量配置补齐元数据字段 |
| DATA-202 | warning | 文本超长被截断 | 检查截断 flag 并确认是否接受 |
| TOOL-301 | error | 编码值不在词表 | 修正编码值或更新编码规则 |
| TOOL-302 | error | 必答题留空 | 为必答题给出至少一个编码值 |
| TOOL-401 | error | 裁决缺少 rule_ref | 为每条裁决补充规则依据 |
| TOOL-402 | error | 超出 max_audit_ratio 熔断 | 降低改动比例或提高阈值后重试 |
| TOOL-501 | error | 目标导出格式不支持 | 改用受支持格式或安装扩展模块 |
| TOOL-601 | error | 决策概率与选项不等长 | 检查模型输出对齐后再校准 |
| TOOL-602 | error | ECE 超限 | 重新校准或禁用决策编码器 |
| TOOL-603 | error | 准入未达标 | 决策编码器自动降级为 prefilter |
| TOOL-604 | error | 校准文件与编码规则哈希不匹配 | 规则升版后须重新校准 |
| RUN-201 | error | 依赖步骤未完成或缺少输入 | 先运行上游，或向 input_stage 放置已校验文件 |
| RUN-202 | error | run 目录已存在但哈希不符 | 使用新 run_id 或 --attach-run 核对 |
| RUN-203 | error | 工作区名非法 | 使用合法工作区名正则 |
| CFG-001 | error | 缺少必需配置项 | 在 config/default 或 config/{version} 中补齐该键 |
| LLM-401 | error | 模型认证失败 | 检查 STCX_LLM_*_API_KEY 后重试 |
| LLM-402 | error | 模型余额不足 | 充值或切换离线路由 |
| LLM-429 | error | 模型限流 | 降低并发或稍后重试 |
| LLM-451 | error | 内容审核拒答 | 检查样本并记入失败清单，勿静默丢弃 |
| REL-301 | warning | 信度退化 | 检查类目分布或补充样本 |
| REL-302 | error | 编码员不足 2 | 增加第二个独立编码员后再算信度 |
| REL-303 | warning | 信度口径不适用 | 改用适用口径或排除该字段 |
| REP-401 | error | 报告数字不一致 | 修复统计源后重新装配报告 |
| REP-402 | error | 报告章节缺失 | 检查报告模板与装配清单 |
| PKG-501 | error | 缺少 ffmpeg | 将 ffmpeg 放到 lib/bin/ffmpeg 或加入 PATH |
| PKG-502 | error | 缺少中文字体 | 将 OFL 字体放入 lib/fonts/ |
| PKG-503 | error | sidecar 不可执行 | 检查 bin/runtime 权限与架构 |
