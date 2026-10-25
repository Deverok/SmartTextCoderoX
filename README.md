# SmartTextCoderoX
面向科研内容分析的 Agent 流水线。架构：静态区/工作区/运行区三层隔离，ST01–ST16 以 DAG 编排、跨环节只走文件契约（JSONL 权威 / TXT 人工面 / CSV 交付），确定性模块与可插拔智能体（Coder/Analyzer/Visualizer）解耦，每步 manifest 留痕、可复现可审计。功能：多模态转录→清洗抽样→四级类目编码（维度/组别/类目/编码值，AI+关键词双通路）→信度检验与分歧裁决→统计可视化→学术报告。Python 多包内核 + Electron/Vue，主适配DeepSeek大模型。
