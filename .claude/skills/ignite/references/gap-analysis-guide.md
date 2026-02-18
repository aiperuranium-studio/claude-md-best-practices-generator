# Gap Analysis Guide

Methodology for assessing entity coverage and reporting gaps when `/ignite` cannot find dedicated entities for technologies in the target project's Technology Profile. Read alongside [`SKILL.md`](../SKILL.md) (Step 4 gap summary and Step 6 Known Gaps section) and [`ignite-workflow.md`](ignite-workflow.md).

---

## Coverage Levels

Every technology in the Technology Profile is assessed against the catalog and assigned one of three coverage levels:

### Full Coverage

A dedicated entity exists that specifically targets this technology.

- The entity's `tags.languages` or `tags.frameworks` explicitly includes this technology.
- The entity's content contains specific guidance, examples, or rules for this technology.
- Example: Python project with `python-patterns` skill → **Full** coverage for Python.

### Partial Coverage

No dedicated entity exists, but universal or parent-level entities provide some coverage.

- A universal entity (scope: `universal`) covers the general practice area.
- A parent-language entity covers the language but not the specific framework.
- Example: SQLAlchemy with only `python-patterns` (covers Python generally but not SQLAlchemy specifically) → **Partial** coverage.

### No Coverage

No relevant entities exist in the catalog for this technology.

- No entity tags match the technology.
- No universal entities provide meaningful coverage for this area.
- Example: Elixir project with no Elixir-tagged entities in the catalog → **None**.

---

## Gap Report Structure

For each technology with Partial or No coverage, produce a gap entry:

| Field | Description |
|-------|-------------|
| **Technology** | Name of the technology (e.g., "SQLAlchemy", "Redis", "Elixir") |
| **Coverage** | Full / Partial / None |
| **Existing Entities** | What entities provide partial coverage (empty for None) |
| **Missing** | What kind of entity would close the gap (e.g., "dedicated SQLAlchemy patterns skill") |
| **Impact** | High / Medium / Low — how much this gap affects the project |
| **Recommendation** | Actionable next step (see Recommendations below) |

### Impact Assessment

| Impact | Criteria |
|--------|----------|
| **High** | Primary language or framework with no coverage. Core to the project's architecture. |
| **Medium** | Secondary framework or tool with partial coverage. Important but not blocking. |
| **Low** | Minor tool, build dependency, or infrastructure component. Universal practices apply. |

---

## Recommendations

For each gap, recommend one of these actions (in order of preference):

### 1. Accept Partial Coverage

When universal or parent-level entities provide sufficient guidance.

- **When**: The technology follows standard patterns covered by universal entities (e.g., REST API best practices apply to any HTTP framework).
- **What to tell the user**: "Universal entities cover the fundamentals. Consider supplementing with project-specific notes in your CLAUDE.md."

### 2. Create Custom Entity in `local/`

When the user can define project-specific guidance.

- **When**: The technology is important to the project and the user has domain knowledge to write guidance.
- **What to tell the user**: "Create a custom skill or rule in `catalog/sources/local/` with project-specific patterns. Run `/sync-catalog` to include it in the manifest."
- **Provide**: a brief skeleton or example of what the custom entity should contain.

### 3. Add a New Source via `/add-source`

When a community repository covers the missing technology.

- **When**: A known third-party repository of Claude Code entities exists for this technology.
- **What to tell the user**: "A community source may cover this technology. Use `/add-source` to register it, then `/sync-catalog` to import its entities."

### 4. Request Upstream Addition

When no community source exists yet.

- **When**: The technology is popular enough that the primary source (`everything-claude-code`) should support it.
- **What to tell the user**: "Consider opening an issue or PR on the upstream source repository to add support for this technology."

---

## Surfacing Thresholds

Not every gap needs to be surfaced. Apply these rules:

### Always Surface

- Primary languages in the Technology Profile with **Partial** or **None** coverage.
- Primary frameworks in the Technology Profile with **None** coverage.
- Any technology with **High** impact assessment.

### Surface Selectively

- Secondary frameworks with **Partial** coverage — surface only if the gap is non-obvious.
- Build tools and package managers — surface only if the gap affects development workflow.

### Never Surface

- Technologies not in the Technology Profile.
- Infrastructure tools where universal practices are sufficient (e.g., "Docker" gap when standard Docker best practices apply).
- Technologies with **Full** coverage (no gap to report).

---

## Gap Section in Generated CLAUDE.md

In Step 6, include a `## Known Gaps` section in the generated CLAUDE.md. Keep it concise:

```markdown
## Known Gaps

Technologies with limited or no dedicated entity coverage from the igniter catalog.

| Technology | Coverage | Recommendation |
|------------|----------|----------------|
| SQLAlchemy | Partial | Covered by python-patterns; add project-specific ORM conventions below |
| Redis | None | Create custom caching skill in catalog/sources/local/skills/ |
```

Follow the gap table with any inline guidance that partially addresses the gaps. For example, if SQLAlchemy has partial coverage, add a brief "SQLAlchemy conventions" subsection under Coding Conventions.

---

## Cross-References

- [`SKILL.md`](../SKILL.md) — main `/ignite` procedure (gap analysis presented in Step 4, embedded in Step 6)
- [`ignite-workflow.md`](ignite-workflow.md) — Step 3 selection algorithm and Step 6 CLAUDE.md generation
- [`specialization-guide.md`](specialization-guide.md) — how to adapt entities that provide partial coverage
