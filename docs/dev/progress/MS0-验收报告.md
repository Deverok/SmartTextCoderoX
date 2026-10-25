# MS0 验收报告 — 契约与骨架

**日期**：2026-10-25  
**分支**：`feat/ms0-contracts`  
**规格**：v2.4.1 §12 / §14（契约 · 编码规则 · 工作区）

## DoD 清单

| 项 | 结果 | 证据 |
|---|---|---|
| `uv run stcx-step --help` | PASS | 输出含 `--workspace` / `--dry-run` |
| `uv run stcx-tool --help` | PASS | 输出含 `--list` / `--dry-run` |
| 六 Schema 正例+反例 | PASS | `tests/test_schema_contracts.py`（12 cases） |
| `pytest` 全绿 | PASS | `uv run pytest -q` → **58 passed** |
| CI 骨架（3.10–3.13） | PASS（文件就绪） | `.github/workflows/ci.yml`；本地同质量门 |
| `verify_workspace` 检出破坏 | PASS | `test_ACC_WS_02_*` |
| 错误码表 ↔ 常量 | PASS | `docs/dev/error-codes.md` + `test_ACC_ERR_*` |
| 合成 fixture 往返 | PASS | `make_fixture` + `test_ACC_FIX_01_*` |
| ACC-M1 解析与往返 | PASS | `tests/test_codebook_parse.py` |

## §14 域对照

| 域 | 状态 | 说明 |
|---|---|---|
| 契约 | PASS | Schema ×6；TXT↔JSON 往返（codebook/sample） |
| 编码规则 | PASS | 四题型、拼写变体、CB-* 用例；ACC-M1-05 外部导入待人工 1 次 |
| 工作区 | PASS | 静态/运行分区落地；`STCX_WORKSPACES_ROOT` 路径解析就绪 |

## 默认假设（§15.4）

- **O2**：使用合成 fixture；`TODO(DECISION)` 留在 `data/_example/README.md` 与 `make_fixture.py`。
- Schema 字段以附录 B + §16.3 补齐（含 `evidence_source` / `hierarchy_path` / `layer` / `invocation_id`）。
- `requires-python = ">=3.10"`（本机可用 3.13/3.14 开发）。

## 未通过 / 延后

| 项 | 原因 |
|---|---|
| ACC-M1-05 外部平台人工导入 | 需人工一次；自动化仅断言同构标记 |
| 完整 ST02–ST15 / 38 工具 | 属 MS1+；MS0 仅骨架与 codebook/samples 薄封装 |
| 静态区只读安装探测 | `verify_workspace --probe-static-writable` 已实现；开发树默认可写属预期 |

## 复现命令

```powershell
uv sync --group dev
uv run python script/dataset/make_fixture.py --out data/_example
uv run python script/maintenance/verify_workspace.py
uv run ruff check .
uv run mypy src
uv run pytest -q
uv run stcx-step --help
uv run stcx-tool --help
```
