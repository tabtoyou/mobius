# Mobius for Codex

Use Mobius commands when the user is asking to clarify requirements, generate a seed, run a seed, inspect workflow status, evaluate an execution, or manage Mobius setup.

## CRITICAL: MCP Tool Routing

When the user types `mob <command>`, you MUST call the corresponding MCP tool.
Do NOT interpret `mob` commands as natural language. ALWAYS route to the MCP tool.

| User Input | MCP Tool to Call |
|-----------|-----------------|
| `mob interview "<topic>"` | `mobius_interview` with `initial_context` |
| `mob interview "<answer>"` (follow-up) | `mobius_interview` with `answer` and `session_id` |
| `mob seed [session_id]` | `mobius_generate_seed` |
| `mob run <seed.yaml>` | `mobius_execute_seed` with `seed_path` |
| `mob status [session_id]` | `mobius_session_status` |
| `mob evaluate <session_id>` | `mobius_evaluate` |
| `mob evolve ...` | `mobius_evolve_step` |
| `mob cancel [execution_id]` | `mobius_cancel_execution` |
| `mob unstuck` / `mob lateral` | `mobius_lateral_think` |

## Natural Language Mapping

For natural-language requests, map to the corresponding MCP tool:
- "clarify requirements", "interview me", "socratic interview" → call `mobius_interview`
- "generate a seed", "freeze requirements" → call `mobius_generate_seed`
- "run the seed", "execute the workflow" → call `mobius_execute_seed`
- "check status", "am I drifting?" → call `mobius_session_status`
- "evaluate", "verify the result" → call `mobius_evaluate`

## Setup & Update

- `mob setup` → write Mobius config (`~/.mobius/config.yaml`) and register the MCP server
- `mob update` → upgrade Mobius to the latest PyPI version

If the request is clearly unrelated to Mobius, handle it normally.
