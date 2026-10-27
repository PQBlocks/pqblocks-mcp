# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses semantic versioning.

## [Unreleased]

### Changed
- The package catalog is generated from the package repositories and synced from
  https://pqblocks.github.io/catalog.json on a schedule, so new packages appear automatically. Every quickstart is executed against its package before it is
  written; the test suite fails if any entry is unverified.
- `recommend_package` ranks packages by their own keywords, topics and summaries plus a small intent
  table, honours what a package's README says it does **not** do, and returns alternatives.
- `get_snippet` returns the executed README quickstart, example scripts and evidence links, warns when a
  quickstart seeds key generation, and no longer returns invented framework code.
- `check_config` matches algorithm names on word boundaries line by line (no more "RSA" inside
  "UNIVERSAL"), accepts the hybrid `X25519MLKEM768`, and adds DSA, lone X25519 / Ed25519, MD5, SHA-1,
  3DES and AES-128.
- Install lines are the ones that work today (PyPI when published, otherwise the GitHub repository).

### Fixed
- The previous catalog described functions that do not exist in the packages (for example
  `encrypt_jwe` / `generate_hybrid_keypair` in `pqblocks-jwe`, which does not encrypt). All snippets now
  come from the packages themselves.
- FastMCP tools are registered under the documented names (`recommend_package`, not
  `mcp_recommend_package`).
- The stdio transport no longer answers notifications, supports `ping`, negotiates the protocol
  version, and marks tool errors with `isError`.
- The SDK extra is pinned to `mcp<2`; v2 renamed FastMCP and the server fell back silently.

## [0.1.0]

### Added
- First release: four MCP tools (`recommend_package`, `get_snippet`, `check_config`, `list_packages`)
  over stdio, with optional FastMCP support.
