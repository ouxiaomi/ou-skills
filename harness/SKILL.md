---
name: harness
description: "Configure a long-running agent Harness system for any project with progress persistence, failure recovery, and task dependency management. Use when users request '/harness' or need autonomous multi-session agent work with checkpointing. Based on Anthropic and OpenAI engineering practices."
---

# Harness System — Long-Running Agent Framework

A robust framework enabling AI agents to work continuously across multiple context windows with automatic progress recovery, task dependencies, and standardized error handling.

Based on [Anthropic's engineering blog](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) and [stellarlinkco/myclaude](https://github.com/stellarlinkco/myclaude/tree/master/skills/harness).

## Design Principles

1. **Progress files ARE the context** — When context window resets, progress files + git history = full recovery
2. **Design for the agent, not the human** — Test output, docs, and task structure are the agent's primary interface
3. **Premature completion is the #1 failure mode** — Structured task lists with explicit completion criteria
4. **Standardize everything grep-able** — ERROR on same line, structured timestamps, consistent prefixes
5. **Idempotent everything** — Init scripts, task execution, environment setup must be safe to re-run
6. **Fail safe, not fail silent** — Every failure must have an explicit recovery strategy

## Core Files

| File | Purpose |
|------|---------|
| `feature_list.json` | Structured task list with dependencies, validation, and status |
| `claude-progress.txt` | Append-only log of all agent actions |
| `init.sh` | Environment initialization (idempotent) |
| `.claude/prompts/initializer.md` | First session prompt |
| `.claude/prompts/coding-agent.md` | Subsequent session prompt |
| `.claude/prompts/checkpoint.md` | Session resume after interruptions |

---

## Session Protocols

### Session Start (Execute Every Time)

Run these in EXACT order:

```
1. pwd                                              # Confirm working directory
2. cat claude-progress.txt | tail -200             # Read recent progress
3. cat feature_list.json                            # Read task structure
4. git log --oneline -10                            # Review recent commits
5. git diff --stat                                  # Check uncommitted changes
6. ./init.sh                                        # Verify environment
```

### Context Window Recovery (When Finding In-Progress Task)

If a task has `status: "in_progress` (previous session was interrupted):

1. Check `git diff --stat` for uncommitted changes
2. Check `git log --oneline -5` for recent commits
3. Check task's `checkpoints` array for last completed step
4. Use this decision matrix:

| Uncommitted? | Recent Commits? | Checkpoints? | Action |
|--------------|-----------------|--------------|--------|
| No | No | None | Mark failed: `[SESSION_TIMEOUT] No progress detected` |
| No | No | Some | Verify file state matches checkpoints. If yes, resume. If no, mark failed |
| No | Yes | Any | Run validation. Pass → completed, Fail → reset & mark failed |
| Yes | No/Yes | Any | Commit changes, run validation. Pass → completed, Fail → reset & mark failed |

Log recovery action: `[RECOVERY] [task-id] action="..." reason="..."`

---

## Task Management

### Task Selection Algorithm

Before selecting, validate dependencies:

1. **Cycle Detection**: Walk `depends_on` transitively. If a task appears in its own chain, mark failed with `[DEPENDENCY] Circular dependency detected`
2. **Blocked Propagation**: If a task depends on a permanently failed task, mark it blocked

Then pick next task by priority:
1. Pending tasks with ALL dependencies completed → sort by `priority` (high > medium > low), then by `id`
2. Failed tasks with attempts remaining and dependencies met → sort by priority, then oldest failure first

### Task Structure (feature_list.json)

```json
{
  "version": 2,
  "created": "2025-02-28T00:00:00Z",
  "session_config": {
    "max_tasks_per_session": 20,
    "max_sessions": 50
  },
  "features": [
    {
      "id": "F001",
      "title": "Implement user authentication",
      "category": "core",
      "status": "completed|pending|in_progress|failed|blocked",
      "priority": "high|medium|low",
      "depends_on": [],
      "attempts": 1,
      "max_attempts": 3,
      "started_at_commit": "abc1234",
      "validation": {
        "command": "npm test -- --testPathPattern=auth",
        "timeout_seconds": 300
      },
      "on_failure": {
        "cleanup": null
      },
      "error_log": [],
      "checkpoints": [],
      "completed_at": "2025-02-28T10:00:00Z",
      "created_at": "2025-02-28T00:00:00Z",
      "blockers": []
    }
  ],
  "session_count": 1,
  "last_session": "2025-02-28T10:00:00Z"
}
```

**Status Flow**: `pending` → `in_progress` → `completed` OR `failed`

### Feature Fields

| Field | Modifiable | Notes |
|-------|------------|-------|
| `status` | ✅ Yes | Use: `pending`, `in_progress`, `completed`, `failed`, `blocked` |
| `attempts` | ✅ Yes | Increment on each failure |
| `error_log` | ✅ Yes | Append error messages |
| `checkpoints` | ✅ Yes | Track step progress |
| `started_at_commit` | ✅ Yes | Set when starting |
| `completed_at` | ✅ Yes | Set when completed |
| `blockers` | ✅ Yes | Document blockers |
| `id` | ❌ Never | Never change |
| `title` | ❌ Never | Never change |
| `priority` | ❌ Never | Never change |
| `depends_on` | ❌ Never | Never change after creation |

---

## Task Execution Cycle

For each task, execute this exact sequence:

### 1. Claim Task
- Set `status: "in_progress"`
- Record `started_at_commit` = current HEAD
- Log: `[Starting] [F001] Implement user authentication (base=abc1234)`

### 2. Execute with Checkpoints
After each significant step, log:
```
[CHECKPOINT] [F001] step=2/4 "auth routes created, tests pending"
```
Append to task's `checkpoints` array: `{ "step": 2, "total": 4, "description": "...", "timestamp": "ISO" }`

### 3. Validate
Run task's `validation.command` with timeout:
```bash
timeout <timeout_seconds> <command>
```
- Exit 0 → PASS → mark `completed`
- Exit non-zero → FAIL → rollback and retry
- Timeout → treat as failure

### 4. Handle Outcome

**Success**:
```json
{
  "status": "completed",
  "completed_at": "2025-02-28T10:00:00Z"
}
```
Log: `[Completed] [F001] (commit abc1234)` and commit changes

**Failure**:
1. Increment `attempts`
2. Append error to `error_log`
3. Execute `git reset --hard <started_at_commit>` + `git clean -fd`
4. Run `on_failure.cleanup` if defined
5. Log: `[ERROR] [F001] [TASK_EXEC] Redis connection refused`
6. If `attempts >= max_attempts` → mark `failed`. Else → retry.

---

## Concurrency Control

Before modifying `feature_list.json`, acquire an exclusive lock:

```bash
LOCKDIR="/tmp/harness-$(pwd | shasum -a 256 | cut -c1-16).lock"

if ! mkdir "$LOCKDIR" 2>/dev/null; then
  LOCK_PID=$(cat "$LOCKDIR/pid" 2>/dev/null)
  if [ -n "$LOCK_PID" ] && kill -0 "$LOCK_PID" 2>/dev/null; then
    echo "ERROR: Another harness session is active (pid=$LOCK_PID)"; exit 1
  fi
  # Stale lock recovery
  STALE="$LOCKDIR.stale.$$"
  mv "$LOCKDIR" "$STALE" 2>/dev/null && rm -rf "$STALE"
  mkdir "$LOCKDIR" || { echo "ERROR: Lock contention"; exit 1; }
fi

echo "$$" > "$LOCKDIR/pid"
trap 'rm -rf "$LOCKDIR"' EXIT
```

Log lock acquisition: `[LOCK] acquired (pid=12345)`
Log lock release: `[LOCK] released`

---

## Error Handling & Recovery

### Error Categories

| Category | Default Recovery | Agent Action |
|----------|-----------------|--------------|
| `ENV_SETUP` | Re-run init, then STOP if still failing | Run `init.sh` again. If fails twice, stop — environment broken |
| `TASK_EXEC` | Rollback via `git reset --hard`, retry | Reset to `started_at_commit`, run cleanup, retry if attempts < max |
| `TEST_FAIL` | Rollback, retry with targeted fix | Reset, analyze test output, retry |
| `TIMEOUT` | Kill process, cleanup, retry | Wrap with `timeout`. On timeout, cleanup and retry (consider splitting task) |
| `DEPENDENCY` | Skip task, mark blocked | Log dependency failure, mark task `failed` |
| `SESSION_TIMEOUT` | Use Context Window Recovery | New session assesses progress via Recovery Protocol |

### JSON Corruption Recovery

Before every write, backup: `cp feature_list.json feature_list.json.bak`

If JSON is unparseable:
1. Check for `feature_list.json.bak`
2. If valid, restore from backup
3. If no valid backup: log `[ERROR] [ENV_SETUP] feature_list.json corrupted and unrecoverable` and STOP

---

## Logging Standard

All log entries use grep-friendly single-line format:

```
[ISO-timestamp] [SESSION-N] <TYPE> [task-id] [category] message
```

Types: `INIT`, `Starting`, `Completed`, `ERROR`, `CHECKPOINT`, `ROLLBACK`, `RECOVERY`, `STATS`, `LOCK`, `WARN`

### Filtering Examples

```bash
grep "ERROR" claude-progress.txt                    # All errors
grep "ERROR" claude-progress.txt | grep "TASK_EXEC" # Execution errors only
grep "SESSION-3" claude-progress.txt                # Session 3 activity
grep "STATS" claude-progress.txt                    # Session summaries
grep "CHECKPOINT" claude-progress.txt               # All checkpoints
grep "RECOVERY" claude-progress.txt                 # Recovery actions
```

---

## Session Statistics

At session end, append:
```
[STATS] tasks_total=10 completed=7 failed=1 pending=2 blocked=0 attempts_total=12 checkpoints=23
```

Update in feature_list.json:
- Increment `session_count`
- Set `last_session` to current timestamp

---

## Commands

```bash
/harness init              # Initialize harness in current directory
/harness status            # Show progress and stats
/harness add "task desc"   # Add a new task
```

### Init Command

1. Create `feature_list.json` with empty task list
2. Create `claude-progress.txt` with initialization entry
3. Optionally create `init.sh` template
4. Ask: add harness files to `.gitignore`?

### Status Command

Display:
1. Task summary: count by status (completed, failed, pending, blocked)
2. Per-task one-liner: `[status] id: title (attempts/max_attempts)`
3. Last 5 lines from `claude-progress.txt`
4. Session count and last session timestamp

(No lock needed — read-only)

### Add Command

Append new task with:
- Auto-incremented id (F001, F002, etc.)
- `status: "pending"`
- `max_attempts: 3`
- Empty `depends_on`

Prompt user for optional: `priority`, `depends_on`, `validation.command`, `timeout_seconds`

---

## Quick Start

```bash
python scripts/setup_harness.py [project_path]
```

If `project_path` omitted, uses current directory.

### What It Creates

| File | Purpose |
|------|---------|
| `feature_list.json` | Task structure with dependencies and validation |
| `claude-progress.txt` | Append-only session log |
| `init.sh` | Environment initialization |
| `.claude/prompts/initializer.md` | First session prompt |
| `.claude/prompts/coding-agent.md` | Regular session prompt |
| `.claude/prompts/checkpoint.md` | Recovery prompt |

---

## Project Type Detection

Auto-detects:

| Type | Detection | Init Adaptations |
|------|-----------|------------------|
| Node.js | `package.json` | npm install, supports Vue/React/Next.js |
| Python | `pyproject.toml`, `setup.py` | Prefers uv, falls back to pip |
| Go | `go.mod` | Standard Go module |
| Generic | None of above | Basic POSIX setup |

See `references/` for detailed templates:
- `references/nodejs.md`
- `references/python.md`
- `references/go.md`
- `references/generic.md`

---

## Completion Checklist

Before marking a feature complete:

- [ ] Code follows project conventions
- [ ] Tests pass (`validation.command` exits 0)
- [ ] Manual verification if needed
- [ ] Committed with descriptive message
- [ ] Progress logged in `claude-progress.txt`
- [ ] Status updated in `feature_list.json`