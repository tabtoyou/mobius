# Clean Uninstall Guide

## One Command

```bash
mobius uninstall
```

This interactively removes all Mobius configuration:
- MCP server registration (`~/.claude/mcp.json`, `~/.codex/config.toml`)
- CLAUDE.md integration block (`<!-- mob:START -->` ... `<!-- mob:END -->`)
- Codex rules and skills (`~/.codex/rules/mobius.md`, `~/.codex/skills/mobius/`)
- Project-level config (`.mobius/`)
- Data directory (`~/.mobius/` — config, credentials, DB, seeds, logs, locks, prefs)

Then finish with:

```bash
uv tool uninstall mobius-ai            # or: pip uninstall mobius-ai
claude plugin uninstall mobius         # if using Claude Code plugin
```

### Options

| Flag | Effect |
|:-----|:-------|
| `-y`, `--yes` | Skip confirmation prompt |
| `--dry-run` | Preview what would be removed, change nothing |
| `--keep-data` | Keep entire `~/.mobius/` (config, credentials, seeds, DB, logs) |

### Inside Claude Code

Inside an active Claude Code session, type:

```
/mobius:setup --uninstall
```

This is a **skill command** (not a CLI flag) that removes MCP registration and the CLAUDE.md block interactively.

---

## What Lives Where

| Path | Created by | Contents |
|:-----|:-----------|:---------|
| `~/.claude/mcp.json` | `mob setup` / `mobius setup` | MCP server entry |
| `~/.codex/config.toml` | `mobius setup --runtime codex` | Codex MCP section |
| `~/.codex/rules/mobius.md` | `mobius setup --runtime codex` | Codex rules |
| `~/.codex/skills/mobius/` | `mobius setup --runtime codex` | Codex skills |
| `CLAUDE.md` | `mob setup` | Command reference block |
| `~/.mobius/config.yaml` | `mobius setup` | Runtime configuration |
| `~/.mobius/credentials.yaml` | `mobius setup` | API credentials |
| `~/.mobius/mobius.db` | First run | Event store + brownfield registry |
| `~/.mobius/seeds/` | `mob seed` / `mob interview` | Generated seed specs |
| `~/.mobius/data/` | `mob interview` | Interview state |
| `~/.mobius/logs/` | Any run | Log files |
| `~/.mobius/locks/` | `mob run` | Heartbeat locks |
| `~/.mobius/prefs.json` | `mob setup` | Preferences |
| `.mobius/` (project) | `mob evaluate` | Mechanical eval config |

## What Is NOT Removed

- Your project source code and git history
- Generated seed YAML files copied outside `~/.mobius/seeds/`
- Package manager caches (run `uv cache clean mobius-ai` or `pip cache purge` if needed)
