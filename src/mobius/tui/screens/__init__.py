"""TUI screen modules.

This package contains the various screens for the Mobius TUI:
- Dashboard: Main monitoring view (legacy)
- DashboardV2: Tree-centric command center
- DashboardV3: Split view with node detail + enhanced graph (recommended)
- HUDDashboardScreen: Enhanced dashboard with HUD components (agents, tokens, progress, events)
- Execution: Detailed execution view
- Logs: Log viewer
- Debug: Debug/inspect view
"""

from mobius.tui.screens.confirm_rewind import ConfirmRewindScreen
from mobius.tui.screens.dashboard import DashboardScreen
from mobius.tui.screens.dashboard_v2 import DashboardScreenV2
from mobius.tui.screens.dashboard_v3 import DashboardScreenV3
from mobius.tui.screens.debug import DebugScreen
from mobius.tui.screens.execution import ExecutionScreen
from mobius.tui.screens.hud_dashboard import HUDDashboardScreen
from mobius.tui.screens.lineage_detail import LineageDetailScreen
from mobius.tui.screens.lineage_selector import LineageSelectorScreen
from mobius.tui.screens.logs import LogsScreen

__all__ = [
    "ConfirmRewindScreen",
    "DashboardScreen",
    "DashboardScreenV2",
    "DashboardScreenV3",
    "HUDDashboardScreen",
    "DebugScreen",
    "ExecutionScreen",
    "LineageDetailScreen",
    "LineageSelectorScreen",
    "LogsScreen",
]
