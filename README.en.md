# claude-project-bootstrap

> Claude Code plugin: bootstrap new projects with **negative-first** rules, a **baseline E2E harness**, and **context optimization**.

**A reusable framework that turns real-world trial-and-error patterns into defaults for your next project.**

**[한국어 README](README.md)**

---

## Quick Start

```bash
# 1. Add marketplace
claude plugin marketplace add seungjaeyuu/claude-project-bootstrap

# 2. Install
claude plugin install claude-project-bootstrap

# 3. In a new project directory, run Claude Code and type:
/claude-project-bootstrap:init
```

> **Namespace note**: Plugin commands require the `/<plugin-name>:<command>` prefix (Claude Code convention). `/init` alone returns `Unknown command` — always use `/claude-project-bootstrap:init`.

---

## Updating (already-installed users)

```bash
# 1) Refresh marketplace metadata
claude plugin marketplace update seungjaeyuu-plugins

# 2) Reinstall = update
claude plugin uninstall claude-project-bootstrap@seungjaeyuu-plugins
claude plugin install  claude-project-bootstrap@seungjaeyuu-plugins
```

> Also available via `/plugin` interactive UI: **Marketplaces → Update marketplace listings** or the **auto-update** toggle.

---

## What It Provides

### Slash Commands

#### Main Commands (v0.3.0+)

| Command | Purpose |
|---|---|
| `/claude-project-bootstrap:init` | Initialize new project + reconfigure existing (up to 8 interactive prompts) |
| `/claude-project-bootstrap:audit` | Quality, context, and baseline checks (`--context`, `--baseline`, `--quality`) |
| `/claude-project-bootstrap:release` | Release readiness check (version, security, legal, i18n, testing, accessibility) |
| `/claude-project-bootstrap:guide` | Auto-detect project phase + recommend commands |

#### Feature Commands (v0.2.0+, backward-compatible)

| Command | Purpose |
|---|---|
| `/claude-project-bootstrap:init-project` | → Merged into `/init` (kept for backward compat) |
| `/claude-project-bootstrap:baseline-review` | → Merged into `/audit --baseline` (kept for backward compat) |
| `/claude-project-bootstrap:bash-permission` | Set Bash permission tier (YOLO/Standard/Strict/None) |
| `/claude-project-bootstrap:firebase-isolation` | Add Firebase isolation (`.firebaserc` + predeploy hook) |
| `/claude-project-bootstrap:slim-claude-md` | Slim down CLAUDE.md + split into per-domain RULES |
| `/claude-project-bootstrap:doc-size-hook` | Add doc size threshold hook (CLAUDE.md 120 lines / RULES 250 lines) |

### Generated Files (by option)

| Option | Generated Files |
|---|---|
| Default (always) | `CLAUDE.md`, `INDEX.md`, `.gitignore`, `.claudeignore`, `.secret/.gitkeep` |
| `.claude/commands/` | `build.md`, `check.md`, `status.md` (build commands separated from CLAUDE.md) |
| E2E test framework? (Yes) | `TESTING_FRAMEWORK.md`, `{APP}_BASELINE.md`, `scripts/baseline.yml` |
| Firebase/Supabase? (Yes) | Default-deny security rules guide + `.env.example` |
| Auto-install hooks? (Yes) | `.claude/settings.json`, `.git/hooks/pre-commit` + `post-merge` symlink, `scripts/check_*.py` |
| TASK.md backlog? (Yes) | `TASK.md` + `tasks/DEV-XXX.md` two-layer structure |

### Per-Domain RULES (on-demand loading)

CLAUDE.md body (~99 lines) keeps only cross-cutting guardrails + a discovery trigger table. Domain rules are loaded only when relevant:

| RULES File | Trigger |
|---|---|
| `RULES_E2E.md` | E2E testing / Codex orchestrator work |
| `RULES_DATA_INTEGRITY.md` | Firestore / backend data calls |
| `RULES_ACCESSIBILITY.md` | UI component editing |
| `RULES_TERMINOLOGY.md` | Domain terms in comments/UI text |
| `RULES_DICT_DUPLICATES.md` | Dict literal editing |
| `RULES_REFACTORING.md` | 100+ line file changes / major refactoring |
| `RULES_VERSIONING.md` | Version changes / releases / main commits |
| `RULES_PROJECT_LIFECYCLE.md` | Release prep / project phase checks |

### Automatic Build Number Management

| Platform | Source of Truth | Hook Behavior |
|---|---|---|
| iOS (XcodeGen) | `project.yml` → `CURRENT_PROJECT_VERSION` | pre-commit: auto +1 + `xcodegen generate` + `.xcodeproj` staging |
| Android | `build.gradle(.kts)` → `versionCode` | pre-commit: auto +1 |
| Web / Node | `package.json` → `buildNumber` | pre-commit: auto +1 |

`post-merge` hook: auto-regenerates `.xcodeproj` when `project.yml` changes after merge (no build number change).

---

## Design Philosophy

**Negative-first** — Rules only say what NOT to do; everything else is allowed. General best practices a high-performance LLM can figure out on its own are excluded.

**4-tier rule legend** — 🚫 Guardrail / 📐 Schema / 📎 Reference / 💡 Recommendation. Each rule's enforcement level is explicit.

**Context window is finite** — ~200K tokens, with plugins/MCP consuming ~19%. Optimized via `.claudeignore`, `enabledPlugins`, and on-demand RULES loading.

**Single SSOT + discovery path optimization** — No copy-pasting rules. A trigger table maps work types → RULES files, loading only what's needed.

Details: [`docs/design-principles.md`](docs/design-principles.md)

---

## Docs

- [Design Principles](docs/design-principles.md)
- [Decision Log](docs/changelog-decisions.md)
- [Migration Guide](docs/migration-guide.md) (for legacy `_PROJECT_FRAMEWORK` users)
- [CHANGELOG](CHANGELOG.md)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Issues and PRs welcome.

## License

[MIT](LICENSE) © 2026 Yu Seungjae
