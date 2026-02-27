# Test Archetype: Python Django

Simulated project context for validating `/ignite` entity selection, specialization, and gap analysis.
See [RESULTS.md](RESULTS.md) for the analysis output produced from this archetype.

---

## Tech Stack

| Dimension | Value |
|-----------|-------|
| **Language** | Python 3.12 |
| **Framework** | Django 5.x |
| **Database** | PostgreSQL 16 |
| **Package manager** | Poetry |
| **Test framework** | pytest + pytest-django |
| **Infrastructure** | Docker Compose |
| **CI/CD** | GitHub Actions |
| **Project type** | api-service (Django REST Framework) |

---

## Simulated File Signals

Files that would exist in the target project root, triggering technology detection in Step 1 of `/ignite`:

```
myproject/
├── pyproject.toml          # Python + Poetry → language: python, PM: poetry
├── poetry.lock
├── manage.py               # Django signal
├── Dockerfile
├── docker-compose.yml      # Infrastructure signal
├── .github/
│   └── workflows/
│       └── ci.yml          # CI/CD signal
├── myapp/
│   ├── models.py
│   ├── views.py
│   └── tests/
│       └── test_views.py   # pytest naming convention
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   └── urls.py
└── requirements/
    ├── base.txt
    └── production.txt
```

### `pyproject.toml` (excerpt)
```toml
[tool.poetry]
name = "myproject"
python = "^3.12"

[tool.poetry.dependencies]
django = "^5.0"
djangorestframework = "^3.15"
psycopg2-binary = "^2.9"
celery = "^5.3"

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.test"
```

### `docker-compose.yml` (excerpt)
```yaml
services:
  web:
    build: .
    command: python manage.py runserver
  db:
    image: postgres:16
  redis:
    image: redis:7
```

---

## Architecture Notes

*As provided in conversation history to `/ignite`:*

> Building a REST API backend using Django 5 and Django REST Framework. PostgreSQL for primary storage, Redis for caching and Celery task queue. Containerised with Docker Compose for local development, deployed to AWS ECS via GitHub Actions. Tests use pytest-django. Code formatted with ruff and black.

---

## Expected Technology Profile

```json
{
  "languages": ["python"],
  "frameworks": ["django", "postgres", "docker"],
  "packageManagers": ["poetry"],
  "testFrameworks": ["pytest"],
  "buildTools": [],
  "ciCd": ["github-actions"],
  "docker": true,
  "projectType": "api-service"
}
```

---

## Notes for Reviewers

- **Celery** appears in `pyproject.toml` but has no catalog tag — expected gap.
- **Redis** is used for caching and task queue — no dedicated catalog entity.
- **Poetry** as package manager — no Poetry-specific entity; `python-patterns` covers general Python conventions.
- Hook matchers should be adapted: `**/*.ts` → `**/*.py`, `npx prettier` → `ruff format`.