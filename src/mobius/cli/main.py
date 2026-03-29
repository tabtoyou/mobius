"""Mobius CLI main entry point.

This module defines the main Typer application and registers
all command groups for the Mobius CLI.

Command shortcuts (v0.8.0+):
    mobius run seed.yaml          # shorthand for: mobius run workflow seed.yaml
    mobius init "Build an API"    # shorthand for: mobius init start "Build an API"
    mobius monitor                # shorthand for: mobius tui monitor
"""

from typing import Annotated

import typer

from mobius import __version__
from mobius.cli.commands import cancel, config, init, mcp, pm, run, setup, status, tui, uninstall
from mobius.cli.formatters import console

# Create the main Typer app
app = typer.Typer(
    name="mobius",
    help="Mobius - Self-Improving AI Workflow System",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

# Register command groups
app.add_typer(init.app, name="init")
app.add_typer(run.app, name="run")
app.add_typer(config.app, name="config")
app.add_typer(status.app, name="status")
app.add_typer(cancel.app, name="cancel")
app.add_typer(mcp.app, name="mcp")
app.add_typer(setup.app, name="setup")
app.add_typer(tui.app, name="tui")
app.add_typer(pm.app, name="pm")
app.add_typer(uninstall.app, name="uninstall")


# Top-level convenience aliases
@app.command(hidden=True)
def monitor(
    backend: Annotated[
        str,
        typer.Option(
            "--backend",
            help="TUI backend to use: 'python' (default) or 'slt' (native binary).",
        ),
    ] = "python",
) -> None:
    """Launch the TUI monitor (shorthand for 'mobius tui monitor')."""
    tui.monitor_command(backend=backend)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"[bold cyan]Mobius[/] version [green]{__version__}[/]")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            "-V",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit.",
        ),
    ] = None,
) -> None:
    """Mobius - Self-Improving AI Workflow System.

    A self-improving AI workflow system with 6 phases:
    Big Bang, PAL Router, Execution, Resilience, Evaluation, and Consensus.

    [bold]Quick Start:[/]

        mobius init "Build a REST API"     Start interview
        mobius run seed.yaml               Execute workflow
        mobius monitor                     Launch TUI monitor

    Use [bold cyan]mobius COMMAND --help[/] for command-specific help.
    """
    pass


__all__ = ["app", "main"]
