# Test Archetype: Empty Project (Conversation-Only)

Simulated project context for validating `/ignite` edge-case behaviour when no file signals are present.
See [RESULTS.md](RESULTS.md) for the analysis output produced from this archetype.

---

## Tech Stack

| Dimension | Value |
|-----------|-------|
| **Language** | Unknown (not yet chosen) |
| **Framework** | Unknown |
| **Infrastructure** | Unknown |
| **Project type** | Unknown |

---

## Simulated File Signals

**None.** The target project directory contains only:

```
new-project/
└── (empty)
```

No `package.json`, no `pyproject.toml`, no `go.mod`, no `Dockerfile`, no `.github/` — nothing that would trigger automatic technology detection.

---

## Architecture Notes

*Two sub-cases tested:*

### Sub-case A: Vague conversation description

> "I want to start a new web scraping project."

No language, framework, or technology specified. `/ignite` has no basis for technology matching beyond the phrase "web scraping".

### Sub-case B: Detailed conversation description

> "I'm planning to build a Python web scraper using Scrapy and store results in SQLite. No web frontend needed — just a CLI tool."

Language (Python) and partial framework (Scrapy, SQLite) are stated but not confirmed by any file. Scrapy and SQLite have no catalog entities.

---

## Expected Technology Profile

### Sub-case A
```json
{
  "languages": [],
  "frameworks": [],
  "packageManagers": [],
  "testFrameworks": [],
  "buildTools": [],
  "ciCd": [],
  "docker": false,
  "projectType": "unknown"
}
```

### Sub-case B
```json
{
  "languages": ["python"],
  "frameworks": [],
  "packageManagers": [],
  "testFrameworks": [],
  "buildTools": [],
  "ciCd": [],
  "docker": false,
  "projectType": "cli-tool"
}
```

---

## Expected `/ignite` Behaviour

### Sub-case A
1. Step 1 produces empty/low-confidence Technology Profile.
2. `/ignite` **asks for more context** before proceeding: "No technology signals found. Could you describe your planned tech stack?"
3. If user provides no additional context, fall back to **core entities only** (22 entities).
4. CLAUDE.md generated with generic structure; Known Gaps section omitted (no tech stack to analyse).

### Sub-case B
1. Step 1 detects Python from conversation (low-confidence signal — no file confirmation).
2. Technology Profile marked as `"confidence": "inferred"` for python.
3. Core + Python language entities selected.
4. **Scrapy and SQLite** surfaced as None-coverage gaps (mentioned in conversation but no catalog entities).
5. Recommendation: run `/sync-catalog` to check for updated catalog, or add custom local entities.

---

## Notes for Reviewers

- This archetype validates the **conversation-only signal path** in ignite-workflow.md Step 1.
- Core entities (22) are the safety net — always included regardless of tech stack confidence.
- The empty project case should never produce an error — graceful degradation to core-only is the correct behaviour.
- Sub-case B tests **low-confidence inference** from conversation vs. high-confidence file-based detection.
