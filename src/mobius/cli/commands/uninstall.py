"""Uninstall command for Mobius.

Cleanly reverses everything `mobius setup` did:
  1. MCP server registration  (~/.claude/mcp.json, ~/.codex/config.toml)
  2. CLAUDE.md integration block (<!-- mob:START --> … <!-- mob:END -->)
  3. Codex artifacts          (~/.codex/rules/mobius.md, ~/.codex/skills/mobius/)
  4. Data directory           (~/.mobius/)

Does NOT remove:
  - The Python package itself (user runs pip/uv/pipx uninstall separately)
  - The Claude Code plugin   (user runs `claude plugin uninstall mobius`)
  - Project source code or git history
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
from typing import Annotated

import typer

from mobius.cli.formatters import console
from mobius.cli.formatters.panels import (
    print_info,
    print_success,
    print_warning,
)

app = typer.Typer(
    name="uninstall",
    help="Cleanly remove Mobius from your system.",
)


# ── Removal helpers ──────────────────────────────────────────────
# Each returns True on success, False on skip/failure.
# Failures are reported via print_warning — never raise.


def _remove_claude_mcp(dry_run: bool) -> bool:
    """Remove mobius entry from ~/.claude/mcp.json."""
    mcp_path = Path.home() / ".claude" / "mcp.json"
    if not mcp_path.exists():
        return False

    try:
        data = json.loads(mcp_path.read_text())
    except (json.JSONDecodeError, OSError):
        print_warning("~/.claude/mcp.json is malformed — skipping.")
        return False
    servers = data.get("mcpServers", {})
    if "mobius" not in servers:
        return False

    if dry_run:
        print_info("[dry-run] Would remove mobius from ~/.claude/mcp.json")
        return True

    del servers["mobius"]
    try:
        mcp_path.write_text(json.dumps(data, indent=2) + "\n")
    except OSError:
        print_warning("Could not write ~/.claude/mcp.json — skipping.")
        return False
    print_success("Removed mobius from ~/.claude/mcp.json")
    return True


def _remove_codex_mcp(dry_run: bool) -> bool:
    """Remove mobius MCP section from ~/.codex/config.toml."""
    codex_config = Path.home() / ".codex" / "config.toml"
    if not codex_config.exists():
        return False

    try:
        raw = codex_config.read_text()
    except OSError:
        print_warning("~/.codex/config.toml is unreadable — skipping.")
        return False
    if "[mcp_servers.mobius]" not in raw:
        return False

    if dry_run:
        print_info("[dry-run] Would remove mobius from ~/.codex/config.toml")
        return True

    lines = raw.splitlines()
    output: list[str] = []
    skip = False
    in_comment_block = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("# Mobius MCP hookup"):
            in_comment_block = True
            continue
        if in_comment_block and stripped.startswith("#"):
            continue
        in_comment_block = False

        if stripped == "[mcp_servers.mobius]" or stripped.startswith("[mcp_servers.mobius."):
            skip = True
            continue
        if skip:
            if stripped.startswith("[") and stripped.endswith("]"):
                # Next TOML table header — stop skipping
                skip = False
                output.append(line)
            elif stripped.startswith("#"):
                # Comment after the managed section — preserve it
                skip = False
                output.append(line)
            # else: key=value lines or blank lines inside the table — skip them
            continue

        output.append(line)

    cleaned = re.sub(r"\n{3,}", "\n\n", "\n".join(output)).strip() + "\n"
    try:
        codex_config.write_text(cleaned)
    except OSError:
        print_warning("Could not write ~/.codex/config.toml — skipping.")
        return False
    print_success("Removed mobius from ~/.codex/config.toml")
    return True


def _remove_codex_artifacts(dry_run: bool) -> bool:
    """Remove Codex rules and skills installed by setup.

    Returns True only if ALL existing artifacts were removed successfully.
    Returns False if any artifact could not be removed.
    """
    rules_path = Path.home() / ".codex" / "rules" / "mobius.md"
    skills_path = Path.home() / ".codex" / "skills" / "mobius"
    had_work = False
    all_ok = True

    if rules_path.exists():
        had_work = True
        if dry_run:
            print_info(f"[dry-run] Would remove {rules_path}")
        else:
            try:
                rules_path.unlink()
                print_success(f"Removed {rules_path}")
            except OSError:
                print_warning(f"Could not remove {rules_path} — skipping.")
                all_ok = False

    if skills_path.exists():
        had_work = True
        if dry_run:
            print_info(f"[dry-run] Would remove {skills_path}/")
        else:
            try:
                shutil.rmtree(skills_path)
                print_success(f"Removed {skills_path}/")
            except OSError:
                print_warning(f"Could not remove {skills_path}/ — skipping.")
                all_ok = False

    return had_work and all_ok


def _remove_claude_md_block(project_dir: Path, dry_run: bool) -> bool:
    """Remove <!-- mob:START --> … <!-- mob:END --> block from CLAUDE.md."""
    claude_md = project_dir / "CLAUDE.md"
    if not claude_md.exists():
        return False

    try:
        content = claude_md.read_text()
    except OSError:
        print_warning(f"Could not read {claude_md} — skipping.")
        return False
    if "<!-- mob:START -->" not in content:
        return False

    if dry_run:
        print_info(f"[dry-run] Would remove mob block from {claude_md}")
        return True

    cleaned = re.sub(
        r"<!-- mob:START -->.*?<!-- mob:END -->\n?",
        "",
        content,
        flags=re.DOTALL,
    )
    try:
        claude_md.write_text(cleaned)
    except OSError:
        print_warning(f"Could not write {claude_md} — skipping.")
        return False
    print_success(f"Removed Mobius block from {claude_md}")
    return True


def _remove_data_dir(dry_run: bool) -> bool:
    """Remove ~/.mobius/ directory."""
    data_dir = Path.home() / ".mobius"
    if not data_dir.exists():
        return False

    if dry_run:
        print_info("[dry-run] Would remove ~/.mobius/")
        return True

    try:
        shutil.rmtree(data_dir)
    except OSError:
        print_warning("Could not fully remove ~/.mobius/ — partial cleanup.")
        return False
    print_success("Removed ~/.mobius/")
    return True


def _remove_project_dir(project_dir: Path, dry_run: bool) -> bool:
    """Remove .mobius/ directory in the current project."""
    mob_dir = project_dir / ".mobius"
    if not mob_dir.exists():
        return False

    if dry_run:
        print_info(f"[dry-run] Would remove {mob_dir}/")
        return True

    try:
        shutil.rmtree(mob_dir)
    except OSError:
        print_warning(f"Could not remove {mob_dir}/ — skipping.")
        return False
    print_success(f"Removed {mob_dir}/")
    return True


# ── CLI Command ──────────────────────────────────────────────────


@app.callback(invoke_without_command=True)
def uninstall(
    keep_data: Annotated[
        bool,
        typer.Option(
            "--keep-data",
            help="Keep entire ~/.mobius/ directory (config, credentials, seeds, logs, DB).",
        ),
    ] = False,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Show what would be removed without actually deleting.",
        ),
    ] = False,
    yes: Annotated[
        bool,
        typer.Option(
            "--yes",
            "-y",
            help="Skip confirmation prompt.",
        ),
    ] = False,
) -> None:
    """Cleanly remove all Mobius configuration from your system.

    Reverses everything `mobius setup` did. Does NOT remove the
    Python package itself — run `pip uninstall mobius-ai` separately.

    [dim]Examples:[/dim]
    [dim]    mobius uninstall              # interactive[/dim]
    [dim]    mobius uninstall -y           # no prompts[/dim]
    [dim]    mobius uninstall --dry-run    # preview only[/dim]
    [dim]    mobius uninstall --keep-data  # preserve ~/.mobius/[/dim]
    """
    console.print("\n[bold red]Mobius Uninstall[/bold red]\n")

    # Preview what will be removed
    targets: list[str] = []

    mcp_path = Path.home() / ".claude" / "mcp.json"
    if mcp_path.exists():
        try:
            mcp_data = json.loads(mcp_path.read_text())
            if "mobius" in mcp_data.get("mcpServers", {}):
                targets.append("MCP server registration (~/.claude/mcp.json)")
        except (json.JSONDecodeError, OSError):
            targets.append("MCP server registration (~/.claude/mcp.json — may be malformed)")

    codex_config = Path.home() / ".codex" / "config.toml"
    try:
        if codex_config.exists() and "[mcp_servers.mobius]" in codex_config.read_text():
            targets.append("Codex MCP config (~/.codex/config.toml)")
    except OSError:
        targets.append("Codex MCP config (~/.codex/config.toml — may be unreadable)")

    codex_rules = Path.home() / ".codex" / "rules" / "mobius.md"
    codex_skills = Path.home() / ".codex" / "skills" / "mobius"
    if codex_rules.exists() or codex_skills.exists():
        targets.append("Codex rules and skills (~/.codex/)")

    cwd = Path.cwd()
    claude_md = cwd / "CLAUDE.md"
    try:
        if claude_md.exists() and "<!-- mob:START -->" in claude_md.read_text():
            targets.append(f"CLAUDE.md integration block ({claude_md})")
    except OSError:
        pass

    mob_dir = cwd / ".mobius"
    if mob_dir.exists():
        targets.append(f"Project config ({mob_dir}/)")

    data_dir = Path.home() / ".mobius"
    if not keep_data and data_dir.exists():
        targets.append("Data directory (~/.mobius/)")

    if not targets:
        console.print("[green]Nothing to remove — Mobius is not installed.[/green]\n")
        raise typer.Exit()

    console.print("[bold]Will remove:[/bold]")
    for t in targets:
        console.print(f"  [red]-[/red] {t}")
    console.print()

    console.print("[bold]Will NOT remove:[/bold]")
    console.print("  [dim]- Python package (run: pip uninstall mobius-ai)[/dim]")
    console.print("  [dim]- Claude Code plugin (run: claude plugin uninstall mobius)[/dim]")
    console.print("  [dim]- Your project source code or git history[/dim]")
    if keep_data:
        console.print("  [dim]- ~/.mobius/ (--keep-data)[/dim]")
    console.print()

    if dry_run:
        console.print("[yellow]Dry run — no changes made.[/yellow]\n")
        raise typer.Exit()

    if not yes:
        confirm = typer.confirm("Proceed with uninstall?", default=False)
        if not confirm:
            print_info("Cancelled.")
            raise typer.Exit()

    # Execute removal — track failures only for items we expected to remove.
    # Each helper returns True on success, False on skip/failure.
    console.print()
    failed: list[str] = []

    if not _remove_claude_mcp(dry_run=False):
        # Only record as failed if we expected to clean it (was in targets)
        if any("mcp.json" in t for t in targets):
            failed.append("~/.claude/mcp.json")

    if not _remove_codex_mcp(dry_run=False):
        if any("codex/config.toml" in t for t in targets):
            failed.append("~/.codex/config.toml")

    if not _remove_codex_artifacts(dry_run=False):
        if any("Codex rules" in t for t in targets):
            failed.append("~/.codex/ rules/skills")

    if not _remove_claude_md_block(cwd, dry_run=False):
        if any("CLAUDE.md" in t for t in targets):
            failed.append("CLAUDE.md block")

    if not _remove_project_dir(cwd, dry_run=False):
        if any("Project config" in t for t in targets):
            failed.append(f"{cwd}/.mobius/")

    if not keep_data:
        if not _remove_data_dir(dry_run=False):
            if any("Data directory" in t for t in targets):
                failed.append("~/.mobius/")

    # Final summary
    console.print()
    if failed:
        console.print("[bold yellow]Mobius partially removed.[/bold yellow]")
        console.print("[yellow]Could not clean:[/yellow]")
        for s in failed:
            console.print(f"  [yellow]![/yellow] {s}")
        console.print()
    else:
        console.print("[bold green]Mobius has been removed.[/bold green]")
    console.print()
    console.print("[dim]To finish cleanup:[/dim]")
    console.print("  uv tool uninstall mobius-ai     [dim]# or: pip uninstall mobius-ai[/dim]")
    console.print("  claude plugin uninstall mobius   [dim]# if using Claude Code plugin[/dim]")
    console.print()
