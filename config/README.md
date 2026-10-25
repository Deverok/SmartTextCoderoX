# config/

| Path | Role | Git |
|---|---|---|
| `default/` | Project-wide defaults (app, llm, palette, …) | yes |
| `schema/` | JSON Schema contracts (`*.schema.json`) | yes |
| `{version}/` | Per-workspace research design (编码规则, 变量配置, …) | yes |

Runtime must treat this tree as **read-only**. Version overlays win over `default/`.
Missing required keys fail fast — no silent defaults.
