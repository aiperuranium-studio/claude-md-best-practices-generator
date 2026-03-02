# scaffold-claude-md/ — Scoped Instructions

## Purpose

Scans a project's directory tree, identifies directories that need scoped CLAUDE.md files, and generates content following the current CLAUDE-MD-SOTA placement and content guidelines. No Python scripts — entirely Claude-guided with human approval gates.

## Key Files

| File | Role |
|------|------|
| `SKILL.md` | 7-step procedure: load guidelines → scan → assess → draft → approve → write |
| `references/directory-assessment.md` | Criteria for evaluating whether a directory needs its own CLAUDE.md |

## Source Selection Logic

Same as `/refactor-claude-md`:
- **Enriched first**: `docs/CLAUDE-MD-SOTA.enriched.md` if it exists and is non-empty.
- **Seed fallback**: `docs/CLAUDE-MD-SOTA.md` otherwise.
- **Abort**: If neither file exists, direct the user to run `/refresh-guidelines` first.

## Output

- New CLAUDE.md files in directories that need them.
- Optional update to root CLAUDE.md Project Structure section.
- No intermediate generated artifacts — proposals are presented in conversation.

## Constraints

- **IMPORTANT**: Never write files without explicit human approval at Step 5.
- Never overwrite existing CLAUDE.md files — this skill only creates new ones.
- Never duplicate content already in root or parent CLAUDE.md.
- All content follows the current SOTA guidelines, not hardcoded rules.
