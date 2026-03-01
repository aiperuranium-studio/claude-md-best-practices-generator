### Installation

`claude plugin install` only works with plugins registered in a marketplace. Passing a GitHub URL directly fails with "not found in any configured marketplace".

**Correct install sequence (in the target project):**

```bash
claude plugin marketplace add https://github.com/aiperuranium-studio/claude-md-best-practices-generator
claude plugin install claude-md-best-practices
```

The first command registers the repo's `marketplace.json` as a source; the second installs the plugin from it.

---

### Plugin Manifest Gotchas

If you plan to edit `.claude-plugin/plugin.json`, be aware that the Claude plugin validator enforces several **undocumented but strict constraints** that can cause installs to fail with vague errors (for example, `agents: Invalid input`). In particular, component fields must be arrays, `agents` must use explicit file paths rather than directories, and a `version` field is required for reliable validation and installation.

These constraints are not obvious from public examples and have caused repeated installation failures in the past. They are documented in detail in `.claude-plugin/PLUGIN_SCHEMA_NOTES.md`, which should be reviewed before making any changes to the plugin manifest.
