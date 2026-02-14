---
name: harness
description: Configure a long-running agent Harness system for any project. Use when users request to set up Harness, configure long-running agent system, or say "/harness". Creates feature_list.json, claude-progress.txt, init.sh, and agent prompts. Supports Node.js, Python, Go, and generic projects with auto-detection.
---

# Harness System Setup

Configure a long-running agent Harness system for AI agents to work effectively across multiple context windows.

Based on [Anthropic's engineering blog](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents).

## Quick Start

Run the setup script:

```bash
python scripts/setup_harness.py [project_path]
```

If `project_path` is omitted, uses current directory.

## What It Creates

| File | Purpose |
|------|---------|
| `feature_list.json` | Feature requirements with status tracking |
| `claude-progress.txt` | Session progress log |
| `init.sh` | Environment initialization script |
| `.claude/prompts/initializer.md` | Initializer agent prompt |
| `.claude/prompts/coding-agent.md` | Coding agent prompt |
| `CLAUDE.md` | Updates with Harness documentation |

## Project Type Detection

Auto-detects and adapts to:

| Type | Detection File | Notes |
|------|----------------|-------|
| Node.js | `package.json` | Detects Vue, React, Next.js, Svelte |
| Python | `pyproject.toml`, `setup.py` | Prefers uv over pip |
| Go | `go.mod` | Standard Go module |
| Generic | None of above | Basic setup |

## Workflow

### Session Start

1. **Locate**: `pwd`
2. **Review**: `cat claude-progress.txt` and `git log --oneline -10`
3. **Select**: Read `feature_list.json`, pick highest priority pending feature
4. **Verify**: `./init.sh`

### Session End

1. Commit with descriptive message
2. Update `claude-progress.txt`
3. Update feature status in `feature_list.json`

## Feature List Format

```json
{
  "project": "my-project",
  "version": "1.0.0",
  "features": [
    {
      "id": "F001",
      "category": "core",
      "description": "Feature description",
      "priority": "high",
      "status": "completed|pending|failed",
      "steps": ["step1", "step2"],
      "testCommand": "Verification command"
    }
  ]
}
```

**Rules:**
- Only modify `status` field
- Never delete or change feature descriptions
- Status values: `completed`, `pending`, `failed`

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
