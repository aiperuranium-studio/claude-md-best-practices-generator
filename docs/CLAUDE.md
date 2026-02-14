# docs/ — Scoped Instructions

## Document Classification

Every file in this directory belongs to exactly one category:

- **Internal dev docs** — Development-only, never shipped:
  `IGNITER-PLUS-CLAUDE-MD-SOTA-PLAN.md`, `IGNITER-PLUS-CLAUDE-MD-SOTA-DEV-AGENDA.md`, `old/`
- **Sub-products** — Application outputs, tracked in git:
  `CLAUDE-MD-SOTA.md`, `SOURCE-SCHEMA.md`
- **Generated artifacts** — Produced locally by running tools, gitignored:
  `CLAUDE-MD-SOTA.enriched.md`, `guidelines-raw.json`, `insights-parsed.json`, `insights-raw.md`

## Sub-product Isolation

Sub-products may **only** hyperlink to other sub-products. They must **never** reference internal dev docs. Internal dev docs may freely reference anything.

## Cross-referencing

When creating or modifying any file here, check all other docs files and add hyperlink references where missing. Every doc should link to related docs.

## Renumbering & Reference Validation

After any insertion, deletion, or reordering of numbered sections or references, re-validate all numbering. Never leave orphaned references.

## Pointers Over Copies

Don't embed code snippets in documentation — use `file:line` references to point at the authoritative source code.
