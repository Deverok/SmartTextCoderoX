# Schema migrations

When a contract in `config/schema/` changes:

1. Bump `schema_version` in affected documents.
2. Add a migration script under `script/maintenance/`.
3. Document the change here and in `CHANGELOG.md`.

MS0 baseline: all schemas at `schema_version` **1.0**.
