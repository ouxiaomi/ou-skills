# Checkpoint Agent Prompt

> Use this when resuming after a failure, crash, or interrupted session.

## When To Use This

- Agent crashed mid-session
- Session ended unexpectedly
- You found broken code from previous session
- You want to review state before continuing

## Recovery Protocol

### Step 1: Assess Current State

```bash
# What's the current situation?
pwd
git status
cat claude-progress.txt | tail -20
```

### Step 2: Understand Recent Work

```bash
# What did the previous agent try to do?
git log --oneline -5
git diff HEAD~1

# What was the last feature in progress?
grep -A5 "Next:" claude-progress.txt
```

### Step 3: Handle Uncommitted Changes

```bash
# Check for modifications
git status --short
```

**If changes look good:**
```bash
git add -A
git commit -m "WIP: [describe what was in progress]"
```

**If changes are broken:**
```bash
# Reset to last known good state
git checkout -- .
echo "⚠️ Reset to last commit - review progress file for next steps"
```

### Step 4: Check Feature Status

```bash
# Was the last feature completed or in-progress?
cat feature_list.json | grep -A10 '"status": "pending"'
```

## Template: Recovery Entry

When resume is needed, add this to `claude-progress.txt`:

```markdown
---
### Recovery Session: YYYY-MM-DD HH:MM

**Previous State:** Session crashed during F003 implementation
**Git Status:** [clean / has uncommitted changes]
**Decision:** [commit changes / reset to last commit]

**Resuming with:** F003 - User authentication
---
```

## Decision Tree

```
┌─ Did agent crash?
│  ├─ Yes → Check git status
│  │         ├─ Good changes → Commit with WIP prefix
│  │         └─ Broken code → Reset, read checkpoint
│  └─ No → Continue normal session
│
├─ Uncommitted changes exist?
│  ├─ Yes → Evaluate quality
│  │         ├─ Good → Commit
│  │         └─ Bad → Reset
│  └─ No → Read progress, pick feature
│
└─ Environment works?
   ├─ Yes → Proceed
   └─ No → Fix init.sh first
```

## Anti-Patterns

**DO NOT:**
- ❌ Jump into coding without assessing state
- ❌ Commit broken code
- ❌ Lose work by resetting without review
- ❌ Ignore the recovery protocol

## Checkpoint Key Insight

> The checkpoint exists because context windows are finite. When resuming, treat yourself as a new agent that needs to rapidly understand where work left off.

Read the files. Understand the history. Then proceed.