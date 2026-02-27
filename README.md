# Claude Code Project Igniter

An AI-driven tool that maintains a catalog of Claude Code entities (agents, skills, rules, hooks) and intelligently selects, specialises, and installs only the relevant ones into a target project. Run `/ignite` after planning a new project's architecture to get a fully tailored Claude Code configuration — with transparent gap reporting for uncovered technologies.

---

## Prerequisites

- **Git** — for cloning sources
- **Python 3.10+** — for the manifest builder and guidelines pipeline
- **[Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code)** — the tool this igniter configures

---

## Installation

The igniter must be **attached** to your Claude Code session so its `.claude/` directory is discovered alongside your target project.

### Option A — `--add-dir` (recommended)

```bash
git clone https://github.com/your-org/claude-code-project-igniter ~/igniter
claude --add-dir ~/igniter
```

Claude Code merges the igniter's `.claude/` directory with your target project's. All skills (`/ignite`, `/sync-catalog`, `/add-source`, `/refresh-guidelines`) become available in every session.

### Option B — Symlink

```bash
git clone https://github.com/your-org/claude-code-project-igniter ~/igniter
ln -s ~/igniter/.claude/skills/ignite ~/.claude/skills/ignite
ln -s ~/igniter/.claude/skills/sync-catalog ~/.claude/skills/sync-catalog
# repeat for other skills
```

### Option C — Shell alias

Add to `~/.bashrc` or `~/.zshrc`:

```bash
alias claude-ignite='claude --add-dir ~/igniter'
```

---

## Quick Start

```bash
# 1. Clone the igniter once
git clone https://github.com/your-org/claude-code-project-igniter ~/igniter

# 2. Build the entity catalog (clones everything-claude-code + generates manifest.json)
claude --add-dir ~/igniter
# then inside Claude Code:
/sync-catalog

# 3. Open your target project
cd ~/my-new-project

# 4. Run the igniter
claude --add-dir ~/igniter
# then inside Claude Code:
/ignite
```

`/ignite` will:
1. Scan your project files and conversation history to detect your tech stack
2. Present a selection report for your approval
3. Install and specialise the chosen entities into `.claude/`
4. Generate a tailored `CLAUDE.md` with a Known Gaps section

---

## Skills Reference

| Skill | Description |
|-------|-------------|
| `/ignite` | Selects, specialises, and installs catalog entities into a target project. Generates `CLAUDE.md`. |
| `/sync-catalog` | Clones/updates remote sources and rebuilds `catalog/manifest.json`. Run before first use and periodically to refresh. |
| `/add-source` | Registers a new remote entity source in `catalog/sources.json` and optionally syncs it immediately. |
| `/refresh-guidelines` | Enriches `docs/CLAUDE-MD-SOTA.md` from curated web sources + `/insights` data. Improves CLAUDE.md generation quality. |

---

## Catalog Structure

```
catalog/
├── sources.json          # Source registry — where entities come from
├── manifest.json         # Auto-generated entity index (gitignored, rebuilt by /sync-catalog)
└── sources/
    ├── everything-claude-code/   # Synced remote source (gitignored)
    └── local/                    # User custom entities (tracked in git, always wins)
        ├── agents/
        ├── skills/
        ├── commands/
        └── rules/
```

The `local/` source has **priority 1** — any entity you place here overrides the equivalent from any remote source. Drop a `my-agent.md` in `catalog/sources/local/agents/` and it will be selected over the upstream version.

---

## Extending the Catalog

### Add your own entities

Place custom entities in `catalog/sources/local/`:

```bash
# Custom agent
cat > catalog/sources/local/agents/my-reviewer.md << 'EOF'
# My Custom Reviewer
...
EOF

# Rebuild manifest to include it
/sync-catalog
```

### Add a remote source

```
/add-source
```

Prompts for URL, branch, and entity paths. Registers the source in `sources.json` and optionally syncs it.
