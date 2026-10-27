# pqblocks-mcp

Model Context Protocol (MCP) server for post-quantum cryptography packages and quantum-inspired optimization.
When to use it: connect AI coding assistants (Claude Code, Cursor, Windsurf, Copilot) to the PQBlocks ecosystem.
Standard it implements: Model Context Protocol (2024-11-05).

```bash
pip install pqblocks-mcp
```

## Quick Start (MCP Client Configuration)

### Claude Desktop / Claude Code (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "pqblocks": {
      "command": "uvx",
      "args": ["pqblocks-mcp"]
    }
  }
}
```

### Cursor (`.cursor/mcp.json`)

```json
{
  "mcpServers": {
    "pqblocks": {
      "command": "python",
      "args": ["-m", "pqblocks_mcp.server"]
    }
  }
}
```

## Available MCP Tools

| Tool | Parameters | What it returns |
|---|---|---|
| `recommend_package` | `task_description` (str) | The right `pqblocks-*` package, reasoning, standards and quick snippet |
| `get_snippet` | `package` (str), `framework` (str) | Ready-to-run copy-paste code with install commands |
| `check_config` | `code_or_config` (str) | Detects classical-only crypto (RSA, ECDSA) and advises PQC migration |
| `list_packages` | `category` (optional str) | Full package catalog categorized by transition domain |

## Part of PQBlocks — a QubitRock project
Licensed under Apache-2.0.
