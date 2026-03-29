"""Mobius Terminal User Interface module.

This module provides an interactive TUI for real-time workflow monitoring
using the Textual framework.

Key components:
- MobiusTUI: Main Textual app with keybindings
- Dashboard: Main monitoring view with status, phase progress, drift/cost
- Screens: Execution detail, log viewer, debug views
- Widgets: Phase progress, AC tree, drift meter, cost tracker

Usage:
    from mobius.tui import MobiusTUI

    app = MobiusTUI()
    await app.run_async()
"""

from mobius.tui.app import MobiusTUI

__all__ = ["MobiusTUI"]
