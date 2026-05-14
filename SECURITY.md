# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.3.x   | :white_check_mark: |
| 0.2.x   | :x: (upgrade recommended) |
| 0.1.x   | :x: |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, **please do NOT open a public GitHub issue.**

Instead, report it privately:

1. **Email**: [yu.seungjae@gmail.com](mailto:yu.seungjae@gmail.com)
2. **Subject**: `[SECURITY] claude-project-bootstrap — <brief description>`

### What to include

- Description of the vulnerability
- Steps to reproduce
- Affected versions
- Potential impact

### Response timeline

- **Acknowledgment**: within 48 hours
- **Initial assessment**: within 7 days
- **Fix release**: as soon as practical, depending on severity

### Scope

This plugin generates configuration files and shell scripts for target projects. Security concerns include:

- **Shell injection** in generated hook scripts (`pre-commit-framework.sh`, `post-merge.sh`)
- **Secret exposure** in generated templates (`.gitignore` patterns, `.secret/` handling)
- **Permission escalation** in Bash permission templates (`permissions/*.json`)
- **Firebase project mismatch** in isolation scripts (`check_firebase_project.py`)

### Recognition

Security reporters will be credited in the release notes (unless anonymity is preferred).
