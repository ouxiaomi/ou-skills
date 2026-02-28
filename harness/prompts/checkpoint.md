# Checkpoint Agent Prompt

> Use this when resuming after a failure, crash, or interrupted session.

## When To Use This

- Agent crashed mid-session
- Session ended unexpectedly (context window reset)
- You found broken code from previous session
- You want to review state before continuing

---

## Recovery Protocol

### Step 1: Assess Current State

```bash
# Confirm location
pwd

# Check git state
git status
git diff --stat

# Read recent progress
cat claude-progress.txt | tail -200

# Read task structure
cat feature_list.json
```

### Step 2: Identify Interrupted Task

Look for task with `status: "in_progress`:

```bash
grep -A50 '"status": "in_progress"' feature_list.json
```

Check its details:
- `started_at_commit` - Where task began
- `checkpoints` - Last completed step
- `attempts` - How many times attempted

### Step 3: Analyze Checkpoints

If the task has checkpoints, verify file state matches claims:
- Do the files mentioned in checkpoints exist?
- Do they contain the expected content?

### Step 4: Decide Recovery Action

**Decision Matrix:**

| Uncommitted? | Recent Commits? | Checkpoints? | Action |
|--------------|-----------------|--------------|--------|
| No | No | None | Mark failed: `[SESSION_TIMEOUT] No progress detected` |
| No | No | Some | Verify file state. Match → resume. Mismatch → fail |
| No | Yes | Any | Run validation. Pass → completed. Fail → reset & fail |
| Yes | No/Yes | Any | Commit -> Run validation. Pass → complete. Fail → reset & fail |

### Step 5: Execute Recovery

**If resuming:**
- Log: `[RECOVERY] [F001] action="resume" reason="checkpoints match file state"`
- Continue from last checkpoint
- Set status back to `in_progress`

**If starting fresh:**
- Log: `[RECOVERY] [F001] action="reset" reason="progress lost"`
- Execute `git reset --hard <started_at_commit>` + `git clean -fd`
- Increment `attempts`, append error to `error_log`
- Mark status as `failed` (or retry if attempts < max_attempts)

---

## Context Window Recovery Details

When you find `status: "in_progress"` at session start:

1. **Check git state:**
   ```bash
   git diff --stat          # Uncommitted changes?
   git log --oneline -5     # Recent commits?
   git stash list           # Any stashed work?
   ```

2. **Verify commit exists:**
   ```bash
   git cat-file -t <started_at_commit>
   ```
   If missing → work was lost, mark failed

3. **Run validation if exists:**
   ```bash
   timeout <timeout_seconds> <validation.command>
   ```
   - Pass → mark completed
   - Fail → rollback, mark failed

---

## Template: Recovery Entry

When resuming, append to `claude-progress.txt`:

```
[RECOVERY] [F001] action="resume" reason="checkpoints verified, file state matches"
[RECOVERY] [F002] action="reset" reason="progress lost, no commits since start"
[RECOVERY] [F003] action="completed" reason="validation passed with uncommitted changes"
```

---

## Decision Flow

```
Session Start → Check for in_progress tasks?
│
├─ No → Normal session, pick next task
│
└─ Yes → Found F001 in_progress
   │
   ├─ checkpoints exist?
   │   ├─ Yes → File state matches?
   │   │       ├─ Yes → Resume from last step
   │   │       └─ No  → Mark failed, reset
   │   │
   │   └─ No → Recent commits?
   │           ├─ Yes → Run validation?
   │           │       ├─ Pass → Mark completed
   │           │       └─ Fail → Reset & fail
   │           │
   │           └─ No → Mark failed (SESSION_TIMEOUT)
   │
   └─ has uncommitted changes?
           ├─ Yes → Commit → Run validation?
           │           ├─ Pass → Mark completed
           │           └─ Fail → Reset & fail
           │
           └─ No → See above column
```

---

## Anti-Patterns

**DO NOT:**
- ❌ Jump into coding without assessing state
- ❌ Skip git status check
- ❌ Assume checkpoints are accurate without verifying
- ❌ Commit broken code
- ❌ Lose work by resetting without review
- ❌ Ignore failed dependencies (check `depends_on`)
- ❌ Skip the recovery protocol

---

## Checkpoint Key Insight

> The checkpoint exists because context windows are finite. When resuming, treat yourself as a new agent that needs to rapidly understand where work left off.

Read the files. Understand the history. Verify the state. Then proceed.

The key is: **Progress files + git history = full recovery**