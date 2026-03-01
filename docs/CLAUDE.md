# docs/ — Scoped Instructions

## Document Classification

Every file in this directory belongs to exactly one category:

- **Sub-products** — Application outputs, tracked in git:
  `CLAUDE-MD-SOTA.md`
- **Generated artifacts** — Produced locally by running tools, gitignored:
  `CLAUDE-MD-SOTA.enriched.md`, `guidelines-raw.json`, `insights-parsed.json`, `insights-raw.md`, `freshness-report.json`

## Sub-product Isolation

**IMPORTANT**: Sub-products may **only** hyperlink to other sub-products. They must **never** reference internal dev docs or generated artifacts. Only `CLAUDE-MD-SOTA.md` is a sub-product.

## Cross-referencing

**IMPORTANT**: When creating or modifying any file here, check all other docs files and add hyperlink references where missing. Every doc should link to related docs.

## Renumbering & Reference Validation

**IMPORTANT**: After any insertion, deletion, or reordering of numbered sections or references in docs, re-validate all numbering. Never leave orphaned references.
