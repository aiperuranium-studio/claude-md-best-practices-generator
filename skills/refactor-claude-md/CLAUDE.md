# refactor-claude-md/ — Scoped Instructions

## Purpose

Audits any CLAUDE.md (root or scoped) against CLAUDE-MD-SOTA guidelines and produces a compliant refactored version. Accepts an optional target path — defaults to the project root CLAUDE.md. No Python scripts — entirely Claude-guided with human approval gates.

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

- Refactored CLAUDE.md written to the target path (root or scoped, overwrite in place).
- For scoped files, the parent CLAUDE.md is also read (to detect duplication) but not modified.
- No intermediate generated artifacts — the audit report is presented in conversation.

## Constraints

- **IMPORTANT**: Never apply changes without explicit human approval at Step 5.
- All changes must be traceable to specific text in the current SOTA file — nothing is invented.
- Never remove project-specific content that doesn't violate guidelines.
- Refactored file must respect the size budget from the current SOTA.
