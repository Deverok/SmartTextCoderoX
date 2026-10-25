# SmartTextCoderoX

离线优先的文本内容分析流水线：样本 + 编码规则 → 编码数据集、信效度证据、统计分析、图表与学术报告。

## 快速开始

```powershell
uv sync --group dev
uv run python script/dataset/make_fixture.py --out data/_example
uv run stcx-step --help
uv run stcx-tool --list
uv run pytest -q
```

工作区示例：

```powershell
uv run stcx-step ST01 --workspace v1 --dry-run
uv run stcx-tool codebook.parse --file config/v1/编码规则.txt
```

## 文档

- 需求规格：[`docs/需求规格说明书.md`](docs/需求规格说明书.md)（v2.4.1，唯一需求来源）
- Agent 规则：[`AGENTS.md`](AGENTS.md)
- 错误码：[`docs/dev/error-codes.md`](docs/dev/error-codes.md)
- MS0 验收：[`docs/dev/progress/MS0-验收报告.md`](docs/dev/progress/MS0-验收报告.md)

## 许可

Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
