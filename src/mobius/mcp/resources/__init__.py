"""MCP Resources package.

This package provides resource handlers for the MCP server.

Public API:
    MOBIUS_RESOURCES: List of available resource definitions
    Resource handlers for seeds, sessions, and events
"""

from mobius.mcp.resources.handlers import (
    MOBIUS_RESOURCES,
    events_handler,
    seeds_handler,
    sessions_handler,
)

__all__ = [
    "MOBIUS_RESOURCES",
    "seeds_handler",
    "sessions_handler",
    "events_handler",
]
