# AGENTS.md

Guidance for AI coding agents working in this repository.

- `src/pqblocks_mcp/catalog.json` is generated. Never edit it by hand. Rebuild it from the package sources:
  `python3 scripts/build_catalog.py <packages-dir> --verify` (needs each package's dependencies and liboqs).
- Every catalog entry must have `"verified": true`; `tests/test_server.py` enforces this.
- Package facts (functions, imports, install lines) come only from the packages. Do not add hand-written
  snippets or API descriptions to `catalog.py`.
- The server must keep working with no runtime dependencies (`--stdio-fallback`). The official SDK is optional.
- stdout carries the MCP protocol: log to stderr only.
- Run `pytest -q` before committing.
