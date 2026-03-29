# API Reference

This section provides detailed API documentation for the Mobius Python library.

## Modules

### Core Module

The [Core Module](./core.md) provides foundational types and utilities:

- **Result** - Generic type for handling expected failures
- **Seed** - Immutable workflow specification
- **Error Hierarchy** - Structured exception types
- **Type Aliases** - Common domain types

```python
from mobius.core import Result, Seed, MobiusError
```

### MCP Module

The [MCP Module](./mcp.md) provides Model Context Protocol integration:

- **MCPClient** - Connect to external MCP servers
- **MCPServer** - Expose Mobius as an MCP server
- **ToolRegistry** - Manage MCP tools
- **Error Types** - MCP-specific exceptions

```python
from mobius.mcp import MCPClientAdapter, MCPServerAdapter, MCPError
```

## Quick Reference

### Core Types

| Type | Description | Import |
|------|-------------|--------|
| `Result[T, E]` | Success/failure container | `from mobius.core import Result` |
| `Seed` | Immutable workflow spec | `from mobius.core import Seed` |
| `MobiusError` | Base exception | `from mobius.core import MobiusError` |

### MCP Types

| Type | Description | Import |
|------|-------------|--------|
| `MCPClientAdapter` | MCP client implementation | `from mobius.mcp.client import MCPClientAdapter` |
| `MCPServerAdapter` | MCP server implementation | `from mobius.mcp.server import MCPServerAdapter` |
| `MCPToolDefinition` | Tool definition | `from mobius.mcp import MCPToolDefinition` |
| `MCPError` | Base MCP exception | `from mobius.mcp import MCPError` |

## See Also

- [Getting Started](../getting-started.md) - Install and onboarding guide
