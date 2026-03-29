"""TUI widget modules.

This package contains reusable widgets for the Mobius TUI:
- PhaseProgress: Phase progress indicator showing Double Diamond phases
- ACTree: AC decomposition tree visualization
- ACProgress: AC progress list with status and timing
- DriftMeter: Drift score visualization with thresholds
- CostTracker: Cost and token usage display
- AgentActivity: Current agent tool/file/thinking display
- ParallelGraph: Parallel AC execution graph (Graph LR visualization)
"""

from mobius.tui.widgets.ac_progress import ACProgressItem, ACProgressWidget
from mobius.tui.widgets.ac_tree import ACTreeWidget
from mobius.tui.widgets.agent_activity import AgentActivityWidget
from mobius.tui.widgets.cost_tracker import CostTrackerWidget
from mobius.tui.widgets.drift_meter import DriftMeterWidget
from mobius.tui.widgets.lineage_tree import LineageTreeWidget
from mobius.tui.widgets.parallel_graph import GraphNode, ParallelGraphWidget
from mobius.tui.widgets.phase_progress import PhaseProgressWidget

__all__ = [
    "ACProgressItem",
    "ACProgressWidget",
    "ACTreeWidget",
    "AgentActivityWidget",
    "CostTrackerWidget",
    "DriftMeterWidget",
    "GraphNode",
    "LineageTreeWidget",
    "ParallelGraphWidget",
    "PhaseProgressWidget",
]
