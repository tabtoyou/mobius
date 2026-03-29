---
name: help
description: "Full reference guide for Mobius commands and agents"
---

# /mobius:help

Full reference guide for Mobius power users.

## Usage

```
mob help
/mobius:help
```

## What Is Mobius?

Mobius is a **requirement crystallization engine** for AI workflows. It transforms vague ideas into validated specifications through:

1. **Socratic Interview** - Exposes hidden assumptions
2. **Seed Generation** - Creates immutable specifications
3. **PAL Routing** - Auto-escalates/descends model complexity
4. **Lateral Thinking** - 5 personas to break stagnation
5. **3-Stage Evaluation** - Mechanical > Semantic > Consensus

## All Commands

### Core Commands

| Command | Purpose | Mode |
|---------|---------|------|
| `mob` | Welcome + quick start | Plugin |
| `mob interview` | Socratic requirement clarification | Plugin |
| `mob seed` | Generate validated seed spec | Plugin |
| `mob run` | Execute seed workflow | MCP |
| `mob evaluate` | 3-stage verification | MCP |
| `mob unstuck` | 5 lateral thinking personas | Plugin |
| `mob status` | Session status + drift check | MCP |
| `mob clone` | Prepare or refresh the digital clone profile | Plugin |
| `mob setup` | Installation wizard | Plugin |
| `mob welcome` | First-touch welcome guide | Plugin |
| `mob tutorial` | Interactive hands-on learning | Plugin |
| `mob help` | This reference guide | Plugin |
| `mob pm` | PM-focused interview + PRD generation | MCP |
| `mob qa` | General-purpose QA verdict for any artifact | Plugin |
| `mob cancel` | Cancel stuck or orphaned executions | CLI |
| `mob update` | Check for updates + upgrade to latest | Plugin |
| `mob brownfield` | Scan and manage brownfield repo defaults | MCP |

### Evolutionary Loop

| Command | Purpose | Mode |
|---------|---------|------|
| `mob evolve` | Start/monitor evolutionary development loop | MCP |
| `mob ralph` | Self-referential loop until verified ("don't stop") | Plugin + MCP |

**Plugin** = Works immediately after `mob setup`.
**MCP** = Requires `mob setup` (Python >= 3.12 auto-detected). Run setup once to unlock all features.

## Natural Language Triggers

| Phrase | Triggers |
|--------|----------|
| "interview me", "clarify requirements", "socratic interview" | `mob interview` |
| "crystallize", "generate seed", "create seed", "freeze requirements" | `mob seed` |
| "mobius run", "execute seed", "run seed", "run workflow" | `mob run` |
| "evaluate this", "3-stage check", "verify execution" | `mob evaluate` |
| "think sideways", "i'm stuck", "break through", "lateral thinking" | `mob unstuck` |
| "am I drifting?", "drift check", "session status" | `mob status` |
| "set up clone", "refresh clone", "digital clone" | `mob clone` |

### Utility Triggers

| Phrase | Triggers |
|--------|----------|
| "write prd", "pm interview", "product requirements", "create prd" | `mob pm` |
| "qa check", "quality check" | `mob qa` |
| "cancel execution", "stop job", "kill stuck", "abort execution" | `mob cancel` |
| "update mobius", "upgrade mobius" | `mob update` |
| "brownfield defaults", "brownfield scan" | `mob brownfield` |

### Loop Triggers

| Phrase | Triggers |
|--------|----------|
| "ralph", "don't stop", "must complete", "until it works", "keep going" | `mob ralph` |
| "evolve", "evolutionary loop", "iterate until converged" | `mob evolve` |

## Available Skills

### Core Skills

| Skill | Purpose | Mode |
|-------|---------|------|
| `/mobius:welcome` | First-touch welcome experience | Plugin |
| `/mobius:interview` | Socratic requirement clarification | Plugin |
| `/mobius:seed` | Generate validated seed spec | Plugin |
| `/mobius:run` | Execute seed workflow | MCP |
| `/mobius:evaluate` | 3-stage verification | MCP |
| `/mobius:unstuck` | 5 lateral thinking personas | Plugin |
| `/mobius:status` | Session status + drift check | MCP |
| `/mobius:clone` | Prepare or refresh the digital clone profile | Plugin |
| `/mobius:setup` | Installation wizard | Plugin |
| `/mobius:tutorial` | Interactive hands-on learning | Plugin |
| `/mobius:help` | This guide | Plugin |
| `/mobius:pm` | PM-focused interview + PRD generation | MCP |
| `/mobius:qa` | General-purpose QA verdict for any artifact | Plugin |
| `/mobius:cancel` | Cancel stuck or orphaned executions | CLI |
| `/mobius:update` | Check for updates + upgrade to latest | Plugin |
| `/mobius:brownfield` | Scan and manage brownfield repo defaults | MCP |

### Loop Skills

| Skill | Purpose | Best For |
|-------|---------|----------|
| `/mobius:ralph` | Self-referential loop until verified | "Don't stop", must complete |
| `/mobius:evolve` | Evolutionary ontology refinement | Spec iteration until convergence |

## Available Agents

| Agent | Purpose |
|-------|---------|
| `mobius:socratic-interviewer` | Exposes hidden assumptions through questioning |
| `mobius:ontologist` | Finds root problems vs symptoms |
| `mobius:seed-architect` | Crystallizes requirements into seed specs |
| `mobius:evaluator` | Three-stage verification |
| `mobius:contrarian` | "Are we solving the wrong problem?" |
| `mobius:hacker` | "Make it work first, elegance later" |
| `mobius:simplifier` | "Cut scope to absolute minimum" |
| `mobius:researcher` | "Stop coding, start investigating" |
| `mobius:architect` | "Question the foundation, redesign if needed" |

## Setup

After installing Mobius, run `mob setup` once to register the MCP server.
This connects your runtime backend to the Mobius Python core and unlocks all features.

```
mob setup    # One-time setup (~1 minute)
```
