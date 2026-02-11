# CLAUDE.md Lifecycle Guidelines

These behavioral rules must be embedded into every project's `CLAUDE.md` during `/ignite` (initial creation) and preserved across all subsequent modifications. They govern how Claude Code interacts with the user throughout the development lifecycle.

## Rules for CLAUDE.md Content

The `/ignite` skill and any command that modifies `CLAUDE.md` (e.g., `/init`, manual updates) must include the following directives in the generated file:

**1. Write-first, never chat-first**
> When asked to create a plan, save it to a file, or write documentation, ALWAYS write it to a file immediately. Do NOT present it in plan mode or chat output first — write directly to the requested file path. If no path is specified, ask for one before proceeding.

**2. No preemptive execution**
> Do NOT start implementing or running code unless the user explicitly asks you to. When presenting a plan or analysis, wait for user approval before taking action. Never run code preemptively.

**3. No scope creep**
> Do NOT extrapolate, suggest features, or expand scope beyond what was explicitly requested. If you have ideas, mention them briefly at the end but do not elaborate unless asked.

**4. Clarify before acting**
> When you don't understand a request (especially if it's in Italian or domain-specific), ASK for clarification rather than guessing and jumping into action. It's better to ask one question than to waste time on a wrong approach.

## Domain-Specific Workflow Rules

These are additional sections that `/ignite` should generate in `CLAUDE.md` when the project's domain matches. Unlike the core behavioral rules (always included), these are conditionally included based on project characteristics detected during ignition.

**## General Conventions** *(always include)*

> This project primarily uses Markdown and YAML files. When editing these, preserve existing formatting conventions (indentation, heading levels, list styles) unless explicitly asked to change them.

**## Document Validation** *(include when project contains markdown documents, guidelines, or compliance-driven content)*

> When validating documents against guidelines or requirements, always perform TWO passes: first identify all non-conformities, then re-read the document to catch anything missed before applying fixes. Never assume the first pass caught everything.

> When validating documents against adherence guidelines, always complete the full validation pass before starting corrections. Present a summary of ALL issues found first, then ask which to fix — never interleave analysis and editing.

> When renumbering sections, citations, or bibliographic references, always do a full-document consistency pass after renumbering. Grep for ALL old reference numbers to catch orphaned citations before presenting results.

> When working with Work Package (WP) documents or research proposal files, always validate against the content adherence requirements/guidelines before considering the task complete. Flag any discursive style violations, missing sections, or formatting non-conformities.

**## Task Management** *(always include)*

> For long multi-file document tasks, use TodoWrite to create a checklist of all files/sections to process BEFORE starting work. Update the checklist as each item completes. This ensures work can resume cleanly if interrupted by usage limits.

**## Docker / Infrastructure** *(include when project uses Docker Compose or containerized development)*

> When working with Docker Compose / infrastructure files (YAML), always check version compatibility between services before recommending upgrades. Verify Docker API version compatibility, volume mount path changes, and environment variable changes across major version bumps.

> This project uses Docker Compose for the development environment. When modifying environment variables or container configuration, always verify variable names match between docker-compose.yml, env templates, and application code. Never modify container entrypoint commands without checking the existing entrypoint first.

**## Grant Proposal Documents** *(include when project contains work package / grant proposal markdown files)*

> When working with grant proposal / work package markdown files: the bibliography is maintained in a separate file. Always cross-reference it when editing citations. Citation format is [N] with page numbers where applicable. Never remove or renumber citations without updating ALL references across ALL WP files.

## How These Rules Are Applied

- **During `/ignite`**: The core behavioral rules (1–4) are always written into a `## Behavioral Rules` section of the generated `CLAUDE.md`, near the top of the file (after project description, before installed entities). Domain-specific workflow rules are added as separate top-level sections when their inclusion condition is met.
- **During CLAUDE.md updates**: Any skill or agent that modifies `CLAUDE.md` (e.g., the doc-updater agent, the `/ignite` re-run) must preserve both `## Behavioral Rules` and all domain-specific workflow sections unchanged. They are never removed, overwritten, or diluted.
- **Extensibility**: The user may add additional project-specific rules to any of these sections. The igniter treats user-added rules as immutable — they are preserved verbatim during any automated update.