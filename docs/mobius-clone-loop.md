# Mobius Clone-In-The-Loop

`mobius_clone_decide` is an MCP tool for replacing parts of the human feedback path inside the Ralph loop with a profile-backed digital clone.
It runs as a bounded sub-agent, not just a single LLM completion.

## What It Does

- Accepts an ambiguous implementation choice plus candidate options.
- Spawns a read-only decision sub-agent that can inspect the current repo, nearby local repos, and use search/fetch tools.
- Reads a persistent clone profile from one of these locations:
  - explicit `profile_path`
  - `MOBIUS_CLONE_PROFILE_PATH` or `MOBIUS_CLONE_PROFILE_PATH`
  - `.mobius/clone_profile.md`
  - `.mobius/memory.md`
  - `.mobius/clone_profile.md`
- Chooses an option when confidence is strong enough for the decision importance.
- Refuses to choose and requests human feedback when the history/profile is not strong enough.
- Fails open: if the clone sub-agent crashes or cannot return valid JSON, it degrades to a non-blocking `request_user_feedback` result instead of crashing Ralph loop.
- Writes every decision to `.mobius/clone-decisions.jsonl` by default.
- Emits `clone.decision.made` or `clone.feedback.requested` events when an event store is available.

## Ralph Integration Pattern

Use the clone tool as the first stop whenever the execution agent reaches an underspecified choice:

1. Detect that more than one implementation path is consistent with the seed.
2. Call `mobius_clone_decide` with the current context and concrete options.
3. If the clone returns `choose_option`, continue with the selected option.
4. If the clone returns `request_user_feedback`, stop and surface the question instead of guessing.

The Codex runtime prompt now injects this protocol automatically when the tool is present in the session tool list.

## Minimal Example

```json
{
  "topic": "notification delivery channel",
  "context": "The Ralph loop needs to report clone choices after autonomous decisions.",
  "options": [
    "append to local JSONL log only",
    "send Slack webhook and keep local JSONL log"
  ],
  "importance": "high",
  "project_dir": "/path/to/project",
  "notify_channel": "log"
}
```

## Notification Hooks

- `notify_channel=log`: only local log persistence.
- `notify_channel=slack`: best-effort Slack webhook delivery via `MOBIUS_CLONE_SLACK_WEBHOOK_URL`.
- `notify_channel=imessage`: best-effort Apple Messages delivery via `MOBIUS_CLONE_IMESSAGE_RECIPIENT`.
- `notify_channel=auto`: log plus any configured Slack/iMessage integrations.

The intended long-term model is:

- clone decides when the owner's history is sufficiently clear
- clone escalates when the decision is high impact and prior behavior is insufficient
- owner receives a durable audit trail for every autonomous decision
