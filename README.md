# pqblocks-mcp

An MCP server that tells AI coding agents which PQBlocks package to use, with install lines and quickstarts verified to run.
Use it in Claude Code, Claude Desktop, Cursor, VS Code or any Model Context Protocol client when you add or migrate post-quantum cryptography, audit code for RSA and ECC, or pick a quantum-inspired solver.
Implements the Model Context Protocol over stdio (protocol versions 2024-11-05, 2025-03-26 and 2025-06-18).

```bash
claude mcp add pqblocks -- uvx --from git+https://github.com/PQBlocks/pqblocks-mcp pqblocks-mcp
```

[![CI](https://github.com/PQBlocks/pqblocks-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/PQBlocks/pqblocks-mcp/actions/workflows/ci.yml)
![Runtime dependencies](https://img.shields.io/badge/runtime%20deps-none-334155?style=flat-square)
![Python](https://img.shields.io/badge/python-%3E%3D3.10-1e40af?style=flat-square)
![Licence](https://img.shields.io/badge/licence-Apache--2.0-334155?style=flat-square)
[![Docs](https://img.shields.io/badge/docs-pqblocks.github.io-0e7490?style=flat-square)](https://pqblocks.github.io/ai/mcp/)

## Why PQBlocks MCP

Ask an assistant to "add post-quantum encryption" and it will often invent a function name. This server answers from a catalog generated from the 26 PQBlocks packages themselves, in which **every quickstart was executed against its package** before it was written. The agent gets a real package, the install line that works today and code that runs.

```mermaid
flowchart LR
    A[Agent: "sign JWTs with ML-DSA"] -->|recommend_package| S[pqblocks-mcp]
    S --> C[(catalog.json<br/>26 packages<br/>quickstarts executed)]
    S -->|package · install · import · quickstart · docs| A
    A -->|get_snippet / check_config| S
```

## Install

| Client | Configuration |
|---|---|
| **Claude Code** | `claude mcp add pqblocks -- uvx --from git+https://github.com/PQBlocks/pqblocks-mcp pqblocks-mcp` |
| **Claude Desktop** | `claude_desktop_config.json` → `"pqblocks": {"command": "uvx", "args": ["--from", "git+https://github.com/PQBlocks/pqblocks-mcp", "pqblocks-mcp"]}` under `mcpServers` |
| **Cursor** | `.cursor/mcp.json` → same entry under `mcpServers` |
| **VS Code** | `.vscode/mcp.json` → `"pqblocks": {"type": "stdio", "command": "uvx", "args": ["--from", "git+https://github.com/PQBlocks/pqblocks-mcp", "pqblocks-mcp"]}` under `servers` |
| **Any client, with pip** | `pip install git+https://github.com/PQBlocks/pqblocks-mcp`, then run `pqblocks-mcp` |

The server has **no runtime dependencies**: it speaks MCP over stdio with its own small JSON-RPC implementation. Install the `sdk` extra (`pqblocks-mcp[sdk]`) to use the official MCP Python SDK transport instead.

## Usage

### Tools

| Tool | Input | Returns |
|---|---|---|
| `recommend_package` | `task_description` | Best package, why, install, import, executed quickstart, docs, alternatives |
| `get_snippet` | `package` (full or short name), `framework` (optional) | Install, import, executed quickstart, example scripts, evidence documents, warnings |
| `check_config` | `code_or_config` | Line-numbered findings: RSA, ECDSA, ECDH / NIST curves, DH, DSA, lone X25519 / Ed25519, MD5, SHA-1, 3DES, AES-128, with replacements and packages |
| `list_packages` | `category` (optional area) | All packages with area, version, status, install line |

### From Python

The tools are plain functions too:

```python
from pqblocks_mcp.server import check_config, recommend_package

print(recommend_package("find RSA usage in my repo")["recommended_package"])   # pqblocks-scan
for f in check_config('key = rsa.generate_private_key(key_size=2048)')["findings"]:
    print(f["line"], f["algorithm"], "->", f["replace_with"])
```

## API reference

| Function | Signature |
|---|---|
| `recommend_package` | `(task_description: str) -> dict` |
| `get_snippet` | `(package: str, framework: str = "python") -> dict` |
| `check_config` | `(code_or_config: str) -> dict` |
| `list_packages` | `(category: str \| None = None) -> list[dict]` |
| `main` | Console entry point `pqblocks-mcp`; `--stdio-fallback` forces the built-in transport |

## Security notes

- The server reads only its bundled catalog. It makes no network calls and executes no code it receives.
- `check_config` is a pattern match on algorithm names. It cannot see algorithms chosen at runtime or hidden behind library defaults, and it says so in every response. Use [`pqblocks-scan`](https://pqblocks.github.io/packages/scan/) for a whole repository.
- Recommendations point to pre-1.0 packages that are not FIPS 140-3 / CMVP validated or externally audited; each package's `SECURITY_NOTES.md` has the details.

## Verification

- `tests/test_server.py` checks that all 26 catalog entries are verified and parse, that 22 realistic tasks route to the right package, that a package is never recommended for something its README says it does not do, that the config checker has no false positives on hybrid names, and the full stdio protocol (initialize, notifications, tools/list, tools/call, errors, ping).
- The catalog is rebuilt with `python3 scripts/build_catalog.py <packages-dir> --verify`, which runs every quickstart and records the result.

```bash
pip install -e ".[test]" && pytest -q
```

## Part of PQBlocks, a QubitRock project

[PQBlocks](https://pqblocks.github.io) builds verified building blocks for the post-quantum era. See also [`pqblocks-skills`](https://github.com/PQBlocks/pqblocks-skills) (Claude skill, Cursor rule, AGENTS.md) and the [package catalog](https://pqblocks.github.io/packages/). Licensed under Apache-2.0.
