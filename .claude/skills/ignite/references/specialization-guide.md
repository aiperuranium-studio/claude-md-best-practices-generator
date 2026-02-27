# Specialization Guide

How to adapt catalog entities for a target project's specific technology stack. Read alongside [`ignite-workflow.md`](ignite-workflow.md) (Step 5: Installation) and [`SKILL.md`](../SKILL.md).

---

## Inviolable Constraints

These four rules apply to **all** specialization, regardless of entity type. Never violate them.

1. **Preserve core purpose** — Every entity has a primary function (code review, TDD workflow, security scanning, etc.). Specialization adapts the entity to a project's tech stack but never changes what the entity fundamentally does. A code reviewer must still review code. A security scanner must still scan for vulnerabilities.

2. **Never remove security content** — Security-related instructions, checks, and rules must be preserved in full. You may add project-specific security context (e.g., "also check for Django CSRF tokens") but never remove existing security guidance. When in doubt, keep it.

3. **Additive over subtractive** — Specialization should primarily add project-specific context rather than strip generic content. If an agent's prompt mentions "check for SQL injection," don't remove it just because the project uses an ORM — the principle still applies. Add the ORM-specific guidance alongside it.

4. **Mark provenance** — Every installed/adapted entity must include a provenance header as the first line:
   ```
   <!-- Installed by claude-code-project-igniter from {source}::{type}::{name} on {YYYY-MM-DD} -->
   ```
   This makes installed entities auditable, updatable, and distinguishable from user-created files.

---

## Entity Type: Agents

Agent files are Markdown with YAML frontmatter containing `name`, `description`, `tools`, and `model`. The Markdown body is the system prompt.

### What to Adapt

- **Description** — Update to reference the project's actual technologies. Example: "Expert code reviewer" → "Expert code reviewer for Python/FastAPI projects with SQLAlchemy ORM."
- **System prompt examples** — Replace generic examples with project-specific ones. If the agent shows a JavaScript example, swap it for the project's language.
- **Domain vocabulary** — Adjust terminology to match the project's domain. "API endpoint" → "GraphQL resolver" or "gRPC service" as appropriate.
- **Review checklist items** — Add project-specific checklist items relevant to the detected frameworks.

### What to Preserve

- **Tool lists** — Keep the original tools unless you have a specific reason to change them.
- **Model setting** — Preserve the original model selection.
- **Security sections** — Keep all security review items (Constraint 2).
- **Process structure** — Keep the overall review/analysis process intact.

### Example

Original:
```markdown
You are a senior code reviewer ensuring high standards of code quality.
When reviewing, check for common issues like SQL injection, XSS, and authentication bypasses.
```

Specialized for a Python/FastAPI project:
```markdown
You are a senior code reviewer ensuring high standards of code quality in this Python/FastAPI project.
When reviewing, check for common issues like SQL injection (especially raw SQL in SQLAlchemy), XSS in Jinja2 templates, authentication bypasses in FastAPI dependency injection, and CORS misconfiguration.
```

---

## Entity Type: Skills

Skills contain a `SKILL.md` with procedure steps, prerequisites, and references.

### What to Adapt

- **Code examples** — Swap to the project's framework. Django examples → FastAPI examples. React examples → Vue examples.
- **File paths** — Update paths to match the project's actual structure. `src/components/` → the project's actual component directory.
- **Package manager commands** — `npm run test` → `pytest`, `yarn build` → `make build`, etc.
- **Tool references** — `eslint` → `ruff`, `prettier` → `black`, etc.
- **Irrelevant sections** — If a skill has sections for multiple frameworks, keep only the relevant one and remove the rest.

### What to Preserve

- **Procedure structure** — Keep the overall step sequence.
- **Human approval gates** — If the skill requires user confirmation at certain steps, preserve those gates.
- **Quality standards** — Keep quality thresholds and verification criteria.

---

## Entity Type: Commands → Skills

Commands are simple Markdown files with instructions. They must be converted to proper `SKILL.md` format during installation.

### Conversion Process

1. **Extract the title** — the command name becomes the skill name. `# /plan` stays as `# /plan`.
2. **Extract the summary** — first paragraph becomes the skill description.
3. **Structure as procedure** — convert the command's instructions into numbered steps under `## Procedure`.
4. **Add prerequisites** — infer from the command's requirements.
5. **Add constraints** — extract any rules or limitations mentioned.

### What to Adapt

- **Build/test commands** — update to the project's actual tools:
  - `npm run build` → `make build` or `go build ./...`
  - `npm test` → `pytest` or `go test ./...`
  - `npx prettier --check .` → `ruff check .`
- **File references** — update to the project's actual structure.
- **Package manager** — use the detected package manager consistently.

### What to Preserve

- **Core workflow** — the fundamental process the command implements (plan → execute → verify).
- **Quality gates** — verification steps and approval requirements.

---

## Entity Type: Rules

Rules are Markdown files containing coding guidelines, typically organized by language or topic (e.g., `common/code-quality.md`, `python/type-hints.md`).

### Installation Strategy

Rules cannot be installed as project-level files — they live at `~/.claude/rules/` which is user-level. For project-level use:

**Option A — Embed in CLAUDE.md** (preferred for concise rules):
- Extract the key guidelines from the rule file.
- Embed them in the appropriate CLAUDE.md section:
  - Language-specific rules → `## Coding Conventions`
  - Workflow rules → `## Workflow Preferences`
  - Quality rules → `## Coding Conventions`
- Keep the embedded version concise. Reference the full rule via `@` import if needed.

**Option B — Agent prompt injection** (for rules that affect specific agents):
- Inject rule content into the relevant agent's system prompt.
- Example: security rules → inject into the security reviewer agent.

### What to Adapt

- **Language filter** — only embed rules for languages in the Technology Profile. Skip `typescript/` rules for a Python project.
- **Framework specificity** — adapt generic examples to the project's framework.
- **Tool references** — update linter/formatter references to the project's actual tools.

### What to Preserve

- **Security rules** — always include, regardless of language (Constraint 2).
- **Common rules** — `common/` rules are universal and always included.
- **Core principles** — the underlying principles of each rule.

---

## Entity Type: Hooks

Hooks are JSON entries in `.claude/settings.json` with event types, file matchers, and command configurations.

### What to Adapt

- **File matchers** — update glob patterns to match the project's file types:
  - `**/*.ts` → `**/*.py` for a Python project
  - `**/*.{js,jsx,ts,tsx}` → `**/*.{py,pyi}` for Python
  - Adjust path prefixes to match the project's directory structure

- **Tool paths** — update to the project's actual tools:
  - `npx prettier --write` → `ruff format`
  - `npx eslint --fix` → `ruff check --fix`
  - `npm run lint` → `make lint` or `ruff check .`
  - `npx tsc --noEmit` → `mypy .` or `pyright`

- **Working directory** — adjust if the project has a non-standard structure (monorepo with nested packages, etc.).

### What to Preserve

- **Event types** — keep the original event type (PreCommit, PostEdit, etc.) unless it clearly doesn't apply.
- **Hook structure** — maintain the JSON schema expected by Claude Code.
- **Error handling** — preserve any error handling or fallback behavior.

### Hook JSON Structure

```json
{
  "hooks": {
    "PreCommit": [
      {
        "matcher": "**/*.py",
        "command": "ruff check --fix ${file}"
      }
    ],
    "PostEdit": [
      {
        "matcher": "**/*.py",
        "command": "ruff format ${file}"
      }
    ]
  }
}
```

When merging into an existing `settings.json`:
1. Preserve all existing hooks.
2. Append new hooks under the appropriate event keys.
3. Avoid duplicate hooks (same event + same matcher + same command).

---

## Cross-References

- [`SKILL.md`](../SKILL.md) — main `/ignite` procedure (this guide is used in Step 5)
- [`ignite-workflow.md`](ignite-workflow.md) — detailed step-by-step workflow
- [`gap-analysis-guide.md`](gap-analysis-guide.md) — coverage assessment for technologies without dedicated entities
