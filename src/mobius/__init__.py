"""Mobius - Self-Improving AI Workflow System.

A workflow system that uses Socratic questioning and ontological analysis
to transform ambiguous requirements into executable specifications.

Example:
    # Using CLI
    mobius init start "I want to build a task management CLI"
    mobius run workflow seed.yaml

    # Using Python
    from mobius.core import Result, ValidationError
    from mobius.bigbang import InterviewEngine
"""

try:
    from mobius._version import __version__
except ModuleNotFoundError:
    try:
        from importlib.metadata import version as _v

        __version__ = _v("mobius-ai")
    except Exception:
        __version__ = "0+unknown"

__all__ = ["__version__", "main"]


def main() -> None:
    """Main entry point for the Mobius CLI.

    This function invokes the Typer app from mobius.cli.main.
    """
    from mobius.cli.main import app

    app()
