"""Routing module for Mobius.

This module handles model tier routing and selection, including:
- Tier enumeration and configuration (Frugal, Standard, Frontier)
- Complexity estimation for routing decisions
- PAL (Progressive Adaptive LLM) router for automatic tier selection
- Escalation on failure with automatic tier upgrades
- Downgrade on success for cost optimization
"""

from mobius.routing.complexity import (
    ComplexityScore,
    TaskContext,
    estimate_complexity,
)
from mobius.routing.downgrade import (
    DOWNGRADE_THRESHOLD,
    SIMILARITY_THRESHOLD,
    DowngradeManager,
    DowngradeResult,
    PatternMatcher,
    SuccessTracker,
)
from mobius.routing.escalation import (
    FAILURE_THRESHOLD,
    EscalationAction,
    EscalationManager,
    FailureTracker,
    StagnationEvent,
)
from mobius.routing.router import PALRouter, RoutingDecision, route_task
from mobius.routing.tiers import Tier, get_model_for_tier, get_tier_config

__all__ = [
    # Tiers
    "Tier",
    "get_model_for_tier",
    "get_tier_config",
    # Complexity
    "TaskContext",
    "ComplexityScore",
    "estimate_complexity",
    # Router
    "PALRouter",
    "RoutingDecision",
    "route_task",
    # Escalation
    "EscalationManager",
    "EscalationAction",
    "FailureTracker",
    "StagnationEvent",
    "FAILURE_THRESHOLD",
    # Downgrade
    "DowngradeManager",
    "DowngradeResult",
    "SuccessTracker",
    "PatternMatcher",
    "DOWNGRADE_THRESHOLD",
    "SIMILARITY_THRESHOLD",
]
