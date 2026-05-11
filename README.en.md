# claude-project-bootstrap

> Claude Code plugin that bootstraps new projects with **negative-first** rules, a **baseline test harness**, and accessibility/dict-duplicate guards. Scaffolds CLAUDE.md, testing framework docs, pre-commit hooks, and a dynamic `baseline.yml` tailored to the project type you pick.

**[한국어 README](README.md)**

This plugin provides a reusable framework so every new project starts with consistent conventions in Claude Code. Patterns crystallized from real-world trial-and-error become **defaults** for your next project.

---

## Quick Start

```bash
# 1. Add marketplace
claude plugin marketplace add seungjaeyuu/claude-project-bootstrap

# 2. Install
claude plugin install claude-project-bootstrap

# 3. In a new project directory, run Claude Code and type:
/claude-project-bootstrap:init-project
```

`/claude-project-bootstrap:init-project` walks you through interactive prompts and generates only the files you need.

> **Namespace note**: Plugin commands require the `/<plugin-name>:<command>` prefix (as of Claude Code v2.1.117). `/init-project` alone will fail — always use `/claude-project-bootstrap:init-project`.

---

## Updating (already-installed users)

Claude Code has no dedicated `upgrade` command — it's a two-step **refresh marketplace → reinstall**:

```bash
# 1) Refresh marketplace metadata (so the new version is seen)
claude plugin marketplace update seungjaeyuu-plugins

# 2) Reinstall = update
claude plugin uninstall claude-project-bootstrap@seungjaeyuu-plugins
claude plugin install  claude-project-bootstrap@seungjaeyuu-plugins
```

The same works as `/plugin ...` slash commands inside a session; append `/reload-plugins` to apply it to the current session immediately. You can also use the `/plugin` interactive UI (**Marketplaces → Update marketplace listings**) or toggle **auto-update** for the marketplace.

> Not sure of the marketplace identifier? Run `claude plugin marketplace list` (this repo registers as `seungjaeyuu-plugins`).

---

## What It Provides

### 6 Slash Commands

| Command | Purpose |
|---|---|
| `/claude-project-bootstrap:init-project` | Initialize a new project — selectively generates `CLAUDE.md`, `.gitignore`, `TESTING_FRAMEWORK.md`, `BASELINE.md`, hooks, etc. |
| `/claude-project-bootstrap:baseline-review` | Suggest baseline updates based on Git diff |
| `/claude-project-bootstrap:bash-permission` *(v0.2.0)* | Set Bash permission tier (YOLO / Standard / Strict / None) |
| `/claude-project-bootstrap:firebase-isolation` *(v0.2.0)* | Add Firebase isolation (`.firebaserc` + predeploy hook + verification script) |
| `/claude-project-bootstrap:slim-claude-md` *(v0.2.0)* | Slim down oversized CLAUDE.md + split into per-domain RULES files |
| `/claude-project-bootstrap:doc-size-hook` *(v0.2.0)* | Add doc size threshold hook (CLAUDE.md 120 lines / RULES 250 lines) |

### Generated Files (by option)

| Option | Generated Files |
|---|---|
| Default (always) | `CLAUDE.md`, `INDEX.md`, `.gitignore`, `.secret/.gitkeep` |
| E2E test framework? (Yes) | `TESTING_FRAMEWORK.md`, `{APP}_MASTER_TEST_BASELINE.md`, `scripts/baseline.yml` |
| Firebase/Supabase? (Yes) | Default-deny security rules guide + `.env.example` |
| Auto-install hooks? (Yes) | `.claude/settings.json`, `.git/hooks/pre-commit` symlink, `scripts/check_*.py`, `scripts/baseline_*.py` |
| Accessibility identifiers? (Yes) | `ACCESSIBILITY_IDENTIFIERS.md` template + related scripts |

### Python Scripts (copied to target project)

| Script | Function |
|---|---|
| `baseline_status.py` | Aggregate baseline test status |
| `baseline_update_suggest.py` | Suggest baseline updates from Git diff |
| `check_baseline_sync.py` | Pre-commit — verify baseline sync when UI files change |
| `check_accessibility_identifiers.py` | SwiftUI/Kotlin Compose accessibility label validation |
| `check_dict_duplicates.py` | Detect duplicate keys in Swift/Kotlin/TypeScript dict literals |

---

## Design Philosophy

**Negative-first** — Rules only say what NOT to do; everything else is allowed. General best practices that a high-performance LLM can figure out on its own are excluded from templates.

**4-tier rule legend** — Each rule's enforcement level is explicit:
- 🚫 Guardrail (hard block)
- 📐 Schema (structural requirement)
- 📎 Reference (should follow)
- 💡 Recommendation (nice to have)

**Single SSOT + discovery path optimization** — No copy-pasting the same rule in multiple places. The design focuses on "which context triggers Claude to read which file."

Details: [`docs/design-principles.md`](docs/design-principles.md)

---

## Applying v0.2.0 Features to Existing Projects

Projects initialized with v0.1.x continue to work as-is. To adopt v0.2.0 features, use the dedicated commands:

```bash
/claude-project-bootstrap:bash-permission      # Set Bash permission tier
/claude-project-bootstrap:firebase-isolation    # Add Firebase isolation
/claude-project-bootstrap:slim-claude-md        # Slim down CLAUDE.md
/claude-project-bootstrap:doc-size-hook         # Add doc size hook
```

Each command has 4 safety layers: auto-backup (`_backup_v0.1/`), diff preview, per-domain independence, and diagnosis-based changes. See [`CHANGELOG.md`](CHANGELOG.md) for details.

---

## Docs

- [Design Principles](docs/design-principles.md)
- [Decision Log](docs/changelog-decisions.md)
- [Migration Guide](docs/migration-guide.md) (for legacy `_PROJECT_FRAMEWORK` users)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Issues and PRs in English are welcome.

## License

[MIT](LICENSE) © 2026 Yu Seungjae
