"""PQBlocks MCP: Model Context Protocol Server for Post-Quantum Building Blocks."""

from .catalog import recommend, snippet, check_configuration, list_catalog
from .server import recommend_package, get_snippet, check_config, list_packages

__version__ = "0.1.0"
__all__ = [
    "recommend_package",
    "get_snippet",
    "check_config",
    "list_packages",
    "recommend",
    "snippet",
    "check_configuration",
    "list_catalog"
]
