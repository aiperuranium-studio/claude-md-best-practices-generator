# CLAUDE.md Quality Standards

Rules for editing any CLAUDE.md file in this project.

## Read Guidelines Before Editing

**IMPORTANT**: Before creating or modifying any CLAUDE.md file, read the current generation guidelines:

1. Check if `docs/CLAUDE-MD-SOTA.enriched.md` exists — use it (enriched = seed + /insights).
2. If not, use `docs/CLAUDE-MD-SOTA.md` (seed, web sources only).
3. Apply the structural, content, integration, and behavioral rules found in whichever file you loaded.

Do NOT rely on memorized guidelines — the SOTA files change when `/refresh-guidelines` runs.

## Project Conventions (stable, not SOTA-derived)

- **Prefer pointers to copies** — Use `file:line` references to authoritative source code. Never embed code snippets in CLAUDE.md files.
- **Cross-referencing** — Sub-product CLAUDE.md files may only hyperlink to other sub-products. After modifying any `docs/` file, check all other docs files for missing cross-references.
- **Renumbering** — After any insertion, deletion, or reordering of numbered sections, re-validate all references across docs.
