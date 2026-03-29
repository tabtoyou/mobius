# Getting Started with Mobius

> **Single source of truth for onboarding.** All install and first-run instructions live here.
> Runtime-specific configuration lives in [runtime guides](runtime-guides/). Architecture concepts live in [architecture.md](architecture.md).

Transform a vague idea into a verified, working codebase -- with any AI coding agent.

---

## Quick Start

### Recommended: Claude Code (`mob`)

No Python install required. Run these three commands to go from idea to execution:

**1. Install the plugin** (in your terminal):
```bash
claude plugin marketplace add tabtoyou/mobius
claude plugin install mobius@mobius
```

**2. Set up and build** (inside a Claude Code session -- start one with `claude`):
```
mob setup
mob interview "Build a task management CLI"
mob run
```

That's it. `mob interview` runs a Socratic interview that auto-generates a seed spec, and `mob run` executes it.

> `mob` commands are Claude Code skills. They only work inside an active Claude Code session.
> `mob setup` registers the MCP server globally (one-time) and optionally configures your project.

---

### Alternative: Standalone CLI (`mobius`)

Use this path if you prefer a standalone terminal workflow, or are using a non-Claude runtime (e.g., Codex CLI).

**Requires Python >= 3.12.**

```bash
# Install
pip install mobius-ai

# Set up
mobius setup

# Run a seed spec
mobius run ~/.mobius/seeds/seed_abc123.yaml
```

> **Note:** The standalone CLI interview is invoked via `mobius init start "your context"` (not `mob interview`, which is Claude Code-specific). The interview flow is identical across both tools. Power users can also author seed YAML files directly — see the [Seed Authoring Guide](guides/seed-authoring.md).

> **Tip:** `mobius run` requires a path to a seed YAML file as a positional argument (e.g., `mobius run ~/.mobius/seeds/seed_<id>.yaml`).

---

## Installation Details

### Option 1: Claude Code Plugin (Recommended)

```bash
# Terminal
claude plugin marketplace add tabtoyou/mobius
claude plugin install mobius@mobius
```

Then inside a Claude Code session:
```
mob setup
mob help        # verify installation
```

No Python, pip, or API key configuration needed -- Claude Code handles the runtime.

### Option 2: pip Install

```bash
pip install mobius-ai              # Base package (core engine)
pip install mobius-ai[claude]      # + Claude Code runtime deps (anthropic, claude-agent-sdk)
pip install mobius-ai[litellm]     # + LiteLLM multi-provider support (100+ models)
pip install mobius-ai[dashboard]   # + Streamlit analytics dashboard (streamlit, plotly, pandas)
pip install mobius-ai[all]         # Everything (claude + litellm + dashboard)

mobius --version                   # verify CLI
```

> **Which extra do I need?** If you only use Claude Code as your runtime, `mobius-ai[claude]` is sufficient.
> For multi-model support via LiteLLM, use `mobius-ai[litellm]` or just grab everything with `mobius-ai[all]`.

**One-liner alternative** (auto-detects your runtime and installs matching extras):
```bash
curl -fsSL https://raw.githubusercontent.com/tabtoyou/mobius/main/scripts/install.sh | bash
```

### Option 3: From Source (Contributors)

```bash
git clone https://github.com/tabtoyou/mobius
cd mobius
uv sync                              # base dependencies only
uv sync --all-extras                  # or: include all optional extras
uv run mobius --version            # verify CLI
```

> See [CONTRIBUTING.md](../CONTRIBUTING.md) for the full contributor setup (linting, testing, pre-commit hooks).

### Prerequisites

| Path | Requirements |
|------|-------------|
| Claude Code (`mob`) | Claude Code with plugin support |
| Standalone CLI (`mobius`) | Python >= 3.12, API key (Anthropic or OpenAI) |
| Codex CLI backend | Python >= 3.12, `npm install -g @openai/codex`, OpenAI API key with access to GPT-5.4 |

---

## Configuration

### API Keys

```bash
# Claude-backed flows
export ANTHROPIC_API_KEY="your-anthropic-key"

# Codex-backed flows
export OPENAI_API_KEY="your-openai-key"
```

> Claude Code plugin users: your Claude Code session provides credentials automatically. No export needed.

### Configuration File

`mobius setup` creates `~/.mobius/config.yaml` with sensible defaults. To edit manually:

```yaml
orchestrator:
  runtime_backend: claude   # claude | codex

llm:
  backend: claude_code      # claude_code | codex | litellm

logging:
  level: info
```

For Codex CLI, the recommended documented baseline is GPT-5.4 with medium reasoning effort. Put Mobius per-role overrides in `~/.mobius/config.yaml`, not in `~/.codex/config.toml`:

```yaml
# ~/.mobius/config.yaml
orchestrator:
  runtime_backend: codex
  codex_cli_path: /usr/local/bin/codex

llm:
  backend: codex
  qa_model: gpt-5.4

clarification:
  default_model: gpt-5.4

evaluation:
  semantic_model: gpt-5.4

consensus:
  advocate_model: gpt-5.4
  devil_model: gpt-5.4
  judge_model: gpt-5.4
```

`mobius setup --runtime codex` uses `~/.codex/config.toml` only for the Codex MCP/env hookup and installs managed Mobius rules/skills into `~/.codex/`.

### Environment Variables

```bash
# Override the runtime backend (highest priority)
export MOBIUS_AGENT_RUNTIME=codex
```

Resolution order: `MOBIUS_AGENT_RUNTIME` env var > `config.yaml` > auto-detection during `mobius setup`.

For the full list of configuration keys, see [Configuration Reference](config-reference.md).

---

## Your First Workflow

This tutorial walks through a complete workflow. Examples use `mob` skills (Claude Code); CLI equivalents are shown in callouts for terminal-based workflows.

### Step 1: Interview

Inside a Claude Code session:
```
mob interview "I want to build a personal finance tracker"
```

> **CLI note:** The standalone CLI does not have an `interview` command. Use `mob interview` inside Claude Code, or use MCP tools to run interviews.

The Socratic Interviewer asks clarifying questions:
- "What platforms do you want to track?" (Bank accounts, credit cards, investments)
- "Do you need budgeting features?" (Yes, with category tracking)
- "Mobile app or web-based?" (Desktop-only with web export)
- "Data storage preference?" (SQLite, local file)

Answer until the ambiguity score drops below 0.2. The interview then auto-generates a seed spec:

```yaml
# Auto-generated seed (example)
goal: "Build a personal finance tracker with SQLite storage"
constraints:
  - "Desktop application only"
  - "Category-based budgeting"
  - "Export to CSV/Excel"
acceptance_criteria:
  - "Track income and expenses"
  - "Categorize transactions automatically"
  - "Generate monthly reports"
  - "Set and monitor budgets"
metadata:
  ambiguity_score: 0.15
  seed_id: "seed_abc123"
```

### Step 2: Execute

```
mob run
```

> **CLI equivalent:** `mobius run ~/.mobius/seeds/seed_abc123.yaml` (requires the seed file path as a positional argument)

Mobius decomposes the seed into tasks via the Double Diamond (Discover -> Define -> Design -> Deliver) and executes them through your configured runtime backend.

### Step 3: Monitor

Open a second terminal to watch progress in the TUI dashboard:

```bash
mobius monitor
```

The dashboard shows:
- Double Diamond phase progress
- Acceptance criteria tree with live status
- Cost, drift, and agent activity

See [TUI Usage Guide](guides/tui-usage.md) for keyboard shortcuts and screen details.

### Step 4: Review

`mob run` (or `mobius run`) prints a session summary with the QA verdict when complete.

Useful follow-ups:

```
mob evaluate          # Re-run 3-stage evaluation
mob status            # Check drift and session state
mob evolve            # Start evolutionary refinement loop
```

> **CLI equivalent:** `mobius run seed.yaml --resume <session_id>` to resume, `mobius run seed.yaml --debug` for verbose output.

---

## Common Workflows

### New Project from Scratch

```
mob interview "Build a REST API for a blog"
mob run
```

### Bug Fix

```
mob interview "User registration fails with email validation"
mob run
```

### Feature Enhancement

```
mob interview "Add real-time notifications to the chat app"
mob run
```

> **Terminal users:** The standalone CLI does not have an `interview` command. Generate seeds via `mob interview` in Claude Code or via MCP tools, then run with `mobius run <seed_file>`.

---

## Choosing a Runtime Backend

Mobius delegates code execution to a pluggable runtime backend. Two ship out of the box:

| | Claude Code | Codex CLI |
|---|---|---|
| **Best for** | Claude Code users; subscription billing | OpenAI ecosystem; pay-per-token billing |
| **Install** | `pip install mobius-ai[claude]` | `pip install mobius-ai` + `npm install -g @openai/codex` |
| **Skill shortcuts** | `mob` inside Claude Code | `mob` after `mobius setup --runtime codex` installs managed Codex skills |
| **Config value** | `claude` | `codex` |

Both backends run the same core workflow engine (seed execution, TUI). However, user-facing commands still differ: Claude Code has native in-session `mob` workflows, while Codex CLI relies on `mobius setup --runtime codex` to install managed rules/skills plus the MCP hookup. The `mobius` CLI remains the most universal terminal path, and some advanced operations are still MCP/Claude-only.

For backend-specific configuration:
- [Claude Code runtime guide](runtime-guides/claude-code.md)
- [Codex CLI runtime guide](runtime-guides/codex.md)

---

## Troubleshooting

### Claude Code skill not recognized

```bash
# Check skill is installed
claude plugin list

# Reinstall if needed
claude plugin install mobius@mobius --force
```

### Python / CLI issues

```bash
python --version            # Must be >= 3.12
pip install --force-reinstall mobius-ai
mobius --version
```

### API key not found

```bash
export ANTHROPIC_API_KEY="your-key"     # or OPENAI_API_KEY
env | grep -E 'ANTHROPIC|OPENAI'        # verify
```

### MCP server issues

```bash
mobius mcp info
mobius mcp serve
```

### TUI not displaying

```bash
export TERM=xterm-256color
mobius tui monitor
```

### Stuck execution

Inside Claude Code:
```
mob unstuck
```

From terminal:
```bash
mobius run seed.yaml --resume <session_id>
mobius cancel execution <session_id>
```

### Quick Reference

| Issue | Solution |
|-------|----------|
| Skill not loaded | `claude plugin install mobius@mobius --force` |
| CLI not found | `pip install mobius-ai` |
| API errors | Check `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` |
| TUI blank | `export TERM=xterm-256color` |
| High costs | Reduce seed scope or use a lower model tier |
| Execution stuck | `mob unstuck` or `mobius run seed.yaml --resume <id>` |

---

## Best Practices

### For Better Interviews
1. **Be specific** -- "build a Twitter clone with real-time messaging" beats "build a social app"
2. **State constraints early** -- budget, timeline, technical limitations
3. **Define success** -- clear acceptance criteria produce better seeds

### For Effective Seeds
1. **Include non-functional requirements** -- performance, security, scalability
2. **Define boundaries** -- what is in scope and what is not
3. **Specify integrations** -- APIs, databases, third-party services

### For Successful Execution
1. **Validate first** -- `mobius run seed.yaml --dry-run` checks YAML and schema before executing
2. **Monitor with the TUI** -- run `mobius monitor` in a separate terminal during long workflows
3. **Keep QA enabled** -- post-execution QA runs automatically unless you pass `--no-qa`

---

## Next Steps

- [Seed Authoring Guide](guides/seed-authoring.md) -- advanced seed customization
- [Evaluation Pipeline](guides/evaluation-pipeline.md) -- understand the 3-stage verification gate
- [TUI Usage Guide](guides/tui-usage.md) -- dashboard screens and keyboard shortcuts
- [Architecture](architecture.md) -- system design and component overview
- [Configuration Reference](config-reference.md) -- all config keys and defaults
- [Claude Code runtime guide](runtime-guides/claude-code.md) -- backend-specific setup
- [Codex CLI runtime guide](runtime-guides/codex.md) -- backend-specific setup

Need help? Open an issue on [GitHub](https://github.com/tabtoyou/mobius/issues).
