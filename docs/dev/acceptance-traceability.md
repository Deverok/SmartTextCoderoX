# Acceptance traceability (MS0)

| ACC ID | Test name(s) | Command | Notes |
|---|---|---|---|
| ACC-SCHEMA-01 | `test_ACC_SCHEMA_01_positive` | `uv run pytest tests/test_schema_contracts.py -q` | 6 schemas positive |
| ACC-SCHEMA-02 | `test_ACC_SCHEMA_02_negative_missing_required` | same | each schema fails on `{}` |
| ACC-WS-01 | `test_ACC_WS_01_verify_workspace_ok` | `uv run pytest tests/test_workspace_verify.py -q` | layout OK |
| ACC-WS-02 | `test_ACC_WS_02_detects_missing_dir` | same | intentional break |
| ACC-WS-03 | `test_ACC_WS_03_expect_broken_flag` | same | inverted exit |
| ACC-CFG-01…03 | `test_ACC_CFG_*` | `uv run pytest tests/test_config_failfast.py -q` | fail-fast |
| ACC-ERR-01…02 | `test_ACC_ERR_*` | `uv run pytest tests/test_error_catalog.py -q` | docs ↔ code |
| ACC-DEP-01…02 | `test_ACC_DEP_*` | `uv run pytest tests/test_dep_direction.py -q` | analytics ↛ agents |
| ACC-LOG-01 | `test_ACC_LOG_01_jsonl_fields` | `uv run pytest tests/test_logging_shape.py -q` | JSONL fields |
| ACC-CLI-01…04 | `test_ACC_CLI_*` | `uv run pytest tests/test_cli_skeleton.py -q` | help / dry-run / missing input |
| ACC-FIX-01…02 | `test_ACC_FIX_*` | `uv run pytest tests/test_fixture_roundtrip.py -q` | make_fixture |
| ACC-M1-01 | `test_ACC_M1_01_four_types_and_isAiCoded` | `uv run pytest tests/test_codebook_parse.py -q` | 4 types + isAiCoded |
| ACC-M1-02 | `test_ACC_M1_02_spelling_variants` | same | isRequired variants |
| ACC-M1-03 | `test_ACC_M1_03_txt_json_roundtrip` | same | TXT↔JSON |
| ACC-M1-04 | `test_ACC_M1_04_error_codes` / `…_warning_codes` | same | CB-001…113 |
| ACC-M1-05 | `test_ACC_M1_05_export_format_marker` | same | isomorphic markers; external import = manual once |
