<!--
doc_metadata:
  runtime_scope: [codex]
-->

# Running Mobius with Codex CLI

> For installation and first-run onboarding, see [Getting Started](../getting-started.md).

Mobius can use **OpenAI Codex CLI** as a runtime backend. [Codex CLI](https://github.com/openai/codex) is the local Codex execution surface that the adapter talks to. In Mobius, that backend is presented as a **session-oriented runtime** with the same specification-first workflow harness (acceptance criteria, evaluation principles, deterministic exit conditions), even though the adapter itself communicates with the local `codex` executable.

No additional Python SDK is required beyond the base `mobius-ai` package.

> **Model recommendation:** Use **GPT-5.4** with **medium** reasoning effort for the documented Codex setup. GPT-5.4 provides strong coding, multi-step reasoning, and agentic task execution that pairs well with the Mobius specification-first workflow harness.

## Prerequisites

- **Codex CLI** installed and on your `PATH` (see [install steps](#installing-codex-cli) below)
- An **OpenAI API key** with access to GPT-5.4 (set `OPENAI_API_KEY`). See [`credentials.yaml`](../config-reference.md#credentialsyaml) for file-based key management
- **Python >= 3.12**

## Installing Codex CLI

Codex CLI is distributed as an npm package. Install it globally:

```bash
npm install -g @openai/codex
```

Verify the installation:

```bash
codex --version
```

For alternative install methods and shell completions, see the [Codex CLI README](https://github.com/openai/codex#readme).

## Installing Mobius

> For all installation options (pip, one-liner, from source) and first-run onboarding, see **[Getting Started](../getting-started.md)**.
> The base `mobius-ai` package includes the Codex CLI runtime adapter — no extras are required.

## Platform Notes

| Platform | Status | Notes |
|----------|--------|-------|
| macOS (ARM/Intel) | Supported | Primary development platform |
| Linux (x86_64/ARM64) | Supported | Tested on Ubuntu 22.04+, Debian 12+, Fedora 38+ |
| Windows (WSL 2) | Supported | Recommended path for Windows users |
| Windows (native) | Experimental | WSL 2 strongly recommended; native Windows may have path-handling and process-management issues. Codex CLI itself does not support native Windows. |

> **Windows users:** Install and run both Codex CLI and Mobius inside a WSL 2 environment for full compatibility. See [Platform Support](../platform-support.md) for details.

## Configuration

To select Codex CLI as the runtime backend, set the following in your Mobius configuration:

```yaml
orchestrator:
  runtime_backend: codex
```

Or pass the backend on the command line:

```bash
uv run mobius run workflow --runtime codex ~/.mobius/seeds/seed_abcd1234ef56.yaml
```

### Where Codex users configure what

Use `~/.mobius/config.yaml` for Mobius runtime settings and per-role model overrides.

Use `~/.codex/config.toml` only for the Codex MCP/env hookup written by `mobius setup --runtime codex`.

If you want Codex-backed Mobius roles to use explicit models instead of inheriting Codex CLI's active default/profile, set the existing `config.yaml` keys directly:

```yaml
# ~/.mobius/config.yaml
orchestrator:
  runtime_backend: codex
  codex_cli_path: /usr/local/bin/codex   # omit if codex is already on PATH

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
  # Optional: the simple-voting roster also lives here as `consensus.models`
```

When these keys are left at their shipped defaults, the Codex-aware loader resolves them to Codex's `default` sentinel rather than hardcoding a mini model. In practice, Codex then uses its active global default/profile. Explicit `config.yaml` values always win.

## Command Surface

From the user's perspective, the Codex integration behaves like a **session-oriented Mobius runtime** — the same specification-first workflow harness that drives the Claude runtime.

Under the hood, `CodexCliRuntime` still talks to the local `codex` executable, but it preserves native session IDs and resume handles, and the Codex command dispatcher can route `mob`-style skill commands through the in-process Mobius MCP server.

`mobius setup --runtime codex` currently:

- Detects the `codex` binary on your `PATH`
- Writes `orchestrator.runtime_backend: codex` and `llm.backend: codex` to `~/.mobius/config.yaml`
- Records `orchestrator.codex_cli_path` when available
- Installs managed Mobius rules into `~/.codex/rules/`
- Installs managed Mobius skills into `~/.codex/skills/`
- Registers the Mobius MCP/env hookup in `~/.codex/config.toml`

`~/.codex/config.toml` is not where Mobius per-role model overrides belong. Keep `clarification`, `qa`, `semantic`, and `consensus` model settings in `~/.mobius/config.yaml`.

### `mob` Skill Availability on Codex

After running `mobius setup --runtime codex`, all 15 `mob` skills are installed into `~/.codex/skills/` and the routing rules into `~/.codex/rules/`. The table below shows each skill and its CLI equivalent for terminal-only workflows.

| `mob` Skill | Codex session | CLI equivalent (Terminal) |
|-------------|---------------|--------------------------|
| `mob interview` | Yes | `mobius init start --llm-backend codex "your idea"` |
| `mob seed` | Yes | *(bundled in `mobius init start`)* |
| `mob run` | Yes | `mobius run workflow --runtime codex seed.yaml` |
| `mob status` | Yes | `mobius status execution <session_id>` |
| `mob evaluate` | Yes | *(MCP only)* |
| `mob evolve` | Yes | *(MCP only)* |
| `mob ralph` | Yes | *(MCP only)* |
| `mob cancel` | Yes | `mobius cancel execution <session_id>` |
| `mob unstuck` | Yes | *(MCP only)* |
| `mob tutorial` | Yes | *(MCP only)* |
| `mob welcome` | Yes | *(MCP only)* |
| `mob update` | Yes | `pip install --upgrade mobius-ai` |
| `mob help` | Yes | `mobius --help` |
| `mob qa` | Yes | *(MCP only)* |
| `mob setup` | Yes | `mobius setup --runtime codex` |

> **Note on `mob seed` vs `mob interview`:** These are two distinct skills with separate roles. `mob interview` runs a Socratic Q&A session and returns a `session_id`. `mob seed` accepts that `session_id` and generates a structured Seed YAML (with ambiguity scoring). From the terminal, both steps are performed in a single `mobius init start` invocation.

## Quick Start

> For the full first-run onboarding flow (interview → seed → execute), see **[Getting Started](../getting-started.md)**.

### Verify Installation

```bash
codex --version
mobius --help
```

## How It Works

```
+-----------------+     +------------------+     +-----------------+
|   Seed YAML     | --> |   Orchestrator   | --> |   Codex CLI     |
|  (your task)    |     | (runtime_factory)|     |   (runtime)     |
+-----------------+     +------------------+     +-----------------+
                                |
                                v
                        +------------------+
                        |  Codex executes  |
                        |  with its own    |
                        |  tool set and    |
                        |  sandbox model   |
                        +------------------+
```

The `CodexCliRuntime` adapter launches `codex` (or `codex-cli`) as its transport layer, but wraps it with session handles, resume support, and deterministic skill/MCP dispatch so the runtime behaves like a persistent Mobius session.

> For a side-by-side comparison of all runtime backends, see the [runtime capability matrix](../runtime-capability-matrix.md).

## Codex CLI Strengths

- **Session-aware Codex runtime** -- Mobius preserves Codex session handles and resume state across workflow steps
- **Strong coding and reasoning** -- GPT-5.4 with medium reasoning effort provides robust code generation and multi-file editing across languages
- **Agentic task execution** -- effective at decomposing complex tasks into sequential steps and iterating autonomously
- **Open-source** -- Codex CLI is open-source (Apache 2.0), allowing inspection and contribution
- **Mobius harness** -- the specification-first workflow engine adds structured acceptance criteria, evaluation principles, and deterministic exit conditions on top of Codex CLI's capabilities

## Runtime Differences

Codex CLI and Claude Code are independent runtime backends with different tool sets, permission models, and sandboxing behavior. The same Seed file works with both, but execution paths may differ.

| Aspect | Codex CLI | Claude Code |
|--------|-----------|-------------|
| What it is | Mobius session runtime backed by Codex CLI transport | Anthropic's agentic coding tool |
| Authentication | OpenAI API key | Max Plan subscription |
| Model | GPT-5.4 with medium reasoning effort (recommended) | Claude (via claude-agent-sdk) |
| Sandbox | Codex CLI's own sandbox model | Claude Code's permission system |
| Tool surface | Codex-native tools (file I/O, shell) | Read, Write, Edit, Bash, Glob, Grep |
| Session model | Session-aware via runtime handles, resume IDs, and skill dispatch | Native Claude session context |
| Cost model | OpenAI API usage charges | Included in Max Plan subscription |
| Windows (native) | Not supported | Experimental |

> **Note:** The Mobius workflow model (Seed files, acceptance criteria, evaluation principles) is identical across runtimes. However, because Codex CLI and Claude Code have different underlying agent capabilities, tool access, and sandboxing, they may produce different execution paths and results for the same Seed file.

## CLI Options

### Workflow Commands

```bash
# Execute workflow (Codex runtime)
# Seeds generated by mobius init are saved to ~/.mobius/seeds/seed_{id}.yaml
uv run mobius run workflow --runtime codex ~/.mobius/seeds/seed_abcd1234ef56.yaml

# Dry run (validate seed without executing)
uv run mobius run workflow --dry-run ~/.mobius/seeds/seed_abcd1234ef56.yaml

# Debug output (show logs and agent output)
uv run mobius run workflow --runtime codex --debug ~/.mobius/seeds/seed_abcd1234ef56.yaml

# Resume a previous session
uv run mobius run workflow --runtime codex --resume <session_id> ~/.mobius/seeds/seed_abcd1234ef56.yaml
```

## Seed File Reference

| Field | Required | Description |
|-------|----------|-------------|
| `goal` | Yes | Primary objective |
| `task_type` | No | Execution strategy: `code` (default), `research`, or `analysis` |
| `constraints` | No | Hard constraints to satisfy |
| `acceptance_criteria` | No | Specific success criteria |
| `ontology_schema` | Yes | Output structure definition |
| `evaluation_principles` | No | Principles for evaluation |
| `exit_conditions` | No | Termination conditions |
| `metadata.ambiguity_score` | Yes | Must be <= 0.2 |

## Troubleshooting

### Codex CLI not found

Ensure `codex` or `codex-cli` is installed and available on your `PATH`:

```bash
which codex || which codex-cli
```

If not installed, install via npm:

```bash
npm install -g @openai/codex
```

See the [Codex CLI README](https://github.com/openai/codex#readme) for alternative installation methods.

### API key errors

Verify your OpenAI API key is set and has access to GPT-5.4:

```bash
echo $OPENAI_API_KEY  # should be set
```

### "Providers: warning" in health check

This is normal when using the orchestrator runtime backends. The warning refers to LiteLLM providers, which are not used in orchestrator mode.

### "EventStore not initialized"

The database will be created automatically at `~/.mobius/mobius.db`.

## Cost

Using Codex CLI as the runtime backend requires an OpenAI API key and incurs standard OpenAI API usage charges. Costs depend on:

- Model used (GPT-5.4 with medium reasoning effort recommended)
- Task complexity and token usage
- Number of tool calls and iterations

Refer to [OpenAI's pricing page](https://openai.com/pricing) for current rates.
