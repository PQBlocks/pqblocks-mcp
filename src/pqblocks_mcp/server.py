"""PQBlocks MCP Server: PQC & Quantum-Inspired Optimization Helper for AI Coding Assistants.

Implements the official Model Context Protocol (MCP) exposing 4 core tools:
- recommend_package: Maps developer task to the optimal PQBlocks library.
- get_snippet: Returns the README quickstart, executed when the catalog was built, with install instructions.
- check_config: Analyzes code/configs to flag classical-only crypto and missing hybrid modes.
- list_packages: Lists every package by area of the post-quantum transition.

Supports both FastMCP and a zero-dependency standard library stdio JSON-RPC protocol.
"""

import sys
import json
import logging
from typing import Dict, Any, Optional, List

from . import catalog

# stdout carries the protocol; logs go to stderr
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", stream=sys.stderr)
logger = logging.getLogger("pqblocks-mcp")
VERSION = "0.1.0"
PROTOCOLS = ("2025-06-18", "2025-03-26", "2024-11-05")   # newest first
DESCRIPTIONS = {
    "recommend_package": "Pick the PQBlocks package for a task described in plain words (e.g. 'sign JWTs with "
                         "ML-DSA', 'find RSA in my repo', 'solve a QUBO'). Returns the package, why, its install "
                         "line, a quickstart verified to run, docs links and alternatives.",
    "get_snippet": "Install line, import name and the README quickstart for one PQBlocks package. Every quickstart "
                   "was executed against the package source when the catalog was built; use it as-is rather than "
                   "guessing an API.",
    "check_config": "Scan pasted code or config for quantum-vulnerable public-key algorithms (RSA, ECDSA, ECDH, "
                    "DH, DSA, lone X25519/Ed25519) and classically weak ones (MD5, SHA-1, 3DES, AES-128); returns "
                    "line-numbered findings, replacements and matching packages.",
    "list_packages": "List every PQBlocks package with area, status, version and the install line that works "
                     "today. Optional category filter: 'PQ cryptography', 'Migration & readiness', "
                     "'Interoperability', 'Conformance', 'Quantum-inspired'.",
}


def recommend_package(task_description: str) -> Dict[str, Any]:
    """Recommend the optimal PQBlocks library for a specific post-quantum or optimization task."""
    return catalog.recommend(task_description)


def get_snippet(package: str, framework: Optional[str] = "python") -> Dict[str, Any]:
    """Provide production-ready, runnable code snippets for a specified PQBlocks package."""
    return catalog.snippet(package, framework)


def check_config(code_or_config: str) -> Dict[str, Any]:
    """Audit code or configuration strings for deprecated classical crypto and policy gaps."""
    return catalog.check_configuration(code_or_config)


def list_packages(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """List all available PQBlocks packages, standards, and install targets."""
    return catalog.list_catalog(category)


# Try initializing FastMCP if available
_fastmcp_app = None
try:
    from mcp.server.fastmcp import FastMCP
    _fastmcp_app = FastMCP("pqblocks-mcp")

    @_fastmcp_app.tool(name='recommend_package', description=DESCRIPTIONS['recommend_package'])
    def _recommend_package(task_description: str) -> str:
        """Recommend the right PQBlocks package for a crypto or optimization task."""
        return json.dumps(recommend_package(task_description), indent=2)

    @_fastmcp_app.tool(name='get_snippet', description=DESCRIPTIONS['get_snippet'])
    def _get_snippet(package: str, framework: str = "python") -> str:
        """Get tested, copy-paste code snippets for a PQBlocks package."""
        return json.dumps(get_snippet(package, framework), indent=2)

    @_fastmcp_app.tool(name='check_config', description=DESCRIPTIONS['check_config'])
    def _check_config(code_or_config: str) -> str:
        """Check code or config for classical-only crypto algorithms requiring migration."""
        return json.dumps(check_config(code_or_config), indent=2)

    @_fastmcp_app.tool(name='list_packages', description=DESCRIPTIONS['list_packages'])
    def _list_packages(category: Optional[str] = None) -> str:
        """List PQBlocks packages by transition category (PQ cryptography, Migration & readiness, Interoperability, Conformance, Quantum-inspired)."""
        return json.dumps(list_packages(category), indent=2)

except ImportError:
    pass


def run_stdio_jsonrpc():
    """Fallback zero-dependency JSON-RPC stdio protocol handler."""
    logger.info("Running PQBlocks MCP server in stdio JSON-RPC mode")
    tools = [
        {
            "name": "recommend_package",
            "description": DESCRIPTIONS["recommend_package"],
            "inputSchema": {
                "type": "object",
                "properties": {"task_description": {"type": "string"}},
                "required": ["task_description"]
            }
        },
        {
            "name": "get_snippet",
            "description": DESCRIPTIONS["get_snippet"],
            "inputSchema": {
                "type": "object",
                "properties": {
                    "package": {"type": "string"},
                    "framework": {"type": "string", "default": "python"}
                },
                "required": ["package"]
            }
        },
        {
            "name": "check_config",
            "description": DESCRIPTIONS["check_config"],
            "inputSchema": {
                "type": "object",
                "properties": {"code_or_config": {"type": "string"}},
                "required": ["code_or_config"]
            }
        },
        {
            "name": "list_packages",
            "description": DESCRIPTIONS["list_packages"],
            "inputSchema": {
                "type": "object",
                "properties": {"category": {"type": "string"}},
                "required": []
            }
        }
    ]

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue

        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params") or {}
        if "id" not in req:          # a notification: never answered
            continue

        if method == "initialize":
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": params.get("protocolVersion") if params.get("protocolVersion") in PROTOCOLS else PROTOCOLS[0],
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "pqblocks-mcp", "version": VERSION}
                }
            }
        elif method == "tools/list":
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": tools}
            }
        elif method == "tools/call":
            tool_name = params.get("name")
            args = params.get("arguments", {})
            try:
                if tool_name == "recommend_package":
                    res = recommend_package(args.get("task_description", ""))
                elif tool_name == "get_snippet":
                    res = get_snippet(args.get("package", ""), args.get("framework", "python"))
                elif tool_name == "check_config":
                    res = check_config(args.get("code_or_config", ""))
                elif tool_name == "list_packages":
                    res = list_packages(args.get("category"))
                else:
                    res = {"error": f"Unknown tool: {tool_name}"}

                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(res, indent=2)}],
                        "isError": "error" in res,
                    }
                }
            except Exception as e:
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32000, "message": str(e)}
                }
        elif method == "ping":
            resp = {"jsonrpc": "2.0", "id": req_id, "result": {}}
        else:
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Method {method} not found"}
            }

        sys.stdout.write(json.dumps(resp) + "\n")
        sys.stdout.flush()


def main():
    if _fastmcp_app is not None and "--stdio-fallback" not in sys.argv:
        _fastmcp_app.run()
    else:
        run_stdio_jsonrpc()


if __name__ == "__main__":
    main()
