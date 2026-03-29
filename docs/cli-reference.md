<!--
doc_metadata:
  runtime_scope: [local, claude, codex]
-->

# CLI Reference

Complete command reference for the Mobius CLI.

## Installation

> For install instructions, onboarding, and first-run setup, see **[Getting Started](getting-started.md)**.

## Usage

```bash
mobius [OPTIONS] COMMAND [ARGS]...
```

### Global Options

| Option | Description |
|--------|-------------|
| `-V, --version` | Show version and exit |
| `--install-completion` | Install shell completion |
| `--show-completion` | Show shell completion script |
| `--help` | Show help message |

---

## Quick Start

> For the full first-run walkthrough (interview → seed → execute), see **[Getting Started](getting-started.md)**.

---

## Commands Overview

| Command | Description |
|---------|-------------|
| `setup` | Detect runtimes and configure Mobius for your environment |
| `init` | Start interactive interview to refine requirements |
| `run` | Execute Mobius workflows |
| `cancel` | Cancel stuck or orphaned executions |
| `config` | Manage Mobius configuration (show, switch backend, set values) |
| `uninstall` | Cleanly remove all Mobius configuration from your system |
| `status` | Check Mobius system status |
| `tui` | Interactive TUI monitor for real-time workflow monitoring |
| `monitor` | Shorthand for `tui monitor` |
| `mcp` | MCP server commands for Claude Desktop and other MCP clients |

---

## `mobius setup`

Detect available runtime backends and configure Mobius for your environment.

Mobius supports multiple runtime backends via a pluggable `AgentRuntime` protocol. The `setup` command auto-detects
which runtimes are available in your PATH (currently: Claude Code, Codex CLI) and
configures `orchestrator.runtime_backend` accordingly. Additional runtimes can be registered
by implementing the protocol — see [Architecture](architecture.md#how-to-add-a-new-runtime-adapter).

```bash
mobius setup [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `-r, --runtime TEXT` | Runtime backend to configure. Shipped values: `claude`, `codex`. Auto-detected if omitted |
| `--non-interactive` | Skip interactive prompts (for scripted installs) |

**Examples:**

```bash
# Auto-detect runtimes and configure interactively
mobius setup

# Explicitly select Codex CLI as runtime backend
mobius setup --runtime codex

# Explicitly select Claude Code as runtime backend
mobius setup --runtime claude

# Non-interactive setup (for CI or scripted installs)
mobius setup --non-interactive
```

**What setup does:**

- Scans PATH for `claude`, `codex`, and `opencode` CLI binaries
- Prompts you to select a runtime if multiple are found (or auto-selects if only one)
- Writes `orchestrator.runtime_backend` to `~/.mobius/config.yaml`
- For Claude Code: registers the MCP server in `~/.claude/mcp.json`
- For Codex CLI: sets `orchestrator.codex_cli_path` and `llm.backend: codex` in `~/.mobius/config.yaml`
- For Codex CLI: installs managed Mobius rules into `~/.codex/rules/`
- For Codex CLI: installs managed Mobius skills into `~/.codex/skills/`
- For Codex CLI: registers the Mobius MCP/env block in `~/.codex/config.toml`

> **Codex config split:** put persistent Mobius per-role model overrides in `~/.mobius/config.yaml` (`clarification.default_model`, `llm.qa_model`, `evaluation.semantic_model`, `consensus.models`, `consensus.advocate_model`, `consensus.devil_model`, `consensus.judge_model`). `~/.codex/config.toml` is only the Codex MCP/env hookup file used by setup.

> **`opencode` caveat:** `setup` detects the `opencode` binary in PATH but cannot configure it — if `opencode` is your only installed runtime, `setup` exits with `Error: Unsupported runtime: opencode`. The `opencode` runtime backend is **not yet implemented** (`runtime_factory.py` raises `NotImplementedError`). It is planned for a future release.

---

## `mobius init`

Start interactive interview to refine requirements (Big Bang phase).

**Shorthand:** `mobius init "context"` is equivalent to `mobius init start "context"`.
When the first argument is not a known subcommand (`start`, `list`), it is treated as the context for `init start`.

### `init start`

Start an interactive interview to transform vague ideas into clear, executable requirements.

```bash
mobius init [start] [OPTIONS] [CONTEXT]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `CONTEXT` | Initial context or idea (interactive prompt if not provided) |

**Options:**

| Option | Description |
|--------|-------------|
| `-r, --resume TEXT` | Resume an existing interview by ID |
| `--state-dir DIRECTORY` | Custom directory for interview state files |
| `-o, --orchestrator` | Use Claude Code for the interview/seed flow; combine with `--runtime` to choose the workflow handoff backend |
| `--runtime TEXT` | Agent runtime backend for the workflow execution step after seed generation. Shipped values: `claude`, `codex`. `opencode` appears in the CLI enum but is out of scope. Custom adapters registered in `runtime_factory.py` are also accepted. |
| `--llm-backend TEXT` | LLM backend for interview, ambiguity scoring, and seed generation (`claude_code`, `litellm`, `codex`). `opencode` appears in the CLI enum but is out of scope |
| `-d, --debug` | Show verbose logs including debug messages |

**Examples:**

```bash
# Shorthand (recommended) -- 'start' subcommand is implied
mobius init "I want to build a task management CLI tool"

# Explicit subcommand (equivalent)
mobius init start "I want to build a task management CLI tool"

# Start with Claude Code (no API key needed)
mobius init --orchestrator "Build a REST API"

# Specify runtime backend for the workflow step
mobius init --orchestrator --runtime codex "Build a REST API"

# Use Codex as the LLM backend for interview and seed generation
mobius init --llm-backend codex "Build a REST API"

# Resume an interrupted interview
mobius init start --resume interview_20260116_120000

# Interactive mode (prompts for input)
mobius init
```

### `init list`

List all interview sessions.

```bash
mobius init list [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--state-dir DIRECTORY` | Custom directory for interview state files |

---

## `mobius run`

Execute Mobius workflows.

**Shorthand:** `mobius run seed.yaml` is equivalent to `mobius run workflow seed.yaml`.
When the first argument is not a known subcommand (`workflow`, `resume`), it is treated as the seed file for `run workflow`.

**Default mode:** Orchestrator mode is enabled by default. `--no-orchestrator` exists for the legacy standard path, which is still placeholder-oriented.

### `run workflow`

Execute a workflow from a seed file.

```bash
mobius run [workflow] [OPTIONS] SEED_FILE
```

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `SEED_FILE` | Yes | Path to the seed YAML file |

**Options:**

| Option | Description |
|--------|-------------|
| `-o/-O, --orchestrator/--no-orchestrator` | Use the agent-runtime orchestrator for execution (default: enabled) |
| `--runtime TEXT` | Agent runtime backend override (`claude`, `codex`). Uses configured default if omitted. (`opencode` is in the CLI enum but out of scope) |
| `-r, --resume TEXT` | Resume a previous orchestrator session by ID |
| `--mcp-config PATH` | Path to MCP client configuration YAML file |
| `--mcp-tool-prefix TEXT` | Prefix to add to all MCP tool names (e.g., `mcp_`) |
| `-s, --sequential` | Execute ACs sequentially instead of in parallel |
| `-n, --dry-run` | Validate seed without executing. **Currently only takes effect with `--no-orchestrator`.** In default orchestrator mode this flag is accepted but has no effect — the full workflow executes |
| `--no-qa` | Skip post-execution QA evaluation |
| `-d, --debug` | Show logs and agent thinking (verbose output) |

**Examples:**

```bash
# Run a workflow (shorthand, recommended)
mobius run seed.yaml

# Explicit subcommand (equivalent)
mobius run workflow seed.yaml

# Use Codex CLI as the runtime backend
mobius run seed.yaml --runtime codex

# With MCP server integration
mobius run seed.yaml --mcp-config mcp.yaml

# Resume a previous session
mobius run seed.yaml --resume orch_abc123

# Skip post-execution QA
mobius run seed.yaml --no-qa

# Debug output
mobius run seed.yaml --debug

# Sequential execution (one AC at a time)
mobius run seed.yaml --sequential
```

### `run resume`

Resume a paused or failed execution.

> **Current state:** `run resume` is a placeholder helper. For real orchestrator sessions, use `mobius run seed.yaml --resume <session_id>`.

```bash
mobius run resume [EXECUTION_ID]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `EXECUTION_ID` | Execution ID to resume (uses latest if not specified) |

> **Note:** For orchestrator sessions, you can also use:
> ```bash
> mobius run seed.yaml --resume <session_id>
> ```

---

## `mobius cancel`

Cancel stuck or orphaned executions.

### `cancel execution`

Cancel a specific execution, all running executions, or interactively pick from active sessions.

```bash
mobius cancel execution [OPTIONS] [EXECUTION_ID]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `EXECUTION_ID` | Session/execution ID to cancel. If omitted, enters interactive mode |

**Options:**

| Option | Description |
|--------|-------------|
| `-a, --all` | Cancel all running/paused executions |
| `-r, --reason TEXT` | Reason for cancellation (default: "Cancelled by user via CLI") |

**Examples:**

```bash
# Interactive mode - list active executions and pick one
mobius cancel execution

# Cancel a specific execution by session ID
mobius cancel execution orch_abc123def456

# Cancel all running executions
mobius cancel execution --all

# Cancel with a custom reason
mobius cancel execution orch_abc123 --reason "Stuck for 2 hours"
```

---

## `mobius config`

Manage Mobius configuration.

### `config show`

Display current configuration summary, or a specific section.

```bash
mobius config show [SECTION]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `SECTION` | Configuration section to display (e.g., `orchestrator`, `llm`, `consensus`) |

**Examples:**

```bash
# Show configuration summary (backend, CLI path, DB, log level)
mobius config show

# Show only orchestrator section
mobius config show orchestrator
```

### `config backend`

Show or switch the runtime backend. This sets both `orchestrator.runtime_backend` and `llm.backend` together — they are always kept in sync for simplicity. Advanced users can decouple them with `config set`.

```bash
mobius config backend [BACKEND]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `BACKEND` | Backend to switch to: `claude` or `codex`. Omit to show current |

**Examples:**

```bash
# Show current backend
mobius config backend

# Switch to Codex CLI
mobius config backend codex

# Switch to Claude Code
mobius config backend claude
```

### `config init`

Initialize Mobius configuration.

```bash
mobius config init
```

Creates `~/.mobius/config.yaml` and `~/.mobius/credentials.yaml` with default templates. Sets `chmod 600` on `credentials.yaml`. If the files already exist they are not overwritten.

### `config set`

Set a configuration value using dot notation.

```bash
mobius config set KEY VALUE
```

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `KEY` | Yes | Configuration key (dot notation) |
| `VALUE` | Yes | Value to set |

**Examples:**

```bash
# Change log level
mobius config set logging.level debug

# Override LLM backend separately from runtime backend
mobius config set llm.backend litellm
```

### `config validate`

Validate current configuration. Checks that the runtime backend is supported and the CLI binary path exists.

```bash
mobius config validate
```

---

## `mobius uninstall`

Cleanly remove all Mobius configuration from your system. Reverses everything `mobius setup` did.

```bash
mobius uninstall [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--keep-data` | Keep entire `~/.mobius/` directory (config, credentials, seeds, logs, DB) |
| `--dry-run` | Show what would be removed without actually deleting |
| `-y, --yes` | Skip confirmation prompt |

**Examples:**

```bash
# Interactive uninstall (shows what will be removed, asks for confirmation)
mobius uninstall

# Non-interactive
mobius uninstall -y

# Preview only
mobius uninstall --dry-run

# Remove MCP/artifacts but keep ~/.mobius/
mobius uninstall --keep-data
```

**What it removes:**

- `mobius` entry from `~/.claude/mcp.json`
- `[mcp_servers.mobius]` section from `~/.codex/config.toml`
- `~/.codex/rules/mobius.md` and `~/.codex/skills/mobius/`
- `<!-- mob:START -->` … `<!-- mob:END -->` block from `CLAUDE.md`
- `.mobius/` directory in the current project
- `~/.mobius/` directory (unless `--keep-data`)

**What it does NOT remove:**

- The Python package — run `pip uninstall mobius-ai` or `uv tool uninstall mobius-ai` separately
- The Claude Code plugin — run `claude plugin uninstall mobius` separately
- Your project source code or git history

See [UNINSTALL.md](../UNINSTALL.md) for the full guide.

---

## `mobius status`

Check Mobius system status.

> **Current state:** the `status` subcommands return lightweight placeholder summaries. They are useful for smoke testing the command surface, but should not be treated as authoritative orchestration state.

### `status health`

Check system health. Verifies database connectivity, provider configuration, and system resources.

```bash
mobius status health
```

**Representative Output:**

```
+---------------+---------+
| Database      |   ok    |
| Configuration |   ok    |
| Providers     | warning |
+---------------+---------+
```

### `status executions`

List recent executions with status information.

```bash
mobius status executions [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `-n, --limit INTEGER` | Number of executions to show (default: 10) |
| `-a, --all` | Show all executions |

**Examples:**

```bash
# Show last 10 executions
mobius status executions

# Show last 5 executions
mobius status executions -n 5

# Show all executions
mobius status executions --all
```

### `status execution`

Show details for a specific execution.

```bash
mobius status execution [OPTIONS] EXECUTION_ID
```

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `EXECUTION_ID` | Yes | Execution ID to inspect |

**Options:**

| Option | Description |
|--------|-------------|
| `-e, --events` | Show execution events |

**Examples:**

```bash
# Show execution details
mobius status execution exec_abc123

# Show execution with events
mobius status execution --events exec_abc123
```

---

## `mobius tui`

Interactive TUI monitor for real-time workflow monitoring.

> **Equivalent invocations:** `mobius tui` (no subcommand), `mobius tui monitor`, and `mobius monitor` are all equivalent — they all launch the TUI monitor.

### `tui monitor`

Launch the interactive TUI monitor to observe workflow execution in real-time.

```bash
mobius tui [monitor] [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--db-path PATH` | Path to the Mobius database file (default: `~/.mobius/mobius.db`) |
| `--backend TEXT` | TUI backend to use: `python` (Textual, default) or `slt` (native Rust binary) |

**Examples:**

```bash
# Launch TUI monitor (default Textual backend)
mobius tui monitor

# Monitor with a specific database file
mobius tui monitor --db-path ~/.mobius/mobius.db

# Use the native SLT backend (requires mobius-tui binary)
mobius tui monitor --backend slt
```

> **Note:** The `slt` backend requires the `mobius-tui` binary in your PATH. Install it with:
> ```bash
> cd crates/mobius-tui && cargo install --path .
> ```

**TUI Screens:**

| Key | Screen | Description |
|-----|--------|-------------|
| `1` | Dashboard | Overview with phase progress, drift meter, cost tracker |
| `2` | Execution | Execution details, timeline, phase outputs |
| `3` | Logs | Filterable log viewer with level filtering |
| `4` | Debug | State inspector, raw events, configuration |
| `s` | Session Selector | Browse and switch between monitored sessions |
| `e` | Lineage | View evolutionary lineage across generations (evolve/ralph) |

**Keyboard Shortcuts:**

| Key | Action |
|-----|--------|
| `1-4` | Switch to numbered screen |
| `s` | Session Selector |
| `e` | Lineage view |
| `q` | Quit |
| `p` | Pause execution |
| `r` | Resume execution |
| Up/Down | Scroll |

---

## `mobius mcp`

MCP (Model Context Protocol) server commands for Claude Desktop and other MCP-compatible clients.

### `mcp serve`

Start the MCP server to expose Mobius tools to Claude Desktop or other MCP clients.

```bash
mobius mcp serve [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `-h, --host TEXT` | Host to bind to (default: localhost) |
| `-p, --port INTEGER` | Port to bind to (default: 8080) |
| `-t, --transport TEXT` | Transport type: `stdio` or `sse` (default: stdio) |
| `--db TEXT` | Path to the EventStore database file |
| `--runtime TEXT` | Runtime backend for orchestrator-driven tools (`claude`, `codex`). (`opencode` is in the CLI enum but out of scope) |
| `--llm-backend TEXT` | LLM backend for interview/seed/evaluation tools (`claude_code`, `litellm`, `codex`). (`opencode` is in the CLI enum but out of scope) |

**Examples:**

```bash
# Start with stdio transport (for Claude Desktop)
mobius mcp serve

# Start with SSE transport on custom port
mobius mcp serve --transport sse --port 9000

# Start with Codex-backed orchestrator tools
mobius mcp serve --runtime codex --llm-backend codex

# Start on specific host
mobius mcp serve --host 0.0.0.0 --port 8080 --transport sse
```

**Startup behavior:**

On startup, `mcp serve` automatically cancels any sessions left in `RUNNING` or `PAUSED` state for more than 1 hour. These are treated as orphaned from a previous crash. Cancelled sessions are reported on stderr (or console when using SSE transport). This cleanup is best-effort and does not prevent the server from starting if it fails.

**Claude Desktop / Claude Code CLI Integration:**

`mobius setup --runtime claude` writes this automatically to `~/.claude/mcp.json`.
To register manually, add to `~/.claude/mcp.json`:

```json
{
  "mcpServers": {
    "mobius": {
      "command": "uvx",
      "args": ["--from", "mobius-ai[claude]", "mobius", "mcp", "serve"],
      "timeout": 600
    }
  }
}
```

If Mobius is installed directly (not via `uvx`), use:

```json
{
  "mcpServers": {
    "mobius": {
      "command": "mobius",
      "args": ["mcp", "serve"],
      "timeout": 600
    }
  }
}
```

**Runtime selection** is configured in `~/.mobius/config.yaml` (written by `mobius setup`):

```yaml
orchestrator:
  runtime_backend: claude   # or "codex"
```

Override per-session with the `MOBIUS_AGENT_RUNTIME` environment variable if needed.

### `mcp info`

Show MCP server information and available tools.

```bash
mobius mcp info [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--runtime TEXT` | Agent runtime backend for orchestrator-driven tools (`claude`, `codex`). Affects which tool variants are instantiated |
| `--llm-backend TEXT` | LLM backend for interview/seed/evaluation tools (`claude_code`, `litellm`, `codex`). Affects which tool variants are instantiated |

**Available Tools:**

| Tool | Description |
|------|-------------|
| `mobius_execute_seed` | Execute a seed specification |
| `mobius_session_status` | Get the status of a session |
| `mobius_query_events` | Query event history |

---

## Typical Workflows

> For first-time setup and the complete onboarding flow, see **[Getting Started](getting-started.md)**.
> For runtime-specific configuration, see the [Claude Code](runtime-guides/claude-code.md) and [Codex CLI](runtime-guides/codex.md) runtime guides.

### Cancelling Stuck Executions

```bash
# Interactive: list and pick
mobius cancel execution

# Cancel all at once
mobius cancel execution --all
```

---

## Environment Variables

The table below covers the most commonly used variables. For the full list — including all per-model overrides (e.g., `MOBIUS_QA_MODEL`, `MOBIUS_SEMANTIC_MODEL`, `MOBIUS_CONSENSUS_MODELS`, etc.) — see [config-reference.md](config-reference.md#environment-variables).

| Variable | Overrides config key | Description |
|----------|----------------------|-------------|
| `ANTHROPIC_API_KEY` | — | Anthropic API key for Claude models |
| `OPENAI_API_KEY` | — | OpenAI API key for LiteLLM / Codex CLI |
| `OPENROUTER_API_KEY` | — | OpenRouter API key for consensus and LiteLLM |
| `MOBIUS_AGENT_RUNTIME` | `orchestrator.runtime_backend` | Override the runtime backend (`claude`, `codex`) |
| `MOBIUS_AGENT_PERMISSION_MODE` | `orchestrator.permission_mode` | Permission mode for non-OpenCode runtimes |
| `MOBIUS_LLM_BACKEND` | `llm.backend` | Override the LLM-only flow backend |
| `MOBIUS_CLI_PATH` | `orchestrator.cli_path` | Path to the Claude CLI binary |
| `MOBIUS_CODEX_CLI_PATH` | `orchestrator.codex_cli_path` | Path to the Codex CLI binary |

---

## Configuration Files

Mobius stores configuration in `~/.mobius/`:

| File | Description |
|------|-------------|
| `config.yaml` | Main configuration — see [config-reference.md](config-reference.md) for all options |
| `credentials.yaml` | API keys (chmod 600; created by `mobius config init`) |
| `mobius.db` | SQLite database for event sourcing (actual path: `~/.mobius/mobius.db`; the `persistence.database_path` config key is currently not honored — see [config-reference.md](config-reference.md#persistence)) |
| `logs/mobius.log` | Log output (path configurable via `logging.log_path`) |

---

## Exit Codes

| Code | Description |
|------|-------------|
| `0` | Success |
| `1` | General error |
