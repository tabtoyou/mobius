"""Mobius Plugin System - Auto-discovery and hot-reload.

This package provides:
- Agent Registry: Dynamic agent discovery and registration
- Agent Pool: Reusable agent pool with load balancing
- Skills Registry: Hot-reloading skill discovery
- Orchestration: Task scheduling and model routing

Architecture:
- Extends the orchestrator AgentRuntime abstraction
- Integrates with routing.complexity for PAL routing
- Uses events.base for state tracking

Usage:
    from mobius.plugin import AgentRegistry, AgentPool, SkillsRegistry

    # Discover agents and skills
    agent_registry = AgentRegistry()
    await agent_registry.discover_custom()

    # Create agent pool
    pool = AgentPool(adapter=adapter)
    await pool.start()

    # Or use the unified plugin manager
    from mobius.plugin import PluginManager

    manager = PluginManager()
    await manager.initialize()
"""

from mobius.plugin.agents import (
    AgentInstance,
    AgentPool,
    AgentRegistry,
    AgentRole,
    AgentSpec,
    AgentState,
    TaskRequest,
)
from mobius.plugin.orchestration import (
    ModelRouter,
    RoutingContext,
    ScheduledTask,
    Scheduler,
    SchedulerConfig,
    TaskGraph,
)
from mobius.plugin.skills import (
    SkillInstance,
    SkillMetadata,
    SkillRegistry,
    get_registry,
)

__all__ = [
    # Agents
    "AgentInstance",
    "AgentPool",
    "AgentRegistry",
    "AgentRole",
    "AgentSpec",
    "AgentState",
    "TaskRequest",
    # Orchestration
    "ModelRouter",
    "RoutingContext",
    "Scheduler",
    "SchedulerConfig",
    "ScheduledTask",
    "TaskGraph",
    # Skills
    "SkillInstance",
    "SkillMetadata",
    "SkillRegistry",
    "get_registry",
]
