"""MCP Client package.

This package provides MCP client functionality for connecting to external
MCP servers and using their tools, resources, and prompts.

Public API:
    MCPClient: Protocol defining the client interface
    MCPClientAdapter: Concrete implementation using the MCP SDK
    MCPClientManager: Manager for multiple server connections
"""

from mobius.mcp.client.adapter import MCPClientAdapter
from mobius.mcp.client.manager import MCPClientManager
from mobius.mcp.client.protocol import MCPClient

__all__ = [
    "MCPClient",
    "MCPClientAdapter",
    "MCPClientManager",
]
