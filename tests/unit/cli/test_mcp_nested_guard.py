"""Tests for _MOBIUS_NESTED sentinel guard.

Ensures that:
1. When _MOBIUS_NESTED=1 is set, the serve command exits with code 0 immediately
2. When _MOBIUS_NESTED is not set, serve() sets it to "1" in os.environ before
   starting the MCP server
"""

from __future__ import annotations

import os
from unittest.mock import patch

from typer.testing import CliRunner

from mobius.cli.commands.mcp import app

runner = CliRunner()


def test_nested_guard_exits_cleanly(monkeypatch):
    """Nested mobius MCP server should exit with code 0."""
    monkeypatch.setenv("_MOBIUS_NESTED", "1")
    result = runner.invoke(app, ["serve"])
    assert result.exit_code == 0


def test_serve_sets_nested_env_var(monkeypatch):
    """serve() should set _MOBIUS_NESTED=1 for child processes.

    We need to:
    1. Ensure _MOBIUS_NESTED is not set initially
    2. Mock asyncio.run to prevent actually starting a server
    3. Verify that _MOBIUS_NESTED was set to "1" before asyncio.run was called
    """
    monkeypatch.delenv("_MOBIUS_NESTED", raising=False)

    # Patch asyncio.run to capture os.environ state when it's called
    captured_env = {}

    def mock_asyncio_run(coro):
        # Capture the environment at the time asyncio.run is called
        captured_env["_MOBIUS_NESTED"] = os.environ.get("_MOBIUS_NESTED")
        # Don't actually run anything
        return None

    with patch("mobius.cli.commands.mcp.asyncio.run", side_effect=mock_asyncio_run):
        result = runner.invoke(app, ["serve"])

    # Should exit cleanly (no exception)
    assert result.exit_code == 0

    # _MOBIUS_NESTED should have been set to "1" before asyncio.run was called
    assert captured_env.get("_MOBIUS_NESTED") == "1"
