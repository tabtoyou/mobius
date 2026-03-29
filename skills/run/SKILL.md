---
name: run
description: "Execute a Seed specification through the workflow engine"
mcp_tool: mobius_execute_seed
mcp_args:
  seed_path: "$1"
  cwd: "$CWD"
---

# /mobius:run

Execute a Seed specification through the Mobius workflow engine.

## Usage

```
/mobius:run [seed_file_or_content]
```

**Trigger keywords:** "mobius run", "execute seed"

## How It Works

1. **Input**: Provide seed YAML content directly or a path to a `.yaml` file
2. **Validation**: Seed is parsed and validated (goal, constraints, acceptance criteria, ontology)
3. **Execution**: The orchestrator runs the workflow with PAL routing
4. **Progress**: Real-time progress updates via session tracking
5. **Result**: Execution summary with pass/fail status

## Instructions

When the user invokes this skill:

### Load MCP Tools (Required first)

The Mobius MCP tools are often registered as **deferred tools** that must be explicitly loaded before use. **You MUST perform this step before proceeding.**

1. Use the `ToolSearch` tool to find and load the execution MCP tools:
   ```
   ToolSearch query: "+mobius execute"
   ```
2. The tools will typically be named with prefix `mcp__plugin_mobius_mobius__` (e.g., `mobius_execute_seed`, `mobius_session_status`). After ToolSearch returns, the tools become callable.
3. If ToolSearch finds the tools → proceed with the steps below. If not → skip to **Fallback** section.

**IMPORTANT**: Do NOT skip this step. Do NOT assume MCP tools are unavailable just because they don't appear in your immediate tool list. They are almost always available as deferred tools that need to be loaded first.

### Execution Steps

1. **Detect git workflow** (before any code changes):
   - Read the project's `CLAUDE.md` for git workflow preferences
   - If PR-based workflow detected and currently on `main`/`master`:
     - Create a feature branch: `mob/run/<session_id>`
     - All code changes go to this branch
   - If no preference: use current branch (backward compatible)

2. Check if the user provided seed content or a file path:
   - If a file path: Read the file with the Read tool
   - If inline YAML: Use directly
   - If neither: Check conversation history for a recently generated seed

3. **Start background execution** with `mobius_start_execute_seed`:
   ```
   Tool: mobius_start_execute_seed
   Arguments:
     seed_content: <the seed YAML>
     model_tier: "medium"  (or as specified by user)
     max_iterations: 10    (or as specified by user)
   ```
   This returns immediately with a `job_id`, `session_id`, and `execution_id`.

4. If resuming an existing session, include `session_id`:
   ```
   Tool: mobius_start_execute_seed
   Arguments:
     seed_content: <the seed YAML>
     session_id: <existing session ID>
   ```

5. **Ask user about polling strategy** using `AskUserQuestion` immediately after IDs are returned:

   Present the session/job IDs first, then ask:

   ```
   Question: "Execution started. How would you like to monitor progress?"
   Header: "Monitoring"
   Options:
     - label: "Poll here (Recommended)"
       description: "Poll in this session. Context window is consumed but you get real-time updates."
     - label: "Don't poll — I'll monitor separately"
       description: "End here. Use `mob status <session_id>` in a new terminal or /clone to monitor."
   ```

   **If user chooses "Poll here"**, ask follow-up:
   ```
   Question: "How often should I check progress?"
   Header: "Interval"
   Options:
     - label: "Per level (Recommended)"
       description: "Check once when each parallel level completes. Most context-efficient with meaningful updates."
     - label: "Every 10 minutes"
       description: "Periodic check regardless of level progress. Balanced context usage."
     - label: "Every 20 minutes"
       description: "Minimal context usage. Best for large seeds with many ACs."
   ```

   Then display:
   ```
   💡 Note: Context compression may occur during long executions.
   MCP tools remain available after compression, but prior poll results are summarized.
   If this session is needed for follow-up (mob evaluate, mob evolve), shorter polling = more context consumed.
   ```

   **If user chooses "Don't poll"**, display:

   ```
   Execution running in background.
   Session ID: <session_id>
   Job ID: <job_id>
   
   To monitor progress:
     Option A: Open a new terminal → `mob status <session_id>`
     Option B: Use /clone to fork this conversation for monitoring
     Option C: Come back later and run `mob status <session_id>` here
   
   When execution completes, continue with: `mob evaluate <session_id>`
   ```
   Then **stop** — do NOT proceed to polling steps.

6. **Poll for progress** using `mobius_job_wait` (only if user chose to poll):
   ```
   loop:
     Tool: mobius_job_wait
     Arguments:
       job_id: <job_id from step 3>
       cursor: <cursor from previous response, starts at 0>
       timeout_seconds: 60
   
     # Returns immediately when state changes; waits up to 60s otherwise.
     # This reduces tool call round-trips and context consumption.
     # Continue until status is "completed", "failed", or "cancelled"
   ```

   Between polls, report progress concisely (one line):
   ```
   [Executing] Phase: <current_phase> | AC: <completed>/<total>
   ```

7. **Fetch final result** with `mobius_job_result`:
   ```
   Tool: mobius_job_result
   Arguments:
     job_id: <job_id>
   ```

8. Present the execution results to the user:
   - Show success/failure status
   - Show session ID (for later status checks)
   - Show execution summary

9. **Post-execution QA** (automatic):
   `mobius_start_execute_seed` automatically runs QA after successful execution.
   The QA verdict is included in the final job result text.
   To skip: pass `skip_qa: true` to the tool.

   Present QA verdict with next step:
   - **PASS**: `Next: mob evaluate <session_id> for formal 3-stage verification`
   - **REVISE**: Show differences/suggestions, then `Next: Fix the issues above, then mob run to retry -- or mob unstuck if blocked`
   - **FAIL/ESCALATE**: `Next: Review failures above, then mob run to retry -- or mob unstuck if blocked`

## Fallback (No MCP Server)

If the MCP server is not available, inform the user:

```
Mobius MCP server is not configured.
To enable full execution mode, run: /mobius:setup

Without MCP, you can still:
- Use /mobius:interview for requirement clarification
- Use /mobius:seed to generate specifications
- Manually implement the seed specification
```

## Example

```
User: /mobius:run seed.yaml

[Reads seed.yaml, validates, starts background execution]

Background execution started.
Job ID: job_a1b2c3d4e5f6
Session ID: orch_x1y2z3
Execution ID: exec_m1n2o3

[Polling for progress...]
Phase: Executing | AC Progress: 1/3
Phase: Executing | AC Progress: 2/3
Phase: Executing | AC Progress: 3/3

[Fetching final result...]

Result:
  Seed Execution SUCCESS
  ========================
  Session ID: orch_x1y2z3
  Goal: Build a CLI task manager
  Duration: 45.2s
  Messages Processed: 12

  Next: `mob evaluate orch_x1y2z3` for formal 3-stage verification
```
