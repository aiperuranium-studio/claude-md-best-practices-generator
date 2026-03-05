---
paths:
  - "**/CLAUDE.md"
  - "**/CLAUDE.local.md"
---
# CLAUDE.md Quality Standards

## Read Guidelines Before Editing

ALWAYS load the current SOTA before creating or modifying any CLAUDE.md file:

1. Check if `docs/CLAUDE-MD-SOTA.enriched.md` exists — use it (enriched = seed + /insights).
2. If not, use `docs/CLAUDE-MD-SOTA.md` (seed, web sources only).
3. Apply the structural, content, integration, and behavioral rules from the loaded file.

Do NOT rely on memorized guidelines — the SOTA files change when `/refresh-guidelines` runs.

## Project Conventions

- **Prefer pointers to copies** — Use `file:line` references to authoritative source code. Never embed code snippets in CLAUDE.md files.
- **Cross-referencing** — Sub-product CLAUDE.md files may only hyperlink to other sub-products. After modifying any `docs/` file, check all other docs files for missing cross-references.
- **Renumbering** — After any insertion, deletion, or reordering of numbered sections, re-validate all references across docs.
