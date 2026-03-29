# Mobius - Development Environment

> This CLAUDE.md is for **local development only**. End users install via:
> ```
> claude plugin marketplace add tabtoyou/mobius
> claude plugin install mobius@mobius
> ```
> Once installed as a plugin, skills/hooks/agents work natively without this file.

## mob Commands (Dev Mode)

When the user types any of these commands, read the corresponding SKILL.md file and follow its instructions exactly:

| Input | Action |
|-------|--------|
| `mob` (bare, no subcommand) | Read `skills/welcome/SKILL.md` and follow it |
| `mob interview ...` | Read `skills/interview/SKILL.md` and follow it |
| `mob seed` | Read `skills/seed/SKILL.md` and follow it |
| `mob run` | Read `skills/run/SKILL.md` and follow it |
| `mob evaluate` or `mob eval` | Read `skills/evaluate/SKILL.md` and follow it |
| `mob evolve ...` | Read `skills/evolve/SKILL.md` and follow it |
| `mob unstuck` or `mob stuck` or `mob lateral` | Read `skills/unstuck/SKILL.md` and follow it |
| `mob status` or `mob drift` | Read `skills/status/SKILL.md` and follow it |
| `mob clone` or `mob clone ...` | Read `skills/clone/SKILL.md` and follow it |
| `mob ralph` | Read `skills/ralph/SKILL.md` and follow it |
| `mob tutorial` | Read `skills/tutorial/SKILL.md` and follow it |
| `mob setup` | Read `skills/setup/SKILL.md` and follow it |
| `mob welcome` | Read `skills/welcome/SKILL.md` and follow it |
| `mob cancel` | Read `skills/cancel/SKILL.md` and follow it |
| `mob qa` or `mob qa ...` | Read `skills/qa/SKILL.md` and follow it |
| `mob help` | Read `skills/help/SKILL.md` and follow it |
| `mob update` | Read `skills/update/SKILL.md` and follow it |
| `mob pm` or `mob pm ...` | Read `skills/pm/SKILL.md` and follow it |
| `mob brownfield` or `mob brownfield ...` | Read `skills/brownfield/SKILL.md` and follow it |

**Important**: Do NOT use the Skill tool. Read the file with the Read tool and execute its instructions directly.

## Agents

Bundled agents live in `src/mobius/agents/`. When a skill references an agent (e.g., `mobius:socratic-interviewer`), read its definition from `src/mobius/agents/{name}.md` and adopt that role. Use `MOBIUS_AGENTS_DIR` or `.claude-plugin/agents/` only for explicit custom overrides.

<!-- mob:START -->
<!-- mob:VERSION:0.26.0 -->
# Mobius — Specification-First AI Development

> Before telling AI what to build, define what should be built.
> As Socrates asked 2,500 years ago — "What do you truly know?"
> Mobius turns that question into an evolutionary AI workflow engine.

Most AI coding fails at the input, not the output. Mobius fixes this by
**exposing hidden assumptions before any code is written**.

1. **Socratic Clarity** — Question until ambiguity ≤ 0.2
2. **Ontological Precision** — Solve the root problem, not symptoms
3. **Evolutionary Loops** — Each evaluation cycle feeds back into better specs

```
Interview → Seed → Execute → Evaluate
    ↑                           ↓
    └─── Evolutionary Loop ─────┘
```

## mob Commands

Each command loads its agent/MCP on-demand. Details in each skill file.

| Command | Loads |
|---------|-------|
| `mob` | — |
| `mob interview` | `mobius:socratic-interviewer` |
| `mob seed` | `mobius:seed-architect` |
| `mob run` | MCP required |
| `mob evolve` | MCP: `evolve_step` |
| `mob evaluate` | `mobius:evaluator` |
| `mob qa` | `mobius:qa-judge` |
| `mob unstuck` | `mobius:{persona}` |
| `mob status` | MCP: `session_status` |
| `mob clone` | Prepare or refresh the digital clone profile |
| `mob ralph` | Persistent loop until verified |
| `mob tutorial` | Interactive hands-on learning |
| `mob setup` | — |
| `mob help` | — |
| `mob update` | PyPI version check + upgrade |

## Agents

Loaded on-demand — not preloaded.

**Core**: socratic-interviewer, ontologist, seed-architect, evaluator, qa-judge, contrarian
**Support**: hacker, simplifier, researcher, architect
<!-- mob:END -->
