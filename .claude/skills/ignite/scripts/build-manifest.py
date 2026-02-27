#!/usr/bin/env python3
"""
build-manifest.py — Scan synced catalog sources and generate manifest.json.

Reads catalog/sources.json to discover sources and their entityPaths,
scans each source directory for entities (agents, skills, commands, rules, hooks),
classifies them with tags, and writes catalog/manifest.json.

Python 3.10+, stdlib only.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[3]  # .claude/skills/ignite/scripts/ -> root
SOURCES_JSON = PROJECT_ROOT / "catalog" / "sources.json"
CATALOG_DIR = PROJECT_ROOT / "catalog"
SOURCES_DIR = CATALOG_DIR / "sources"
OUTPUT_FILE = CATALOG_DIR / "manifest.json"

CONTENT_PREVIEW_LINES = 200

# ---------------------------------------------------------------------------
# Keyword maps for tag classification
# ---------------------------------------------------------------------------

LANGUAGE_KEYWORDS: dict[str, list[str]] = {
    "python": [
        "python", "pytest", "pip", "pyproject", "pylint", "mypy",
        "ruff", "poetry", "flake8", "pep8", "virtualenv", "venv",
    ],
    "typescript": [
        "typescript", "tsconfig", "tsx",
    ],
    "javascript": [
        "javascript", "eslint", "prettier", "npm", "yarn", "pnpm",
        "nodejs", "node-",
    ],
    "go": [
        "golang", "go-mod", "go-sum", "go-vet", "gofmt", "golint",
        "goroutine",
    ],
    "java": [
        "java", "jvm", "maven", "gradle", "junit", "jdk",
    ],
    "rust": [
        "rust", "cargo", "crate", "rustfmt", "clippy",
    ],
    "cpp": [
        "cpp", "c\\+\\+", "cmake", "clang", "gcc",
    ],
    "ruby": [
        "ruby", "rails", "gem", "bundler", "rake", "rspec",
    ],
    "php": [
        "php", "laravel", "composer", "artisan", "symfony",
    ],
    "swift": [
        "swift", "xcode", "cocoapod", "swiftpm", "swiftui",
    ],
    "kotlin": [
        "kotlin", "android", "jetpack",
    ],
    "csharp": [
        "csharp", "c#", "dotnet", "\\.net", "nuget",
    ],
}

FRAMEWORK_KEYWORDS: dict[str, list[str]] = {
    "django": ["django"],
    "flask": ["flask"],
    "fastapi": ["fastapi", "fast-api"],
    "react": ["react", "jsx", "tsx"],
    "nextjs": ["nextjs", "next\\.js", "next-js"],
    "vue": ["vue", "vuejs", "nuxt"],
    "angular": ["angular"],
    "spring": ["spring", "springboot", "spring-boot"],
    "express": ["express", "expressjs"],
    "rails": ["rails", "ruby-on-rails"],
    "laravel": ["laravel"],
    "docker": ["docker", "dockerfile", "docker-compose", "container"],
    "postgres": ["postgres", "postgresql"],
    "clickhouse": ["clickhouse"],
    "jpa": ["jpa", "hibernate"],
}

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "testing": ["test", "testing", "spec", "e2e", "integration-test", "unit-test"],
    "tdd": ["tdd", "test-driven"],
    "security": ["security", "secur", "vuln", "owasp"],
    "code-review": ["review", "reviewer", "code-review"],
    "documentation": ["doc-updater", "update-docs", "documentation"],
    "ci-cd": ["ci-cd", "pipeline", "deploy", "github-action"],
    "database": ["database", "migration", "sql", "orm", "query"],
    "api": ["api-design", "rest-api", "graphql", "grpc", "openapi"],
    "devops": ["devops", "terraform", "kubernetes", "k8s", "helm"],
    "architecture": ["architect", "architecture", "design-pattern"],
    "planning": ["plan", "planner", "planning", "roadmap"],
    "debugging": ["debug", "troubleshoot", "error-resolv", "build-error", "build-fix"],
    "refactoring": ["refactor", "clean", "restructure"],
    "performance": ["performance", "perf", "optimize", "benchmark", "cache"],
    "build": ["build", "compile", "bundle", "webpack", "vite"],
    "orchestration": ["orchestrat", "multi-", "workflow", "pipeline"],
    "deployment": ["deploy", "deployment-pattern"],
    "coding-standards": ["coding-standard", "coding-style", "lint"],
    "verification": ["verif", "verify"],
    "learning": ["learn", "continuous-learning"],
    "cost-optimization": ["cost-aware", "cost-optim", "llm-pipeline"],
}

# ---------------------------------------------------------------------------
# Core entity registry
# ---------------------------------------------------------------------------

CORE_ENTITIES: dict[str, set[str]] = {
    "agent": {
        "planner", "architect", "code-reviewer",
        "security-reviewer", "build-error-resolver",
    },
    "skill": {
        "tdd-workflow", "coding-standards",
        "verification-loop", "security-review",
    },
    "command": {
        "plan", "tdd", "code-review", "build-fix", "verify",
    },
    # Rules: handled separately — all files under common/ are core
}

# Entity type singular names (for composite IDs)
ENTITY_TYPE_MAP: dict[str, str] = {
    "agents": "agent",
    "skills": "skill",
    "commands": "command",
    "rules": "rule",
    "hooks": "hook",
}


# ---------------------------------------------------------------------------
# Name normalization & core entity check
# ---------------------------------------------------------------------------

def normalize_name(name: str) -> str:
    """Normalize entity name: lowercase, replace underscores/spaces with hyphens."""
    result = name.lower().strip()
    # Strip .md extension if present
    if result.endswith(".md"):
        result = result[:-3]
    return re.sub(r"[_\s]+", "-", result)


def is_core_entity(entity_type: str, name: str, dir_context: str = "") -> bool:
    """Check if an entity is a core entity using normalized name matching.

    Normalization handles hyphens/underscores/case differences.
    Does NOT use substring matching to avoid false positives
    (e.g. 'plan' matching 'multi-plan').
    """
    # Rules: all files in common/ directory are core
    if entity_type == "rule" and dir_context.startswith("common"):
        return True

    normalized = normalize_name(name)
    core_set = CORE_ENTITIES.get(entity_type, set())

    # Exact match after normalization
    return normalized in core_set


# ---------------------------------------------------------------------------
# Tag classification
# ---------------------------------------------------------------------------

def _match_keywords(
    text: str,
    keyword_map: dict[str, list[str]],
) -> list[str]:
    """Find all matching tags by scanning text against keyword patterns."""
    matches: set[str] = set()
    for tag, keywords in keyword_map.items():
        for kw in keywords:
            # Use word-boundary-like matching for short keywords
            pattern = rf"(?:^|[\s/\-_.,(]){re.escape(kw)}(?:[\s/\-_.),]|$)"
            if re.search(pattern, text, re.IGNORECASE):
                matches.add(tag)
                break
    return sorted(matches)


def _match_go(text: str) -> bool:
    """Special Go language detection with strict word boundaries."""
    go_patterns = [
        r"\bgolang\b",
        r"\bgo[-_]",
        r"[-_]go\b",
        r"\bgo[-_]mod\b",
        r"\bgo[-_]sum\b",
        r"\bgo[-_]vet\b",
        r"\bgofmt\b",
        r"\bgolint\b",
        r"\bgoroutine\b",
        r"\bgo[-_]build\b",
        r"\bgo[-_]test\b",
        r"\bgo[-_]review\b",
        r"\bgo[-_]reviewer\b",
    ]
    for pattern in go_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def classify_tags(
    name: str,
    dir_path: str,
    content_preview: str,
) -> dict:
    """Classify an entity's tags by scanning name, path, and content."""
    # Build corpus with weighted sections
    # Name and path get 3x weight for more reliable signal
    name_path = f" {name} {dir_path} " * 3
    corpus = name_path + " " + content_preview

    languages = _match_keywords(corpus, LANGUAGE_KEYWORDS)
    frameworks = _match_keywords(corpus, FRAMEWORK_KEYWORDS)
    categories = _match_keywords(corpus, CATEGORY_KEYWORDS)

    # Special Go handling
    if "go" not in languages and _match_go(f" {name} {dir_path} "):
        languages = sorted(set(languages) | {"go"})
    # Also check content but with stricter patterns
    if "go" not in languages and _match_go(content_preview):
        languages = sorted(set(languages) | {"go"})

    # Determine scope
    if frameworks:
        scope = "framework-specific"
    elif languages:
        scope = "language-specific"
    else:
        scope = "universal"

    return {
        "languages": languages,
        "frameworks": frameworks,
        "categories": categories,
        "scope": scope,
    }


# ---------------------------------------------------------------------------
# Entity discovery functions
# ---------------------------------------------------------------------------

def _read_preview(file_path: Path) -> str:
    """Read first N lines of a file for content-based classification."""
    try:
        lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
        return "\n".join(lines[:CONTENT_PREVIEW_LINES])
    except OSError as e:
        print(f"  WARNING: Cannot read {file_path}: {e}", file=sys.stderr)
        return ""


def _is_readme(path: Path) -> bool:
    """Check if a path is a README file (case-insensitive)."""
    return path.name.lower() == "readme.md"


def discover_agents(entity_dir: Path) -> list[dict]:
    """Discover agent entities: .md files in the agents directory."""
    if not entity_dir.is_dir():
        return []
    entities = []
    for f in sorted(entity_dir.iterdir()):
        if f.is_file() and f.suffix == ".md" and not _is_readme(f):
            entities.append({
                "name": f.stem,
                "path": str(f),
                "content_preview": _read_preview(f),
            })
    return entities


def discover_skills(entity_dir: Path) -> list[dict]:
    """Discover skill entities: directories with SKILL.md, fallback to .md files."""
    if not entity_dir.is_dir():
        return []
    entities = []

    # Primary: directories containing SKILL.md
    for d in sorted(entity_dir.iterdir()):
        if d.is_dir():
            skill_md = d / "SKILL.md"
            if skill_md.exists():
                entities.append({
                    "name": d.name,
                    "path": str(skill_md),
                    "content_preview": _read_preview(skill_md),
                })

    # Fallback: if no SKILL.md directories found, try .md files directly
    if not entities:
        for f in sorted(entity_dir.iterdir()):
            if f.is_file() and f.suffix == ".md" and not _is_readme(f):
                entities.append({
                    "name": f.stem,
                    "path": str(f),
                    "content_preview": _read_preview(f),
                })

    return entities


def discover_commands(entity_dir: Path) -> list[dict]:
    """Discover command entities: .md files in the commands directory."""
    if not entity_dir.is_dir():
        return []
    entities = []
    for f in sorted(entity_dir.iterdir()):
        if f.is_file() and f.suffix == ".md" and not _is_readme(f):
            entities.append({
                "name": f.stem,
                "path": str(f),
                "content_preview": _read_preview(f),
            })
    return entities


def discover_rules(entity_dir: Path) -> list[dict]:
    """Discover rule entities: .md files recursively, preserving subdirectory context."""
    if not entity_dir.is_dir():
        return []
    entities = []

    # Walk recursively through subdirectories
    for md_file in sorted(entity_dir.rglob("*.md")):
        if _is_readme(md_file):
            continue
        # Name includes subdirectory context relative to entity_dir
        rel = md_file.relative_to(entity_dir)
        # e.g. common/coding-style.md -> common/coding-style
        name = str(rel.with_suffix(""))
        entities.append({
            "name": name,
            "path": str(md_file),
            "content_preview": _read_preview(md_file),
            "dir_context": str(rel.parent) if rel.parent != Path(".") else "",
        })
    return entities


def discover_hooks(entity_dir: Path) -> list[dict]:
    """Discover hook entities from hooks.json, treating each hook entry individually."""
    hooks_json = entity_dir / "hooks.json"
    if not hooks_json.exists():
        return []

    try:
        data = json.loads(hooks_json.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"  WARNING: Cannot parse {hooks_json}: {e}", file=sys.stderr)
        return []

    # The hooks.json structure is:
    # { "hooks": { "EventType": [ { "matcher": "...", "hooks": [...], "description": "..." } ] } }
    hooks_data = data.get("hooks", data) if isinstance(data, dict) else {}
    if not isinstance(hooks_data, dict):
        print(f"  WARNING: Unexpected hooks.json format in {entity_dir}", file=sys.stderr)
        return []

    entities = []
    seen_names: set[str] = set()

    for event_type, hook_list in sorted(hooks_data.items()):
        if not isinstance(hook_list, list):
            continue
        for i, hook_entry in enumerate(hook_list):
            if not isinstance(hook_entry, dict):
                continue

            matcher = hook_entry.get("matcher", "")
            description = hook_entry.get("description", "")

            # Build a unique name from event type + matcher
            base_name = normalize_name(f"{event_type}-{matcher}") if matcher else f"{normalize_name(event_type)}-{i}"

            # Ensure uniqueness
            name = base_name
            counter = 2
            while name in seen_names:
                name = f"{base_name}-{counter}"
                counter += 1
            seen_names.add(name)

            entities.append({
                "name": name,
                "path": str(hooks_json),
                "content_preview": f"{event_type} {matcher} {description}",
                "metadata": {
                    "event": event_type,
                    "matcher": matcher,
                    "description": description,
                },
            })

    return entities


# Discovery function dispatch
DISCOVER_FUNCTIONS: dict[str, callable] = {
    "agents": discover_agents,
    "skills": discover_skills,
    "commands": discover_commands,
    "rules": discover_rules,
    "hooks": discover_hooks,
}


# ---------------------------------------------------------------------------
# Source and coverage helpers
# ---------------------------------------------------------------------------

def load_sources() -> list[dict]:
    """Load and return sources from catalog/sources.json."""
    try:
        data = json.loads(SOURCES_JSON.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"FATAL: {SOURCES_JSON} not found", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"FATAL: Cannot parse {SOURCES_JSON}: {e}", file=sys.stderr)
        sys.exit(1)

    sources = data.get("sources", [])
    if not sources:
        print(f"FATAL: No sources found in {SOURCES_JSON}", file=sys.stderr)
        sys.exit(1)

    return sources


def load_source_meta(source_dir: Path) -> dict | None:
    """Load .source-meta.json for a synced source."""
    meta_file = source_dir / ".source-meta.json"
    if not meta_file.exists():
        return None
    try:
        return json.loads(meta_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"  WARNING: Cannot read {meta_file}: {e}", file=sys.stderr)
        return None


def build_coverage(entities: list[dict]) -> dict:
    """Build aggregated coverage summary from all entities."""
    languages: set[str] = set()
    frameworks: set[str] = set()
    categories: set[str] = set()

    for entity in entities:
        tags = entity.get("tags", {})
        languages.update(tags.get("languages", []))
        frameworks.update(tags.get("frameworks", []))
        categories.update(tags.get("categories", []))

    return {
        "languages": sorted(languages),
        "frameworks": sorted(frameworks),
        "categories": sorted(categories),
    }


def requires_adaptation(tags: dict, is_core: bool) -> bool:
    """Determine if an entity needs specialization during install."""
    if is_core:
        return False
    if tags.get("scope") == "universal":
        return False
    return bool(tags.get("languages") or tags.get("frameworks"))


# ---------------------------------------------------------------------------
# Entity assembly
# ---------------------------------------------------------------------------

def discover_entities(source: dict, source_dir: Path) -> list[dict]:
    """Discover all entities for a source, classify tags, and assemble metadata."""
    source_id = source["id"]
    entity_paths = source.get("entityPaths", {})
    all_entities: list[dict] = []

    for entity_type_plural, rel_path in sorted(entity_paths.items()):
        entity_type = ENTITY_TYPE_MAP.get(entity_type_plural)
        if entity_type is None:
            print(
                f"  WARNING: Unknown entity type '{entity_type_plural}', skipping",
                file=sys.stderr,
            )
            continue

        discover_fn = DISCOVER_FUNCTIONS.get(entity_type_plural)
        if discover_fn is None:
            continue

        entity_dir = source_dir / rel_path
        if not entity_dir.exists():
            print(
                f"  WARNING: Entity directory {entity_dir} does not exist, skipping",
                file=sys.stderr,
            )
            continue

        raw_entities = discover_fn(entity_dir)

        for raw in raw_entities:
            name = raw["name"]
            dir_context = raw.get("dir_context", "")
            content_preview = raw.get("content_preview", "")

            # Classify tags
            tags = classify_tags(name, f"{entity_type_plural}/{dir_context}", content_preview)

            # Core entity check
            core = is_core_entity(entity_type, name, dir_context)

            # Adaptation detection
            adaptation = requires_adaptation(tags, core)

            # Build composite ID
            composite_id = f"{source_id}::{entity_type}::{name}"

            # Compute relative path from project root
            entity_path = raw["path"]
            try:
                entity_path = str(Path(entity_path).relative_to(PROJECT_ROOT))
            except ValueError:
                pass  # Keep absolute if not under project root

            entity = {
                "id": composite_id,
                "source": source_id,
                "type": entity_type,
                "name": name,
                "path": entity_path,
                "tags": tags,
                "coreEntity": core,
                "requiresAdaptation": adaptation,
                "metadata": raw.get("metadata", {}),
            }
            all_entities.append(entity)

        print(
            f"  {entity_type_plural}: {len(raw_entities)} entities",
            file=sys.stderr,
        )

    return all_entities


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    """Build the manifest from all catalog sources."""
    print(
        f"build-manifest.py -- {datetime.now(timezone.utc).isoformat()}",
        file=sys.stderr,
    )
    print(f"Loading sources from {SOURCES_JSON}", file=sys.stderr)

    sources = load_sources()
    print(f"Found {len(sources)} sources\n", file=sys.stderr)

    all_entities: list[dict] = []
    sources_meta: dict[str, dict] = {}

    for source in sources:
        source_id = source["id"]
        source_dir = SOURCES_DIR / source_id

        # Skip sources with no URL that haven't been populated
        if source.get("url") is None and not source_dir.exists():
            print(f"--- Skipping '{source_id}' (no remote URL, directory absent) ---\n", file=sys.stderr)
            continue

        if not source_dir.exists():
            print(
                f"--- Skipping '{source_id}' (directory not found: {source_dir}) ---\n",
                file=sys.stderr,
            )
            continue

        print(f"--- Scanning '{source_id}' ---", file=sys.stderr)

        # Load sync metadata
        meta = load_source_meta(source_dir)
        sources_meta[source_id] = meta or {"id": source_id, "note": "no sync metadata"}

        # Discover entities
        entities = discover_entities(source, source_dir)
        all_entities.extend(entities)
        print(file=sys.stderr)

    # Build output
    coverage = build_coverage(all_entities)

    output = {
        "entities": sorted(all_entities, key=lambda e: e["id"]),
        "coverage": coverage,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sources": sources_meta,
    }

    # Write manifest
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(output, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    # Summary
    core_count = sum(1 for e in all_entities if e["coreEntity"])
    print("--- Summary ---", file=sys.stderr)
    print(f"Total entities: {len(all_entities)}", file=sys.stderr)
    print(f"Core entities: {core_count}", file=sys.stderr)
    print(
        f"Coverage: {len(coverage['languages'])} languages, "
        f"{len(coverage['frameworks'])} frameworks, "
        f"{len(coverage['categories'])} categories",
        file=sys.stderr,
    )
    print(f"Output: {OUTPUT_FILE}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
