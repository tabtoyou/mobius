---
name: pm
description: "Generate a PM through guided PM-focused interview with automatic question classification. Use when the user says 'mob pm', 'prd', 'product requirements', or wants to create a PRD/PM document."
---

# /mobius:pm

PM-focused Socratic interview that produces a Product Requirements Document.

## Instructions

### Step 1: Load MCP Tool

```
ToolSearch query: "+mobius pm_interview"
```

If not found → **diagnose before telling user to run setup**:

1. Check if MCP is already configured:
   ```bash
   grep -q '"mobius"' ~/.claude/mcp.json 2>/dev/null && echo "CONFIGURED" || echo "NOT_CONFIGURED"
   ```

2. **If NOT_CONFIGURED** → tell user to run `mob setup` first. Stop.

3. **If CONFIGURED** → MCP is registered but the server isn't connecting. Do NOT tell the user to run `mob setup` again. Instead show:
   ```
   Mobius MCP is configured but not connected.

   Try these steps in order:
   1. Restart Claude Code (Cmd+Shift+P → "Reload Window" or close/reopen terminal)
   2. Check MCP status: type /mcp in Claude Code
   3. If mobius shows "error", try: mob update
   4. If still failing, re-run: mob setup
   ```
   Stop.

### Step 2: Start Interview

```
Tool: mobius_pm_interview
Arguments:
  initial_context: <user's topic or idea>
  cwd: <current working directory>
```

### Step 3: Loop

After every MCP response, do these three things:

**A. Show alerts** (if present in `meta`):
- `meta.deferred_this_round` → print `[DEV → deferred] "question"`
- `meta.decide_later_this_round` → print `[DEV → decide-later] "question"`
- `meta.pending_reframe` → print `ℹ️ Reframed from technical question.`

**B. Show content + get user input:**

Print the MCP content text to the user first.

Then check: does `meta.ask_user_question` exist?

- **YES** → Pass it directly to `AskUserQuestion`:
  ```
  AskUserQuestion(questions=[meta.ask_user_question])
  ```
  Do NOT modify it. Do NOT add options. Do NOT rephrase the question.

- **NO** → This is an interview question. Use `AskUserQuestion` with `meta.question` and generate 2-3 suggested answers.

**C. Relay answer back:**

```
Tool: mobius_pm_interview
Arguments:
  session_id: <meta.session_id>
  <meta.response_param>: <user's answer>
```

**D. Check completion:**

If `meta.is_complete == true` → go to Step 4.
Otherwise → repeat Step 3.

### Step 4: Generate

```
Tool: mobius_pm_interview
Arguments:
  session_id: <session_id>
  action: "generate"
  cwd: <current working directory>
```

### Step 5: Copy to Clipboard

After generation, read the pm.md file from `meta.pm_path` and copy its contents to the clipboard:

```bash
cat <meta.pm_path> | pbcopy
```

### Step 6: Show Result & Next Step

Show the following to the user:

```
PM document saved: <meta.pm_path>
(Clipboard에 복사되었습니다)

Next step:
  mob interview <meta.pm_path>
```
