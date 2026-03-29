---
name: clone
description: "Set up or refresh the digital clone profile before autonomous loops"
---

# /mobius:clone

Prepare the user's digital clone before `mob ralph` or any planning-heavy autonomous work.

## Usage

```
mob clone
mob clone <repo-or-path> [more paths...]
mob clone <url> [more urls...]
mob clone <repo> <url> <path>     # mix sources freely
/mobius:clone
```

**Trigger keywords:** "set up clone", "refresh clone", "digital clone", "clone profile"

### Supported Sources

| Source | Example | How it works |
|--------|---------|--------------|
| Current directory | `mob clone` | Analyze the working directory |
| Local repo / path | `mob clone ~/projects/myapp` | Read code, docs, and patterns directly |
| GitHub repo URL | `mob clone https://github.com/user/repo` | Fetch and analyze repo contents |
| LinkedIn profile | `mob clone https://linkedin.com/in/someone` | Extract role, skills, domain expertise |
| Any URL | `mob clone https://someone.dev/blog` | Fetch page content for context |

Multiple sources can be combined in a single invocation to build a richer clone profile.

## Instructions

When the user invokes this skill:

1. Determine the target sources.
   - Default to the current working directory.
   - If the user passed additional repo paths, inspect those too.
   - If the user passed URLs (GitHub repos, LinkedIn profiles, blogs, portfolios), fetch their content via WebFetch/WebSearch and extract relevant signals.
   - Multiple source types can be mixed in a single invocation.

2. Gather evidence about the user's engineering style.
   - Read existing project docs (`README`, `CLAUDE.md`, architecture notes).
   - Inspect representative code, tests, naming patterns, error-handling style, and tradeoff patterns.
   - Look for repeated choices across repos: framework preferences, abstraction boundaries, testing strictness, data modeling style, comments, dependency tolerance, UI taste, and rollout habits.

3. Ask only for the missing human judgments.
   - Use short targeted questions for principles that cannot be inferred from code.
   - Prefer concrete tradeoffs over open-ended biography prompts.
   - If enough evidence already exists, do not over-interview.

4. Write or refresh the clone memory files.
   - Primary profile: `.mobius/clone_profile.md`
   - Optional working memory: `.mobius/memory.md`
   - Ensure the profile captures:
     - decision principles
     - preferred defaults
     - strong dislikes / anti-patterns
     - repo-specific conventions
     - confidence notes about what is inferred vs explicitly confirmed

5. End with a concise handoff.
   - Summarize what the clone now knows.
   - Call out any unresolved high-stakes decisions the clone should escalate instead of guessing.
   - Suggest the next command in `📍 Next:` form, typically `mob ralph ...` or the user's planning step.

## Output Shape

The profile should stay compact and operational. Use sections like:

```md
# Clone Profile

## Core Preferences
- ...

## Coding Patterns
- ...

## Decision Rules
- ...

## Escalate To Human When
- ...

## Evidence
- inferred from <repo/file>
- confirmed by user
```
