# AGENTS.md

Guidance for AI coding agents working in this repository.

- `src/pqblocks_mcp/catalog.json` is synced from https://pqblocks.github.io/catalog.json by
  `.github/workflows/sync-catalog.yml`. Never edit it by hand; the catalog is built in the
  `pqblocks.github.io` repository (`scripts/build_catalog.py --verify`).
- Every catalog entry must have `"verified": true`; `tests/test_server.py` enforces this.
- Package facts (functions, imports, install lines) come only from the packages. Do not add hand-written
  snippets or API descriptions to `catalog.py`.
- The server must keep working with no runtime dependencies (`--stdio-fallback`). The official SDK is optional.
- stdout carries the MCP protocol: log to stderr only.
- Run `pytest -q` before committing.
