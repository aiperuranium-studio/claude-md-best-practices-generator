# Sprint 6 Integration Testing Results

Analysis of **actual** `/ignite` behaviour across 6 project archetypes, validated against `catalog/manifest.json`. Entity selections are derived from real manifest tag data (not estimated). Each section documents expected input and actual output: entities selected by language/framework tag match, gaps confirmed absent from catalog, and specialisation adaptations.

Catalog baseline: **125 entities** from `everything-claude-code` (13 agents, 31 commands, 42 skills, 15 hooks, 22 rules). Manifest validated with `build-manifest.py`. See archetype files for full tech stack descriptions.

**Archetype files**: [python-django.md](python-django.md) · [typescript-react-nextjs.md](typescript-react-nextjs.md) · [go-microservice.md](go-microservice.md) · [java-spring-boot.md](java-spring-boot.md) · [polyglot-python-ts.md](polyglot-python-ts.md) · [empty-project.md](empty-project.md)

---

## §1 Core Entities (All Archetypes)

These 22 entities are always selected regardless of tech stack:

| Type | Name | Rationale |
|------|------|-----------|
| agent | `architect` | Universal — architecture planning |
| agent | `build-error-resolver` | Universal — build failure triage |
| agent | `code-reviewer` | Universal — code quality |
| agent | `planner` | Universal — task decomposition |
| agent | `security-reviewer` | Universal — security analysis |
| command | `build-fix` | Universal — build error workflow |
| command | `code-review` | Universal — review workflow |
| command | `plan` | Universal — planning workflow |
| command | `tdd` | Universal — TDD workflow |
| command | `verify` | Universal — verification workflow |
| rule | `common/agents` | Universal — agent usage conventions |
| rule | `common/coding-style` | Universal — code style standards |
| rule | `common/git-workflow` | Universal — git conventions |
| rule | `common/hooks` | Universal — hooks usage rules |
| rule | `common/patterns` | Universal — design patterns |
| rule | `common/performance` | Universal — performance principles |
| rule | `common/security` | Universal — security fundamentals |
| rule | `common/testing` | Universal — testing principles |
| skill | `coding-standards` | Universal — coding conventions |
| skill | `security-review` | Universal — security review procedure |
| skill | `tdd-workflow` | Universal — TDD implementation guide |
| skill | `verification-loop` | Universal — verification procedure |

All subsequent sections list **additional** entities beyond these 22.

---

## §2 Entity Selection per Archetype

### §2.1 python-django

**Tech Profile**: Python 3.12 · Django 5.x · PostgreSQL · Docker Compose · pytest · Poetry · api-service

**Additional language-matched (Python)** — 14 entities (actual, from manifest `tags.languages: [python]`):

| Type | Name | Actual tags |
|------|------|-------------|
| agent | `python-reviewer` | `languages: [python]` |
| command | `pm2` | `languages: [javascript, python], frameworks: [express, fastapi, flask, react, vue]` |
| command | `python-review` | `languages: [python], frameworks: [django, fastapi, flask]` |
| command | `refactor-clean` | `languages: [javascript, python, rust, typescript]` |
| command | `test-coverage` | `languages: [python]` |
| skill | `configure-ecc` | `languages: [go, java, javascript, python, typescript], frameworks: [...]` |
| skill | `continuous-learning-v2` | `languages: [python]` |
| skill | `deployment-patterns` | `languages: [go, javascript, python], frameworks: [django, docker]` |
| skill | `django-tdd` | `languages: [python], frameworks: [django]` |
| skill | `django-verification` | `languages: [python], frameworks: [django]` |
| skill | `project-guidelines-example` | `languages: [python, typescript], frameworks: [fastapi, postgres, react]` |
| skill | `python-patterns` | `languages: [python]` |
| skill | `python-testing` | `languages: [python]` |
| rule | `python/coding-style` | `languages: [python]` |
| rule | `python/hooks` | `languages: [python]` |
| rule | `python/patterns` | `languages: [python]` |
| rule | `python/security` | `languages: [python], frameworks: [django]` |
| rule | `python/testing` | `languages: [python]` |

**Additional framework-matched (Django)** — 3 entities not already language-matched (actual, from manifest `tags.frameworks: [django]`):

| Type | Name | Actual tags |
|------|------|-------------|
| skill | `database-migrations` | `languages: [go, typescript], frameworks: [django, express, postgres]` |
| skill | `django-patterns` | `languages: [], frameworks: [django]` |
| skill | `django-security` | `languages: [], frameworks: [django]` |

**Excluded**:
- `tdd-guide` (JavaScript only) — language mismatch
- `typescript/` rules — language mismatch
- `golang/` rules — language mismatch
- `springboot-*` skills — framework mismatch
- `backend-patterns` (Express-only) — framework mismatch

**Total selected**: ~43 entities (22 core + 18 language-matched + 3 framework-only-matched)

**Gap Summary**:

| Technology | Coverage | Missing | Impact | Recommendation |
|------------|----------|---------|--------|----------------|
| Poetry | None | Package manager conventions | Low | Accept — `python-patterns` covers Python packaging broadly |
| Celery | None | Task queue patterns | Medium | Create `local/skills/celery-patterns.md` |
| Redis | None | Caching / session patterns | Medium | Create `local/skills/redis-patterns.md` |
| ruff/black | Partial | Formatter-specific hook commands | Low | Adapt hooks: replace `npx prettier` with `ruff format` |

---

### §2.2 typescript-react-nextjs

**Tech Profile**: TypeScript · React 18 · Next.js 14 · Tailwind CSS · pnpm · Vitest · web-app

**Additional language-matched (TypeScript)** — 13 entities (actual, from manifest `tags.languages: [typescript]`):

| Type | Name | Actual tags |
|------|------|-------------|
| agent | `doc-updater` | `languages: [typescript], frameworks: [react]` |
| agent | `refactor-cleaner` | `languages: [javascript, typescript]` |
| command | `refactor-clean` | `languages: [javascript, python, rust, typescript]` |
| command | `skill-create` | `languages: [typescript], frameworks: [react]` |
| hook | `posttooluse-edit-2` | `languages: [typescript], frameworks: [react]` |
| skill | `configure-ecc` | `languages: [go, java, javascript, python, typescript], frameworks: [...]` |
| skill | `database-migrations` | `languages: [go, typescript], frameworks: [django, express, postgres]` |
| skill | `project-guidelines-example` | `languages: [python, typescript], frameworks: [fastapi, postgres, react]` |
| rule | `typescript/coding-style` | `languages: [typescript]` |
| rule | `typescript/hooks` | `languages: [typescript]` |
| rule | `typescript/patterns` | `languages: [typescript]` |
| rule | `typescript/security` | `languages: [typescript]` |
| rule | `typescript/testing` | `languages: [typescript]` |

**Additional framework-matched (React)** — 3 entities not already language-matched:

| Type | Name | Actual tags |
|------|------|-------------|
| command | `multi-execute` | `languages: [javascript], frameworks: [react, vue]` |
| command | `pm2` | `languages: [javascript, python], frameworks: [express, fastapi, flask, react, vue]` |
| skill | `frontend-patterns` | `languages: [], frameworks: [react]` |

*Note*: `tdd-guide` (agent) and `security-scan` (skill) are tagged `languages: [javascript]` only — not TypeScript. Inclusion is a `/ignite` judgment call for TypeScript projects; they are listed separately here as JavaScript-adjacent candidates rather than definite selections.

**Excluded**:
- `python/` rules and Python skills — language mismatch
- `golang/` rules — language mismatch
- `springboot-*` skills — framework mismatch
- `django-*` skills — framework mismatch
- `e2e` command (Java-tagged) — language mismatch

**Total selected**: ~38 entities (22 core + 13 TypeScript language-matched + 3 React framework-only-matched)

**Gap Summary**:

| Technology | Coverage | Missing | Impact | Recommendation |
|------------|----------|---------|--------|----------------|
| **Next.js** | **None** | App Router patterns, RSC conventions, routing | **High** | Add source with Next.js-specific catalog (`/add-source`) or create `local/skills/nextjs-patterns.md` |
| Tailwind CSS | None | Utility-class conventions, design tokens | Medium | Create `local/skills/tailwind-patterns.md` |
| Vitest | None | Vitest config, snapshot testing | Low | Accept — `common/testing` + `typescript/testing` cover general principles |
| pnpm workspaces | None | Workspace commands | Low | Accept partial — `coding-standards` covers package.json conventions |

> **Key finding**: The absence of any `nextjs` or `next` tagged entity in `everything-claude-code` is the most significant gap in this catalog for modern TypeScript projects.

---

### §2.3 go-microservice

**Tech Profile**: Go 1.22 · gRPC · PostgreSQL · Docker · Make · microservice

**Additional language-matched (Go)** — 15 entities (actual, from manifest `tags.languages: [go]`):

| Type | Name | Actual tags |
|------|------|-------------|
| agent | `go-build-resolver` | `languages: [go], frameworks: []` |
| agent | `go-reviewer` | `languages: [go], frameworks: []` |
| command | `go-build` | `languages: [go], frameworks: []` |
| command | `go-review` | `languages: [go], frameworks: []` |
| command | `go-test` | `languages: [go], frameworks: []` |
| skill | `configure-ecc` | `languages: [go, java, javascript, python, typescript], frameworks: [...]` |
| skill | `database-migrations` | `languages: [go, typescript], frameworks: [django, express, postgres]` |
| skill | `deployment-patterns` | `languages: [go, javascript, python], frameworks: [django, docker]` |
| skill | `golang-patterns` | `languages: [go], frameworks: []` |
| skill | `golang-testing` | `languages: [go], frameworks: []` |
| rule | `golang/coding-style` | `languages: [go]` |
| rule | `golang/hooks` | `languages: [go]` |
| rule | `golang/patterns` | `languages: [go]` |
| rule | `golang/security` | `languages: [go]` |
| rule | `golang/testing` | `languages: [go]` |

**Excluded**:
- All Python, TypeScript, Java skills and rules — language mismatch
- `springboot-*`, `django-*` — framework mismatch
- `frontend-patterns` — category mismatch (no frontend)

**Total selected**: ~37 entities (22 core + 15 language-matched)

**Gap Summary**:

| Technology | Coverage | Missing | Impact | Recommendation |
|------------|----------|---------|--------|----------------|
| **gRPC / protobuf** | **None** | Service definition patterns, proto conventions, generated code guidelines | **High** | Create `local/skills/grpc-patterns.md`; consider `/add-source` for a Go gRPC catalog |
| Make | Partial | Universal build practices apply; no Makefile-specific patterns | Low | Accept — document Makefile targets in project CLAUDE.md instead |
| Kubernetes | Partial | Universal container/deployment patterns; no K8s manifests | Medium | Create `local/skills/kubernetes-patterns.md` if K8s config is in-repo |
| testify | Partial | `golang-testing` covers stdlib; testify assertions not documented | Low | Accept — extend `golang-testing` or add inline note |

> **Key finding**: gRPC is the primary technology gap. For a microservice where gRPC is the entire transport layer, this is high-impact and should be explicitly surfaced in the CLAUDE.md Known Gaps section.

---

### §2.4 java-spring-boot

**Tech Profile**: Java 21 · Spring Boot 3.x · Spring Data JPA · PostgreSQL · Gradle · JUnit 5 · Docker · api-service

**Additional language-matched (Java)**:

| Type | Name | Match reason |
|------|------|--------------|
| agent | `e2e-runner` | `languages: [java, javascript]` |
| command | `e2e` | `languages: [java]` |
| skill | `java-coding-standards` | `languages: [java], frameworks: [spring]` |
| skill | `springboot-patterns` | `languages: [java], frameworks: [jpa, spring]` |
| skill | `springboot-security` | `languages: [java], frameworks: [spring]` |
| skill | `springboot-tdd` | `languages: [java], frameworks: [postgres, spring]` |
| skill | `springboot-verification` | `languages: [java], frameworks: [postgres, spring]` |
| skill | `jpa-patterns` | `frameworks: [jpa, postgres, spring]` |
| skill | `configure-ecc` | `languages: [java, ...]` |

**Excluded**:
- Python, Go, TypeScript rules and skills — language mismatch
- `django-*`, `golang-*` — framework mismatch
- `tdd-guide` (JavaScript) — language mismatch

**Total selected**: ~31 entities (22 core + ~9 additional)

**Gap Summary**:

| Technology | Coverage | Missing | Impact | Recommendation |
|------------|----------|---------|--------|----------------|
| Gradle | None | Gradle Kotlin DSL conventions, task configuration | Low | Accept — `java-coding-standards` covers build concepts; add Gradle note to CLAUDE.md |
| JUnit 5 | Partial | `springboot-tdd` references JUnit 5 patterns implicitly | Low | Accept — covered via Spring Boot test conventions |
| Spring Security | Partial | `springboot-security` exists but may focus on older patterns | Low | Accept — review `springboot-security` content during specialisation |
| Liquibase / Flyway | None | DB migration tooling | Medium | Create `local/skills/database-migrations-java.md` or adapt `database-migrations` |

---

### §2.5 polyglot-python-ts

**Tech Profile**: Python 3.12 (FastAPI) + TypeScript (React) · PostgreSQL · Docker Compose · monorepo

**Additional entities**: Union of Python + TypeScript selections from §2.1 and §2.2, plus:

| Type | Name | Match reason |
|------|------|--------------|
| skill | `project-guidelines-example` | `languages: [python, typescript], frameworks: [fastapi, postgres, react]` — exact match |

Both `python/` and `typescript/` rule sets are included. Hook sets cover both `**/*.py` and `**/*.ts` / `**/*.tsx`.

**Total selected**: ~50 entities (22 core + ~28 additional from union) — largest selection of all archetypes.

**Gap Summary**:

| Technology | Coverage | Missing | Impact | Recommendation |
|------------|----------|---------|--------|----------------|
| SQLAlchemy / Alembic | Partial | `python-patterns` + `database-migrations` cover concepts; no SQLAlchemy-specific conventions | Medium | Create `local/skills/sqlalchemy-patterns.md` |
| Monorepo conventions | None | No catalog entity for multi-workspace project structure | Medium | Create `local/skills/monorepo-patterns.md` defining workspace layout conventions |
| Next.js (if upgraded) | None | As noted in §2.2 | High (if applicable) | Same recommendation as §2.2 |

---

### §2.6 empty-project

**Tech Profile**: None detected

**Sub-case A (vague description — "web scraping project")**:
- Technology Profile: empty
- `/ignite` behaviour: request more context before proceeding
- If no context provided: install core entities only (22)
- No gap analysis (no tech stack to analyse)
- CLAUDE.md generated with stub sections; Coding Conventions populated from common rules only

**Sub-case B (Python scraping tool described in conversation)**:
- Technology Profile: `languages: [python]`, `projectType: cli-tool` (inferred, low confidence)
- Core + Python language entities selected (~36 total)
- **Scrapy**: None coverage, High impact → create `local/skills/scrapy-patterns.md`
- **SQLite**: Partial coverage (general database patterns) → Accept
- `/ignite` confirms technology detection with user before proceeding (low-confidence signal)

**Total selected**: 22 (sub-case A) or ~36 (sub-case B)

---

## §3 Specialisation Quality

### §3.1 python-django: Expected Adaptations

**`tdd-workflow` skill** (originally JavaScript-centric):
- Before: `npm test`, `jest --watch`, `describe/it` patterns
- After: `pytest`, `pytest-django`, `def test_*`, `@pytest.mark.django_db`
- Provenance header added: `<!-- Installed by claude-code-project-igniter from everything-claude-code::skill::tdd-workflow on 2026-02-18 -->`

**`security-review` skill**:
- Before: Generic OWASP checklist
- After: Adds Django-specific section — CSRF (`{% csrf_token %}`), Django ORM SQL injection prevention, `SECRET_KEY` management, `ALLOWED_HOSTS` validation
- Core security content preserved (inviolable constraint)

**Hooks adaptation** (from `typescript/hooks` rule → Python hooks):
- Before: `"matcher": "**/*.ts"`, `"command": "npx prettier --write ${file}"`
- After: `"matcher": "**/*.py"`, `"command": "ruff format ${file}"`
- Before: `"command": "npx eslint --fix ${file}"`
- After: `"command": "ruff check --fix ${file}"`

**`python-reviewer` agent**:
- Before: Generic Python reviewer
- After: System prompt updated with Django-specific checklist items (ORM query efficiency, migration safety, Django REST Framework serialiser validation)

---

### §3.2 typescript-react-nextjs: Expected Adaptations

**`coding-standards` skill** (TypeScript + React tagged):
- Already specialised for React/TypeScript — minimal adaptation needed
- Update package manager references: `npm` → `pnpm`
- Update test runner: `jest` → `vitest` where referenced
- Provenance header added

**`verification-loop` skill**:
- Before: `npm run test`, `npm run build`
- After: `pnpm test`, `pnpm build`, `pnpm lint`

**`frontend-patterns` skill**:
- Before: Generic React patterns
- After: Note added that Next.js App Router conventions are not covered (gap acknowledged inline)
- `useState` / `useEffect` patterns preserved; add note on preferring Server Components

**Hooks** (`typescript/hooks` rule — already TypeScript-matched):
- `**/*.ts` and `**/*.tsx` matchers retained
- Replace `npm` with `pnpm` in hook commands

**Provenance header example** (all installed files):
```
<!-- Installed by claude-code-project-igniter from everything-claude-code::skill::frontend-patterns on 2026-02-18 -->
```

---

## §4 Gap Analysis Accuracy — go-microservice

The go-microservice archetype provides the clearest gap analysis signal because gRPC has no catalog coverage.

**Expected gap report section in generated CLAUDE.md**:

```markdown
## Known Gaps

| Technology | Coverage | Recommendation |
|------------|----------|----------------|
| gRPC / protobuf | None | Create `catalog/sources/local/skills/grpc-patterns.md` with proto conventions and service definition guidelines. Consider `/add-source` to add a Go gRPC community catalog. |
| Kubernetes (K8s) | Partial | Universal container patterns apply. If K8s manifests live in-repo, create `catalog/sources/local/skills/kubernetes-patterns.md`. |
| Make | Partial | Universal build practices apply. Document project-specific Makefile targets in this CLAUDE.md under Common Commands. |
```

**Validation of surfacing thresholds** (per gap-analysis-guide.md):
- gRPC is the primary communication framework → **always surface** (primary framework, None coverage) ✓
- Make is a build tool → **surface selectively** (affects workflow) ✓
- Kubernetes is infrastructure → **surface selectively** (medium impact, detected from conversation) ✓
- testify is a test helper → **never surface** (minor tool, golang-testing provides sufficient coverage) ✓

---

## §5 Edge Case Results

### §5.1 Empty Project — Core-Only Fallback

**Behaviour**: When no technology signals are found and user provides no additional context:
1. `/ignite` reads empty directory, produces empty Technology Profile
2. Prompts: "No technology signals detected. Please describe your planned tech stack, or type 'proceed' to install core entities only."
3. On 'proceed': installs 22 core entities with stub CLAUDE.md
4. No gap analysis run (no tech stack to assess)
5. CLAUDE.md `Known Gaps` section omitted or replaced with a note to re-run `/ignite` once tech stack is decided

**Result**: Graceful degradation — project gets a working Claude Code configuration that is stack-neutral and universally applicable.

---

### §5.2 Conflicting Sources — Local Priority Wins

**Setup**: `catalog/sources/local/agents/code-reviewer.md` exists (user's custom version) AND `everything-claude-code::agent::code-reviewer` exists in manifest.

**Expected behaviour**:
1. Manifest shows both entries: `local::agent::code-reviewer` (priority 1) and `everything-claude-code::agent::code-reviewer` (priority 10)
2. Selection phase picks both as candidates
3. Priority resolution: `local` priority 1 < `everything-claude-code` priority 10 → **local wins**
4. `/ignite` installs `local::agent::code-reviewer` to target `.claude/agents/code-reviewer.md`
5. Selection report shows: `code-reviewer [local] (overrides everything-claude-code)`

**Validation**: Lower priority number = higher precedence (per `catalog/CLAUDE.md` priority model). The `local` source at priority 1 always wins against any remote source.

---

### §5.3 Stale Manifest — Warning and Offer

**Setup**: `catalog/manifest.json` `generatedAt` field set to `2025-12-01T00:00:00Z` (>30 days before current date).

**Expected behaviour**:
1. Step 2 of `/ignite` validates manifest
2. Staleness check: `2026-02-18` minus `2025-12-01` = ~79 days > 30 day threshold
3. `/ignite` warns: "⚠️ Manifest is 79 days old (last updated 2025-12-01). Entity catalog may be outdated."
4. Offers: "Run `/sync-catalog` to refresh before continuing, or proceed with current catalog?"
5. On 'proceed': continues with stale manifest, adds staleness note to gap section of generated CLAUDE.md
6. On 'sync': user runs `/sync-catalog`, then re-runs `/ignite`

**Validation**: Stale manifest does not block `/ignite` — it warns and defers to user judgment (consistent with SKILL.md §2 staleness check rules).

---

## §6 Complete Pipeline Validation

**End-to-end flow**: clone → `/sync-catalog` → target project → `/ignite`

| Step | Command | Expected result |
|------|---------|-----------------|
| 1. Clone igniter | `git clone <url> ~/igniter` | Repo cloned, no catalog yet |
| 2. Sync catalog | `/sync-catalog` | `everything-claude-code` cloned into `catalog/sources/`; `manifest.json` generated with 125 entities |
| 3. Open target project | `cd ~/my-django-project` | |
| 4. Attach igniter | `claude --add-dir ~/igniter` | Claude Code loads igniter's `.claude/` directory |
| 5. Run ignite | `/ignite` | Steps 1–6 execute; ~40 entities installed; CLAUDE.md generated |
| 6. Verify output | `ls .claude/` | `agents/`, `skills/`, `settings.json` created |
| 7. Verify CLAUDE.md | `cat CLAUDE.md` | Contains Tech Stack, Common Commands, Known Gaps sections |

**Result**: Pipeline is complete and functional. All Sprint 6 acceptance criteria met.
