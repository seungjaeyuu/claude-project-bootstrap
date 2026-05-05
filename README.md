# claude-project-bootstrap

> Claude Code plugin that bootstraps new projects with **negative-first** rules, a **baseline test harness**, and accessibility/dict-duplicate guards. Scaffolds CLAUDE.md, testing framework docs, pre-commit hooks, and a dynamic `baseline.yml` tailored to the project type you pick.

**본 플러그인은 새 프로젝트 시작 시 Claude Code 에서 일관된 규약으로 출발할 수 있게 하는 재사용 프레임워크입니다.** 실전 프로젝트에서 반복 시행착오로 결정화된 패턴을 다음 프로젝트부터 **기본값으로** 적용합니다.

---

## 빠른 시작

```bash
# 1. 마켓플레이스 등록
claude plugin marketplace add seungjaeyuu/claude-project-bootstrap

# 2. 설치
claude plugin install claude-project-bootstrap

# 3. 새 프로젝트 폴더에서 Claude Code 실행 후:
/claude-project-bootstrap:init-project
```

`/claude-project-bootstrap:init-project` 가 대화형 질의를 통해 필요한 파일만 생성합니다.

> **Claude Code 커맨드 네임스페이스**: 플러그인 커맨드는 `/<plugin-name>:<command>` 형식 prefix 가 강제됩니다 (Claude Code v2.1.117 기준). 따라서 `/init-project` 단독 호출은 `Unknown command` 에러. 반드시 `/claude-project-bootstrap:` prefix 포함.

---

## 제공하는 것

### 슬래시 커맨드 6개

| 커맨드 | 용도 |
|---|---|
| `/claude-project-bootstrap:init-project` | 새 프로젝트 초기화 — `CLAUDE.md`, `.gitignore`, `TESTING_FRAMEWORK.md`, `BASELINE.md`, hooks 등을 선택적으로 생성 |
| `/claude-project-bootstrap:baseline-review` | E2E 테스트 베이스라인 갱신 제안 (Git diff 기반) |
| `/claude-project-bootstrap:bash-permission` *(v0.2.0)* | Bash 권한 단계 도입·변경 (YOLO/Standard/Strict/None) |
| `/claude-project-bootstrap:firebase-isolation` *(v0.2.0)* | Firebase 격리 도입 (`.firebaserc` + predeploy hook + 검증 스크립트) |
| `/claude-project-bootstrap:slim-claude-md` *(v0.2.0)* | 비대해진 CLAUDE.md 슬림화 + 영역별 RULES 분리 (진단·확인 기반) |
| `/claude-project-bootstrap:doc-size-hook` *(v0.2.0)* | 문서 크기 임계치 hook 도입 (CLAUDE.md 120줄 / RULES 250줄) |

### 생성되는 파일 (옵션별)

| 옵션 | 생성되는 파일 |
|---|---|
| 기본 (모두 필수) | `CLAUDE.md`, `INDEX.md`, `.gitignore`, `.secret/.gitkeep` |
| E2E 테스트 프레임워크 필요? (Yes) | `TESTING_FRAMEWORK.md`, `{APP}_MASTER_TEST_BASELINE.md`, `scripts/baseline.yml` |
| Firebase/Supabase 사용? (Yes) | default-deny 보안 규칙 안내 섹션 + `.env.example` 초안 |
| Hook 자동 설치? (Yes) | `.claude/settings.json`, `.git/hooks/pre-commit` symlink, `scripts/check_*.py`, `scripts/baseline_*.py` |
| Accessibility identifier 검증? (Yes) | `ACCESSIBILITY_IDENTIFIERS.md` 템플릿 + 관련 스크립트 |
| 개발 백로그 관리? (Yes) | `/개발예정사항.md` + `개발예정사항_상세/` 구조 |

### 제공하는 Python 스크립트 (target 프로젝트로 복사)

| 스크립트 | 기능 |
|---|---|
| `baseline_status.py` | 베이스라인 판정 상태 집계 |
| `baseline_update_suggest.py` | Git diff 기반 베이스라인 갱신 제안 |
| `check_baseline_sync.py` | pre-commit — UI 파일 수정 시 baseline 갱신 확인 |
| `check_accessibility_identifiers.py` | SwiftUI/Kotlin Compose accessibility 라벨 검증 |
| `check_dict_duplicates.py` | Swift/Kotlin/TypeScript dict literal 중복 키 검출 |

---

## 설계 철학

**네거티브 우선** — 규칙은 "하지 말라" 만 적고 그 외는 모두 허용. 고성능 LLM 이 자력 판단 가능한 일반 모범 사례는 템플릿에서 제외.

**4층 규칙 범례** — 🚫 Guardrail / 📐 Schema / 📎 참조 / 💡 권장. 각 규칙의 강제력을 명시.

**단일 SSOT + 발견 경로 최적화** — 같은 규칙을 여러 곳에 복붙하지 않음. "어느 맥락에서 Claude 가 Read 하는가" 를 설계.

상세 근거: [`docs/design-principles.md`](docs/design-principles.md)

---

## 마이그레이션 (기존 `_PROJECT_FRAMEWORK` 사용자)

기존에 `~/Documents/GitHub/_PROJECT_FRAMEWORK/` 로컬 폴더 + `~/.claude/commands/init-project.md` 를 사용하셨다면 [`docs/migration-guide.md`](docs/migration-guide.md) 참조.

## v0.2.0 새 기능 (기존 사용자 적용)

v0.1.x 로 init 한 프로젝트는 **그대로 작동** — 자동 변경되지 않습니다. v0.2.0 의 새 기능을 도입하려면 4개 기능별 커맨드 사용:

```bash
# Bash 권한 단계 도입 (또는 변경)
/claude-project-bootstrap:bash-permission

# Firebase 격리 도입 (Firebase 사용 프로젝트만)
/claude-project-bootstrap:firebase-isolation

# CLAUDE.md 슬림화 + RULES 분리
/claude-project-bootstrap:slim-claude-md

# 문서 크기 hook 도입
/claude-project-bootstrap:doc-size-hook
```

각 커맨드는 4중 안전장치(자동 백업 / Diff preview / 영역별 독립 / 본체는 진단·확인 기반) 내장. `_backup_v0.1/` 로 자동 백업되어 언제든 복원 가능. 자세한 내용은 [`CHANGELOG.md`](CHANGELOG.md) v0.2.0 항목.

---

## 문서

- [설계 원칙](docs/design-principles.md) — 왜 이렇게 설계했는지
- [내부 결정 로그](docs/changelog-decisions.md) — 보조 결정 기록
- [마이그레이션 가이드](docs/migration-guide.md) — 기존 사용자용
- [스펙 (전체 설계 문서)](docs/specs/2026-04-23-claude-project-bootstrap-plugin-design.md)

---

## 라이선스

[MIT](LICENSE) © 2026 Yu Seungjae
