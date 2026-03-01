# Implementation Plan: Refactor Plugin Manifests and Document Real Repo URL

**Date:** 2026-03-01 **Status:** Draft — awaiting user confirmation

---

## Overview

Align `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` with the schema and conventions used by the reference plugin (`everything-claude-code`). Replace all placeholder URLs in `README.md` with the real Git repository URL. Real repo URL: `https://github.com/simonescannapieco/claude-md-best-practices-generator`.

---

## Current State vs Reference

### plugin.json

| Field | Current | Target |
|-------|---------|--------|
| `skills` | String `"./.claude/skills/"` | **Array** `["./.claude/skills/"]` — PLUGIN_SCHEMA_NOTES.md explicitly forbids strings |
| `homepage` | MISSING | **Add** `"https://github.com/simonescannapieco/claude-md-best-practices-generator"` |

> Note: The reference (`everything-claude-code`) plugin.json omits the `skills` field entirely (auto-discovered). However, since our skills live at `./.claude/skills/` (non-standard location relative to plugin root), we declare it explicitly to avoid ambiguity — but as an array.

### marketplace.json

| Field | Current | Target |
|-------|---------|--------|
| `$schema` | MISSING | **Add** `"https://anthropic.com/claude-code/marketplace.schema.json"` |
| `owner` | MISSING | **Add** `{ "name": "simonescannapieco", "email": "<TBD>" }` |
| `metadata` | MISSING | **Add** `{ "description": "..." }` |
| Plugin `source` | `"."` | **Change** to `"./"` (matches reference) |
| Plugin `author` | MISSING | **Add** |
| Plugin `homepage` | MISSING | **Add** real repo URL |
| Plugin `repository` | MISSING | **Add** real repo URL |
| Plugin `license` | MISSING | **Add** `"MIT"` |
| Plugin `keywords` | MISSING | **Add** |
| Plugin `category` | MISSING | **Add** `"documentation"` |
| Plugin `tags` | MISSING | **Add** |
| Plugin `strict` | MISSING | **Add** `false` |

### README.md

| Location | Current | Target |
|----------|---------|--------|
| Option A clone URL | `https://github.com/your-org/claude-code-best-practices` | `https://github.com/simonescannapieco/claude-md-best-practices-generator` |
| Quick Start clone URL | Same placeholder | Same fix |

### CLAUDE.md

Already documents both installation modes. No changes needed.

---

## Open Question (User Input Required)

**Email for `owner` and `author` fields in marketplace.json:** The reference plugin uses `me@affaanmustafa.com`. The marketplace schema requires an email. Should we use:
1. A real email address (specify which)
2. A GitHub noreply address: `simonescannapieco@users.noreply.github.com`
3. Omit the email field (risk: marketplace validation may reject)

---

## Implementation Phases

### Phase 1: Fix `plugin.json`

**File:** `.claude-plugin/plugin.json`

Change `skills` from string to array; add `homepage`.

**Target content:**
```json
{
  "name": "claude-md-best-practices",
  "version": "3.0.0",
  "description": "Enriches CLAUDE.md generation guidelines from curated web sources and /insights behavioral data. Provides /claude-md-best-practices:refresh-guidelines.",
  "author": {
    "name": "simonescannapieco",
    "url": "https://github.com/simonescannapieco/claude-md-best-practices-generator"
  },
  "homepage": "https://github.com/simonescannapieco/claude-md-best-practices-generator",
  "repository": "https://github.com/simonescannapieco/claude-md-best-practices-generator",
  "license": "MIT",
  "keywords": ["claude-md", "best-practices", "guidelines", "anthropic"],
  "skills": ["./.claude/skills/"]
}
```

### Phase 2: Enrich `marketplace.json`

**File:** `.claude-plugin/marketplace.json`

Add `$schema`, `owner`, `metadata`; enrich plugin entry.

**Target content** (substitute `<email>` with answer to open question):
```json
{
  "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
  "name": "claude-md-best-practices",
  "description": "CLAUDE.md best practices generator plugin",
  "owner": {
    "name": "simonescannapieco",
    "email": "<email>"
  },
  "metadata": {
    "description": "Enriches CLAUDE.md generation guidelines from curated web sources and /insights behavioral data"
  },
  "plugins": [
    {
      "name": "claude-md-best-practices",
      "source": "./",
      "description": "Enriches CLAUDE.md guidelines from web sources and /insights data. Provides /claude-md-best-practices:refresh-guidelines.",
      "version": "3.0.0",
      "author": {
        "name": "simonescannapieco",
        "email": "<email>"
      },
      "homepage": "https://github.com/simonescannapieco/claude-md-best-practices-generator",
      "repository": "https://github.com/simonescannapieco/claude-md-best-practices-generator",
      "license": "MIT",
      "keywords": ["claude-md", "best-practices", "guidelines", "anthropic"],
      "category": "documentation",
      "tags": ["claude-md", "best-practices", "guidelines", "documentation", "anthropic"],
      "strict": false
    }
  ]
}
```

### Phase 3: Fix `README.md` placeholder URLs

**File:** `README.md`

Replace two occurrences of `https://github.com/your-org/claude-code-best-practices` with `https://github.com/simonescannapieco/claude-md-best-practices-generator`.

---

## Files Changed Summary

| File | Change |
|------|--------|
| `.claude-plugin/plugin.json` | `skills` string → array; add `homepage` |
| `.claude-plugin/marketplace.json` | Add `$schema`, `owner`, `metadata`; enrich plugin entry |
| `README.md` | Replace 2 placeholder clone URLs |

## Files NOT Changed

| File | Reason |
|------|--------|
| `CLAUDE.md` | Already correct |
| `docs/plugin-plan.md` | Historical; leave as reference |

---

## Risks

| Risk | Level | Mitigation |
|------|-------|------------|
| `skills` array change breaks loading | LOW | PLUGIN_SCHEMA_NOTES.md explicitly requires arrays — the fix is correct |
| Missing email rejected by marketplace | MEDIUM | Use GitHub noreply address if no real email |
| `source: "./"` vs `"."` difference | LOW | Reference uses `"./"` — matching it is safe |

---

**WAITING FOR CONFIRMATION:** Proceed with this plan? Reply "yes" to start, or provide the email address for marketplace.json (or "skip email" to use `simonescannapieco@users.noreply.github.com`).
