---
name: ralph
description: "Persistent self-referential loop until verification passes"
---

# /mobius:ralph

Persistent self-referential loop until verification passes. "The boulder never stops."

## Usage

```
mob ralph "<your request>"
/mobius:ralph "<your request>"
```

**Trigger keywords:** "ralph", "don't stop", "must complete", "until it works", "keep going"

## How It Works

Ralph mode includes parallel execution + automatic verification:

1. **Execute** (parallel where possible)
   - Independent tasks run concurrently
   - Dependency-aware scheduling

2. **Verify** (verifier)
   - Check completion
   - Validate tests pass
   - Measure drift

3. **Loop** (if failed)
   - Analyze failure
   - Fix issues
   - Repeat from step 1

## Instructions

When the user invokes this skill:

1. **Parse the request**: Extract what needs to be done

2. **Initialize loop**:
   - Generate a session_id (UUID)
   - Track iteration, verification_history in conversation context
   - No file I/O needed — evolve_step stores all execution data in EventStore

4. **Enter the loop** (non-blocking background execution):

   ```
   while iteration < max_iterations:
       # Start evolve_step in background — returns immediately
       job = await start_evolve_step(lineage_id, seed_content, execute=true)
       job_id = job.meta["job_id"]
       cursor = job.meta["cursor"]

       # Poll for progress (non-blocking, shows intermediate state)
       # Use timeout_seconds=60 to reduce context consumption
       while not terminal:
           wait_result = await job_wait(job_id, cursor, timeout_seconds=60)
           cursor = wait_result.meta["cursor"]
           status = wait_result.meta["status"]
           # Report progress concisely (one line per poll)
           terminal = status in ("completed", "failed", "cancelled")

       # Fetch final result
       result = await job_result(job_id)

       # Parse QA from evolve_step response text
       # (EvolveStepHandler runs QA internally and appends verdict)
       verification.passed = (qa_verdict == "pass")
       verification.score = qa_score

       # Record in conversation context
       verification_history.append({
           "iteration": iteration,
           "passed": verification.passed,
           "score": verification.score,
           "verdict": qa_verdict
       })

       if verification.passed:
           # SUCCESS
           break

       # Failed - analyze and continue
       iteration += 1

       if iteration >= max_iterations:
           # Max iterations reached
           break
   ```

   **Tool mapping:**
   - `start_evolve_step` = `mobius_start_evolve_step`
   - `job_wait` = `mobius_job_wait`
   - `job_result` = `mobius_job_result`

4. **On termination**, display a next-step:
   - **Success** (QA passed): `Next: mob evaluate for formal 3-stage verification`
   - **Max iterations reached**: `Next: mob interview to re-examine the problem — or mob unstuck to try a different approach`

6. **Report progress** each iteration:
   ```
   [Ralph Iteration <i>/<max>]
   Execution complete. Running QA...

   QA Verdict: <PASS/REVISE/FAIL> (score: <score>)
   Differences:
     - <difference 1>
     - <difference 2>
   Suggestions:
     - <suggestion 1>
     - <suggestion 2>

   The boulder never stops. Continuing...
   ```

6. **Handle interruption**:
   - If user says "stop": exit gracefully
   - If user says "continue": call `mobius_query_events(aggregate_id=<lineage_id>)`
     to reconstruct iteration history from EventStore

## The Boulder Never Stops

This is the key phrase. Ralph does not give up:
- Each failure is data for the next attempt
- Verification drives the loop
- Only complete success or max iterations stops it

## Example

```
User: mob ralph fix all failing tests

[Ralph Iteration 1/10]
Started background execution (job_abc123)
Polling progress...
  Phase: Executing | AC Progress: 1/3
  Phase: Executing | AC Progress: 2/3
  Phase: Executing | AC Progress: 3/3
Execution complete. Fetching result...

QA Verdict: REVISE (score: 0.65)
Differences:
  - 3 tests still failing
  - Type errors in src/api.py
Suggestions:
  - Fix type annotations in api.py before retrying

The boulder never stops. Continuing...

[Ralph Iteration 2/10]
Executing in parallel...
Fixing remaining issues...
Running QA...

QA Verdict: REVISE (score: 0.85)
Differences:
  - 1 test edge case failing
Suggestions:
  - Add boundary check in parse_input()

The boulder never stops. Continuing...

[Ralph Iteration 3/10]
Executing in parallel...
Fixing edge case...
Running QA...

QA Verdict: PASS (score: 1.0)

Ralph COMPLETE
==============
Request: Fix all failing tests
Iterations: 3

QA History:
- Iteration 1: REVISE (0.65)
- Iteration 2: REVISE (0.85)
- Iteration 3: PASS (1.0)

All tests passing. Build successful.

Next: `mob evaluate` for formal 3-stage verification
```
