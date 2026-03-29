"""Plugin agent system for Mobius.

This package provides the agent orchestration engine:
- Agent Registry: Dynamic agent discovery and registration
- Agent Pool: Reusable agent pool with load balancing
- Agent Specs: Built-in agent specifications

Architecture:
- Extends the orchestrator AgentRuntime abstraction
- Integrates with routing.complexity for PAL routing
- Uses events.base for state tracking
"""

from mobius.plugin.agents.pool import (
    AgentInstance,
    AgentPool,
    AgentState,
    TaskRequest,
)
from mobius.plugin.agents.registry import (
    AgentRegistry,
    AgentRole,
    AgentSpec,
)

__all__ = [
    "AgentRegistry",
    "AgentRole",
    "AgentSpec",
    "AgentInstance",
    "AgentPool",
    "AgentState",
    "TaskRequest",
]
