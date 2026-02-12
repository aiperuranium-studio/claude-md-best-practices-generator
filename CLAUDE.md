# Claude Code Project Igniter

An AI-driven tool that maintains a catalog of Claude Code entities (agents, skills, rules, hooks) and intelligently selects, specializes, and installs only the relevant ones into a target project.

## Authoritative Documents

- **Architecture & design**: [docs/IGNITER-PLUS-CLAUDE-MD-SOTA-PLAN.md](docs/IGNITER-PLUS-CLAUDE-MD-SOTA-PLAN.md)
- **CLAUDE.md generation rules**: [docs/CLAUDE-MD-SOTA.md](docs/CLAUDE-MD-SOTA.md)
- **Development agenda**: [docs/IGNITER-PLUS-CLAUDE-MD-SOTA-DEV-AGENDA.md](docs/IGNITER-PLUS-CLAUDE-MD-SOTA-DEV-AGENDA.md)

## Behavioral Rules

**1. Write-first, never chat-first**
> When asked to create a plan, save it to a file, or write documentation, ALWAYS write it to a file immediately. Do NOT present it in plan mode or chat output first — write directly to the requested file path. If no path is specified, ask for one before proceeding.

**2. No preemptive execution**
> Do NOT start implementing or running code unless the user explicitly asks you to. When presenting a plan or analysis, wait for user approval before taking action. Never run code preemptively.

**3. No scope creep**
> Do NOT extrapolate, suggest features, or expand scope beyond what was explicitly requested. If you have ideas, mention them briefly at the end but do not elaborate unless asked.

**4. Clarify before acting**
> When you don't understand a request (especially if it's in Italian or domain-specific), ASK for clarification rather than guessing and jumping into action. It's better to ask one question than to waste time on a wrong approach.

## Project Conventions

- **Python scripts**: Python 3.10+, standard library only (external deps documented explicitly when unavoidable).
- **Shell scripts**: `#!/usr/bin/env bash`, POSIX-compatible where possible.
- **Documentation & entity definitions**: Markdown.
- **Configuration**: JSON (`sources.json`, `manifest.json`, `settings.json`).

## Project Structure

```
claude-code-project-igniter/
├── CLAUDE.md                              # This file
├── .gitignore
├── docs/
│   ├── IGNITER-PLUS-CLAUDE-MD-SOTA-PLAN.md # Architecture & design (unified plan)
│   ├── CLAUDE-MD-SOTA.md             # Authoritative CLAUDE.md generation reference
│   ├── IGNITER-PLUS-CLAUDE-MD-SOTA-DEV-AGENDA.md  # Sprint-based development plan
│   ├── guidelines-raw.json           # Output of fetch-guidelines.py (gitignored)
│   └── old/                          # Archived pre-merge plans
│       ├── IGNITER-PLAN.md
│       └── CLAUDE-MD-SOTA-PLAN.md
├── .claude/
│   ├── settings.json
│   ├── skills/
│   │   ├── ignite/                        # /ignite skill
│   │   │   ├── SKILL.md
│   │   │   ├── references/
│   │   │   │   ├── ignite-workflow.md
│   │   │   │   ├── specialization-guide.md
│   │   │   │   └── gap-analysis-guide.md
│   │   │   └── scripts/
│   │   │       └── build-manifest.py
│   │   ├── sync-catalog/                  # /sync-catalog skill
│   │   │   ├── SKILL.md
│   │   │   └── scripts/
│   │   │       └── sync-catalog.sh
│   │   ├── add-source/                    # /add-source skill
│   │   │   └── SKILL.md
│   │   └── refresh-guidelines/            # /refresh-guidelines skill
│   │       ├── SKILL.md
│   │       ├── references/
│   │       │   ├── curated-sources.md
│   │       │   └── enrichment-procedure.md
│   │       └── scripts/
│   │           └── fetch-guidelines.py
│   └── agents/
│       └── catalog-inspector.md
├── catalog/
│   ├── sources.json                       # Source registry
│   ├── manifest.json                      # Auto-generated entity index
│   └── sources/                           # Downloaded repos (gitignored except local/)
│       ├── everything-claude-code/
│       └── local/                         # User's custom entities
```

## Task Management

> For long multi-file tasks, use TodoWrite to create a checklist of all files/sections to process BEFORE starting work. Update the checklist as each item completes.
