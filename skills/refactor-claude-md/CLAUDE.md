# refactor-claude-md/ — Scoped Instructions

## Purpose

Audits a project's root CLAUDE.md against CLAUDE-MD-SOTA guidelines and produces a compliant refactored version. No Python scripts — entirely Claude-guided with human approval gates.

## Key Files

| File | Role |
|------|------|
| `SKILL.md` | 8-step procedure: source selection → audit → approval → refactor → verify |
| `references/compliance-checklist.md` | Procedure for deriving audit criteria from the current SOTA at runtime |

## Source Selection Logic

- **Enriched first**: `docs/CLAUDE-MD-SOTA.enriched.md` if it exists and is non-empty.
- **Seed fallback**: `docs/CLAUDE-MD-SOTA.md` otherwise.
- **Abort**: If neither file exists, direct the user to run `/refresh-guidelines` first.

The user can override source selection in conversation (e.g., "use seed only").

## Output

- Refactored `CLAUDE.md` at the project root (overwrite in place).
- No intermediate generated artifacts — the audit report is presented in conversation.

## Constraints

- **IMPORTANT**: Never apply changes without explicit human approval at Step 5.
- All changes must be traceable to specific text in the current SOTA file — nothing is invented.
- Never remove project-specific content that doesn't violate guidelines.
- Refactored file must respect the size budget from the current SOTA.
