---
name: refactor-claude-md
description: Audits the root CLAUDE.md against CLAUDE-MD-SOTA guidelines and produces a compliant refactored version. Uses enriched guidelines when available, falls back to seed.
disable-model-invocation: true
allowed-tools: Bash, Read, Write, Glob, Grep
---

# /refactor-claude-md

Audit the project's root `CLAUDE.md` against the CLAUDE-MD-SOTA guidelines and produce a refactored version that fully complies with documented best practices.

## When to Use

- After running `/refresh-guidelines` to update the SOTA reference.
- When the root CLAUDE.md has grown organically and needs realignment.
- When onboarding a project to CLAUDE-MD-SOTA standards for the first time.
- Periodically, to catch drift between the CLAUDE.md and current guidelines.

## Prerequisites

- At least one guidelines file must exist: `docs/CLAUDE-MD-SOTA.enriched.md` (preferred) or `docs/CLAUDE-MD-SOTA.md` (seed fallback).
- A root `CLAUDE.md` must exist (the file being refactored).

## Procedure

Follow these steps in order. Do NOT skip steps or auto-approve — human review is required.

### Step 0: Source selection

Determine which guidelines file to use:

1. Check if `docs/CLAUDE-MD-SOTA.enriched.md` exists and is non-empty.
2. If yes, use it. If no, use `docs/CLAUDE-MD-SOTA.md` (seed).
3. Report to the user: "Using **[enriched/seed]** guidelines dated [file mtime]."

If neither file exists, abort: "No guidelines file found. Run `/refresh-guidelines` first."

### Step 1: Read guidelines and extract audit criteria

Read the selected CLAUDE-MD-SOTA file in full. Then, following the derivation procedure in `$CLAUDE_PLUGIN_ROOT/references/compliance-checklist.md`, extract every rule or requirement from each SOTA Part and classify into the four audit categories:

- **Structural** — from Part 1 (sections, order, size, formatting, @-imports, hierarchy)
- **Content** — from Part 2 (what to include, exclude, anti-patterns)
- **Integration** — from Part 3 (hooks, skills, rules, MCP, subagents)
- **Behavioral** — from Parts 4-5 (verification, workflows, scope discipline, maintenance)

The extracted rules become the **dynamic checklist** for Step 3. Do not use memorized or hardcoded criteria — derive them fresh from the current SOTA file.

### Step 2: Read current CLAUDE.md

Read the project root `CLAUDE.md` in full. Note:

- Current sections and their order.
- Line count.
- Formatting patterns (bullets vs prose, specificity level).
- Content categories present and absent.

### Step 3: Compliance audit

Evaluate the current CLAUDE.md against the dynamic checklist extracted in Step 1. For each rule, assign:

- **PASS** — Fully compliant.
- **PARTIAL** — Present but needs improvement (describe what's missing).
- **FAIL** — Missing or violates the guideline.
- **N/A** — Not applicable to this project.

Every audit item must be traceable to a specific passage in the current SOTA file (quote the relevant text).

### Step 4: Present audit report

Present a structured report:

```
## CLAUDE.md Compliance Audit

**Source**: [enriched/seed] guidelines
**File**: CLAUDE.md ({N} lines)

### Scorecard

| Category | Pass | Partial | Fail | N/A |
|----------|------|---------|------|-----|
| Structural (Part 1) | {n} | {n} | {n} | {n} |
| Content (Part 2) | {n} | {n} | {n} | {n} |
| Integration (Part 3) | {n} | {n} | {n} | {n} |
| Behavioral (Part 4) | {n} | {n} | {n} | {n} |

### Detailed Findings

#### FAIL items (must fix)
| # | Checklist Item | Finding | Proposed Fix |
|---|----------------|---------|--------------|

#### PARTIAL items (should fix)
| # | Checklist Item | Finding | Proposed Fix |
|---|----------------|---------|--------------|

#### PASS items (no action)
[list]
```

### Step 5: Human approval

Present the audit report and proposed changes. **Wait for explicit human approval.** The user may:

- Approve all proposed fixes.
- Approve selectively (accept some, reject others).
- Reject all changes.
- Request modifications before approval.

**Never auto-approve. Never apply changes without explicit confirmation.**

### Step 6: Apply changes

On approval, write the refactored `CLAUDE.md`:

- Apply all approved fixes.
- Preserve any project-specific content that doesn't violate guidelines.
- Maintain the section order and formatting rules from the current SOTA.
- Respect the size budget from the current SOTA.
- Ensure all commands are specific and actionable per the current SOTA.

Write the file. Do NOT present the content in chat first — write directly.

### Step 7: Verify

Re-run the compliance audit (Step 3) on the newly written file. Present a summary:

```
## Post-Refactor Verification

| Category | Before | After |
|----------|--------|-------|
| Structural | {n}/{total} pass | {n}/{total} pass |
| Content | {n}/{total} pass | {n}/{total} pass |
| Integration | {n}/{total} pass | {n}/{total} pass |
| Behavioral | {n}/{total} pass | {n}/{total} pass |

**Remaining issues**: [list any FAIL/PARTIAL items, or "None — fully compliant"]
```

## References

- `$CLAUDE_PLUGIN_ROOT/references/compliance-checklist.md` — Procedure for deriving audit criteria from the current CLAUDE-MD-SOTA at runtime.
- `docs/CLAUDE-MD-SOTA.md` — Seed guidelines (web sources only, git-tracked).
- `docs/CLAUDE-MD-SOTA.enriched.md` — Enriched guidelines (seed + /insights, gitignored).

## Constraints

- The refactored CLAUDE.md must respect the **size budget from the current SOTA**.
- All changes must be **traceable to specific SOTA text** — nothing is invented.
- The process must be **idempotent** — running again on an already-compliant file produces no changes.
- **Never remove project-specific content** that doesn't violate guidelines — only restructure and improve it.
- Conflicts between project conventions and SOTA guidelines are **flagged for human decision**, never auto-resolved.
