---
name: harness
description: Configure a long-running agent Harness system for any project. Use when users request to set up Harness, configure long-running agent system, or say "/harness". Creates feature_list.json, claude-progress.txt, init.sh, and agent prompts. Supports Node.js, Python, Go, and generic projects with auto-detection.
---

# Harness System Setup

Configure a long-running agent Harness system for AI agents to work effectively across multiple context windows.

Based on [Anthropic's engineering blog](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents).

## The Problem: Agent Failure Modes

Long-running agents fail due to three core issues:

| Failure Mode | Description | Solution |
|--------------|-------------|----------|
| **No Structure** | Agent receives one giant goal and doesn't know where to start | Feature list with clear priorities |
| **No Memory** | No persistence between sessions; starts fresh each time | Progress file + git history |
| **No Accountability** | Can't track what was done or what remains | Structured progress tracking |

## The Solution: Two-Agent Pattern

### 1. Initializer Agent (Runs Once)

The very first agent session establishes foundational infrastructure:

- **init.sh** - How to start dev server and run the app
- **claude-progress.txt** - Log of what agents have accomplished
- **feature_list.json** - Structured feature backlog with priorities
- **Initial git commit** - Captures baseline state

### 2. Coding Agent (Runs Every Session)

Subsequent sessions read context files and continue incrementally:

- Read progress file before touching code
- Pick highest-priority pending feature
- Make incremental progress
- Commit frequently with descriptive messages

## Quick Start

Run the setup script:

```bash
python scripts/setup_harness.py [project_path]
```

If `project_path` is omitted, uses current directory.

## What It Creates

| File | Purpose |
|------|---------|
| `feature_list.json` | Feature requirements with status, priority, and test command |
| `claude-progress.txt` | Session progress log with timestamps |
| `init.sh` | Environment initialization script (verifies deps, starts dev server) |
| `.claude/prompts/initializer.md` | Initializer agent prompt (read on first session) |
| `.claude/prompts/coding-agent.md` | Coding agent prompt (read on subsequent sessions) |
| `.claude/prompts/checkpoint.md` | Checkpoint for session resume after failures |
| `CLAUDE.md` | Updates with Harness system documentation |

### Key Insight

> **The key insight**: When starting with a fresh context window, agents need a way to quickly understand the state of work. This is accomplished with `claude-progress.txt` alongside git history.

## Project Type Detection

Auto-detects and adapts to:

| Type | Detection File | Notes |
|------|----------------|-------|
| Node.js | `package.json` | Detects Vue, React, Next.js, Svelte |
| Python | `pyproject.toml`, `setup.py` | Prefers uv over pip |
| Go | `go.mod` | Standard Go module |
| Generic | None of above | Basic setup |

## Session Protocols

### Session Start (Mandatory Order)

Every session MUST follow this order - do not skip steps:

```
1. pwd                           # Confirm working directory
2. cat claude-progress.txt       # Read progress history
3. git log --oneline -10         # Review recent commits
4. cat feature_list.json         # Understand remaining work
5. ./init.sh                     # Verify environment works
```

**Critical**: If init.sh fails, do NOT proceed with coding. Fix the environment first.

### Feature Selection Algorithm

After reading context, select the next feature:

1. Filter features with `status: "pending"`
2. Sort by priority: `high` → `medium` → `low`
3. Within same priority, use `id` order (F001, F002, etc.)
4. Announce what you're working on before starting

### Session End

Complete these before the session ends:

1. **Commit** - Descriptive message following conventional commits:
   ```
   feat(F003): Implement user authentication
   
   - Added login/logout endpoints
   - Integrated JWT tokens
   - Updated feature status to completed
   ```

2. **Update Progress** - Append to `claude-progress.txt`:
   ```
   ### 2025-02-11 15:30
   
   Completed: F003 - User authentication
   Next: F004 - Dashboard API endpoints
   Blockers: None
   ```

3. **Update Feature Status** - Set `status` in `feature_list.json`:
   - `completed` - Feature works and is tested
   - `pending` - Not started or in progress
   - `failed` - Encountered significant blocker

## Feature List Format

```json
{
  "project": "my-project",
  "version": "1.0.0",
  "lastUpdated": "2025-02-11",
  "features": [
    {
      "id": "F001",
      "category": "core",
      "description": "Feature description",
      "priority": "high",
      "status": "completed|pending|failed",
      "steps": ["step1", "step2"],
      "testCommand": "Verification command",
      "createdAt": "2025-02-11",
      "completedAt": null,
      "blockers": []
    }
  ]
}
```

**Field Rules:**

| Field | Modifiable | Notes |
|-------|------------|-------|
| `status` | ✅ Yes | Only use: `completed`, `pending`, `failed` |
| `steps` | ✅ Yes | Update as implementation evolves |
| `testCommand` | ✅ Yes | Verification command |
| `completedAt` | ✅ Yes | Set when status → `completed` |
| `blockers` | ✅ Yes | Array of blocker descriptions |
| `id` | ❌ No | Never change |
| `description` | ❌ No | Never change |
| `priority` | ❌ No | Never change after creation |

## Failure Recovery

When things go wrong, follow this recovery protocol:

### Agent Crashes Mid-Session

1. Check `claude-progress.txt` for last known state
2. Run `git status` to see uncommitted changes
3. Either:
   - **If changes are good**: Commit them with "WIP: ..." prefix
   - **If changes are broken**: `git checkout -- .` to reset

### Feature Implementation Fails

1. Mark feature as `failed` in feature_list.json
2. Document blockers in the `blockers` array
3. Add notes in `claude-progress.txt`
4. Move to next available feature

### Environment Breaks

1. **Never** try to code in a broken environment
2. Fix init.sh first
3. Run `./init.sh` to verify fix
4. Only then continue with feature work

## Context Preservation

### What Persists Between Sessions

- **Files**: feature_list.json, claude-progress.txt, git history
- **Environment**: init.sh recreates the same setup each time
- **Knowledge**: All progress and decisions in plaintext files

### What Doesn't Persist

- **LLM context window**: Fresh start each session
- **In-memory state**: Nothing lives in RAM across sessions
- **Terminal history**: Start fresh

> **This is intentional**: The harness treats every session as a new agent that must read the context files. This is the key to working on projects that exceed the context window.

## Project-Specific Templates

For detailed init.sh templates and patterns:

- **Node.js**: See [references/nodejs.md](references/nodejs.md)
- **Python**: See [references/python.md](references/python.md)
- **Go**: See [references/go.md](references/go.md)
- **Generic**: See [references/generic.md](references/generic.md)

## Completion Checklist

Before marking a feature complete:

- [ ] Code follows project conventions
- [ ] Tests pass (if applicable)
- [ ] Manual verification successful
- [ ] Documentation updated (if needed)
