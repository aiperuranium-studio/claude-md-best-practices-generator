# Test Archetype: Polyglot Python + TypeScript Monorepo

Simulated project context for validating `/ignite` entity selection, specialization, and gap analysis.
See [RESULTS.md](RESULTS.md) for the analysis output produced from this archetype.

---

## Tech Stack

| Dimension | Value |
|-----------|-------|
| **Languages** | Python 3.12 (backend) + TypeScript 5.x (frontend) |
| **Backend framework** | FastAPI |
| **Frontend framework** | React 18 |
| **Database** | PostgreSQL 16 |
| **Package managers** | Poetry (backend) + pnpm (frontend) |
| **Test frameworks** | pytest (backend) + Vitest (frontend) |
| **Infrastructure** | Docker Compose |
| **CI/CD** | GitHub Actions |
| **Project type** | monorepo |

---

## Simulated File Signals

Files that would exist in the target project root, triggering technology detection in Step 1 of `/ignite`:

```
fullstack-app/
├── docker-compose.yml          # Infrastructure signal
├── .github/
│   └── workflows/
│       └── ci.yml              # CI/CD signal
├── backend/
│   ├── pyproject.toml          # Python + Poetry + FastAPI signal
│   ├── poetry.lock
│   ├── Dockerfile
│   └── app/
│       ├── main.py             # FastAPI signal
│       ├── routers/
│       ├── models/
│       └── tests/
│           └── test_api.py
└── frontend/
    ├── package.json            # TypeScript + React + Vitest signal
    ├── pnpm-lock.yaml          # PM: pnpm
    ├── tsconfig.json           # TypeScript signal
    ├── vitest.config.ts
    └── src/
        ├── App.tsx
        └── components/
```

### `backend/pyproject.toml` (excerpt)
```toml
[tool.poetry.dependencies]
python = "^3.12"
fastapi = "^0.111.0"
uvicorn = "^0.30.0"
sqlalchemy = "^2.0.0"
alembic = "^1.13.0"
asyncpg = "^0.29.0"
```

### `frontend/package.json` (excerpt)
```json
{
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0"
  },
  "devDependencies": {
    "typescript": "^5.4.0",
    "vitest": "^1.6.0",
    "@testing-library/react": "^16.0.0"
  }
}
```

---

## Architecture Notes

*As provided in conversation history to `/ignite`:*

> Monorepo with a Python FastAPI backend and a React TypeScript frontend. PostgreSQL via SQLAlchemy async + Alembic migrations. React frontend with Vitest. Both services containerised via Docker Compose. Separate Poetry and pnpm lockfiles per workspace.

---

## Expected Technology Profile

```json
{
  "languages": ["python", "typescript"],
  "frameworks": ["fastapi", "react", "postgres", "docker"],
  "packageManagers": ["poetry", "pnpm"],
  "testFrameworks": ["pytest", "vitest"],
  "buildTools": [],
  "ciCd": ["github-actions"],
  "docker": true,
  "projectType": "monorepo"
}
```

---

## Notes for Reviewers

- **Dual language** — `/ignite` must union Python and TypeScript entity sets. Rules from both `python/` and `typescript/` should be included.
- **`project-guidelines-example`** skill (tagged python+typescript, fastapi+postgres+react) is an exact match and should be selected.
- **SQLAlchemy / Alembic**: No dedicated catalog entity — covered partially by `python-patterns` and `database-migrations` (go/ts tagged, but general migration patterns apply).
- **Monorepo structure**: No monorepo-specific catalog entity — medium-impact gap. Recommendation: create custom `local/` skill defining workspace conventions.
- **Hook matchers**: Two separate hook sets may be needed — Python hooks (`**/*.py`) and TypeScript hooks (`**/*.ts`, `**/*.tsx`).
- **Django rules excluded**: `python/security` has a `django` sub-tag; non-Django parts still apply and should be included.
