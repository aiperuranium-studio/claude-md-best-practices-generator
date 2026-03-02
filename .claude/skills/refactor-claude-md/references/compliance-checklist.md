# CLAUDE.md Compliance Checklist — Derivation Procedure

This is **not** a fixed list of items. It is a procedure for deriving audit criteria from the current CLAUDE-MD-SOTA file at runtime. The SOTA file is dynamic — it changes when `/refresh-guidelines` runs.

---

## How to Use

1. Read the current SOTA file (enriched preferred, seed fallback — see SKILL.md Step 0).
2. For each SOTA Part, extract every rule or requirement expressed in that part.
3. Classify each extracted rule into one of the four audit categories below.
4. For each extracted rule, evaluate the target CLAUDE.md and assign a rating.

---

## Audit Categories

### Structural

Extract from **SOTA Part 1: Structural Standards**. Typical areas:
- Recommended sections and their expected order
- Size budget (line count limits)
- Formatting rules (bullet style, heading levels, emphasis patterns)
- @-import usage and file hierarchy conventions

### Content

Extract from **SOTA Part 2: Content Guidelines**. Typical areas:
- What content must be present (commands, architecture, conventions, gotchas)
- What content must be excluded (standard conventions, stale snippets, secrets, generic advice)
- Anti-patterns to flag (kitchen sink, vague instructions, over-specification, personality prompts)

### Integration

Extract from **SOTA Part 3: Integration Guidelines**. Typical areas:
- Separation of concerns: CLAUDE.md vs hooks vs skills vs rules
- MCP server documentation
- Subagent documentation
- @-import strategy

### Behavioral

Extract from **SOTA Part 4: Behavioral Patterns** and **Part 5: Maintenance Guidelines**. Typical areas:
- Verification command specificity
- Explore-then-plan workflow
- Scope and file discipline
- Review triggers and self-improving patterns

---

## Rating Scale

For each extracted rule, assign:

| Rating | Meaning |
|--------|---------|
| **PASS** | Target CLAUDE.md fully complies with this rule |
| **PARTIAL** | Present but needs improvement — describe what's missing |
| **FAIL** | Missing or violates the rule |
| **N/A** | Not applicable to this project |

---

## Report Format

Present results grouped by category:

```
### [Category Name]
Source: SOTA Part [N], sections [list]
Rules extracted: [count]

| # | Rule (from SOTA) | Rating | Finding |
|---|------------------|--------|---------|
| 1 | [exact rule text from current SOTA] | PASS/PARTIAL/FAIL/N/A | [details] |
```

This format ties every audit item back to the current SOTA text, ensuring traceability even after SOTA restructuring.
