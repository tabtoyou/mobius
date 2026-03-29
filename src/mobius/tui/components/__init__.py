"""TUI HUD components for orchestration visibility.

This package provides high-level HUD (Heads-Up Display) components
for monitoring agent orchestration in the TUI dashboard.

Components:
- agents_panel: Agent pool status display
- token_tracker: Real-time cost tracking
- progress: Visual progress indicators
- event_log: Scrollable event history
"""

from mobius.tui.components.agents_panel import AgentsPanel
from mobius.tui.components.event_log import EventLog
from mobius.tui.components.progress import ProgressTracker
from mobius.tui.components.token_tracker import TokenTracker

__all__ = [
    "AgentsPanel",
    "EventLog",
    "ProgressTracker",
    "TokenTracker",
]
