# claude-project-bootstrap 플러그인 설계

> **작성일**: 2026-04-23
> **범위**: 기존 `_PROJECT_FRAMEWORK` 을 Claude Code 플러그인으로 패키지화, 마켓플레이스 공개 배포
> **상태**: 브레인스토밍 완료, 구현 계획 수립 대기

---

## 1. 개요

### 1.1 목적

`_PROJECT_FRAMEWORK` 은 새 프로젝트를 **Claude Code 에서 일관된 규약으로 시작** 하기 위한 재사용 프레임워크다. 현재는 로컬 절대경로 (`/Users/yuseungjae/Documents/GitHub/_PROJECT_FRAMEWORK/`) 에 의존하는 형태로, `~/.claude/commands/init-project.md` + 글로벌 `CLAUDE.md` 의 자동 제안 규칙으로 실행된다.

본 설계는 이 프레임워크를 **Claude Code 플러그인** 으로 재포장해 다음을 달성한다:

1. 마켓플레이스 공개 배포 — 타 사용자가 `claude plugin install` 한 줄로 설치 가능
2. 절대경로 의존 제거 — `${CLAUDE_PLUGIN_ROOT}` 기반 이식성 확보
3. 버전 관리 — semver 로 업그레이드·롤백 체계화
4. 사적 맥락 제거 — 현재 31건 산재한 SunnyWay 프로젝트 흔적을 generic 화

### 1.2 배경

- **기존 저장소**: `github.com/seungjaeyuu/_PROJECT_FRAMEWORK` (3 커밋, public)
- **현재 로컬 경로**: `~/Documents/GitHub/_PROJECT_FRAMEWORK/`
- **구성 요소**: 2 slash commands, 5 templates, 1 PostToolUse hook, 6 scripts, 1 pre-commit hook, docs/
- **선행 정리 완료**: 글로벌 `~/.claude/CLAUDE.md` 에서 `_PROJECT_FRAMEWORK` 자동 제안 규칙 제거 (Line 4, 7-8 삭제), `~/.claude/commands/init-project.md` 를 `.bak` 으로 백업

### 1.3 범위

- ✅ 플러그인 신규 저장소 생성 (`claude-project-bootstrap`)
- ✅ 기존 `_PROJECT_FRAMEWORK` 파일의 구조적 재배치 및 generic 화
- ✅ 마켓플레이스 manifest 포함 (같은 저장소가 marketplace 역할 겸임)
- ✅ 로컬 검증 후 공개 (GitHub public + archive 기존 저장소)
- ⏳ Anthropic 공식 커뮤니티 리스트 제출 — 선택사항, v1.0 이후 결정

---

## 2. 의사결정 요약 (Q1~Q6)

| # | 결정 사항 | 값 |
|---|---|---|
| Q1 | 배포 대상 | C — Claude Code 마켓플레이스 공개 (학습·재사용·이력 기록 가치) |
| Q2 | 저장소 전략 | **새 저장소** 생성, 기존 `_PROJECT_FRAMEWORK` 는 GitHub archive 처리 (삭제 아님) |
| Q3 | scripts 배포 방식 | **A — 프로젝트 로컬 복사** (Git pre-commit 의 팀 협업 안전성 우선) |
| Q4 | 기존 글로벌 커맨드 | 백업 후 즉시 삭제 (완료 — `.bak` 보관) |
| Q5 | 플러그인·저장소 이름 | **`claude-project-bootstrap`** (kebab-case, 기능 명확) |
| Q6 | Generic 화 전략 | 권장안 — 🟢 6건 공개 원칙 / 🟡 5건 내부 changelog / ⚪ 1건 삭제 |

### 구조 선택: Approach 1 (단일 플러그인 + 내장 marketplace)

**채택 근거**:
- 첫 플러그인 = 단순함이 제1가치
- 수요 검증 전 분할은 오버엔지니어링
- `_PROJECT_FRAMEWORK` 의 기능이 이미 상호 의존적 — 쪼개면 의존성 지옥

**고려했던 대안**:
- Approach 2: 3개 하위 플러그인 분할 (scaffold/baseline-harness/code-quality)
- Approach 3: 플러그인 저장소 + 별도 marketplace 저장소

---

## 3. 아키텍처 & 저장소 레이아웃

### 3.1 Claude Code 플러그인 규약 (현재 이해)

플러그인 저장소 루트에 `.claude-plugin/` 폴더 배치:

| 파일 | 역할 |
|---|---|
| `.claude-plugin/plugin.json` | 플러그인 자체 메타데이터 — 이름, 버전, 포함된 commands/hooks/skills 선언 |
| `.claude-plugin/marketplace.json` | Marketplace 메타데이터 — 저장소가 카탈로그 역할 겸할 때 필요 |

단일 저장소가 두 역할 모두 가능. 사용자 설치 절차:
```
claude plugin marketplace add seungjaeyuu/claude-project-bootstrap
claude plugin install claude-project-bootstrap
```

### 3.2 디렉토리 트리

```
claude-project-bootstrap/
├── .claude-plugin/
│   ├── plugin.json              # 플러그인 manifest
│   └── marketplace.json         # marketplace manifest (같은 저장소 겸용)
├── commands/
│   ├── init-project.md          # /init-project 슬래시 커맨드
│   └── baseline-review.md       # /baseline-review 슬래시 커맨드
├── scripts/
│   ├── install-hooks.sh            # 플러그인 내부에서만 실행 (복사 안 됨)
│   ├── baseline_status.py          # /init-project 가 target 프로젝트로 복사
│   ├── baseline_update_suggest.py  # /init-project 가 target 프로젝트로 복사
│   ├── check_baseline_sync.py      # /init-project 가 target 프로젝트로 복사
│   ├── check_accessibility_identifiers.py  # /init-project 가 target 프로젝트로 복사
│   ├── check_dict_duplicates.py    # /init-project 가 target 프로젝트로 복사
│   └── pre-commit-framework.sh     # /init-project 가 target 프로젝트로 복사
├── templates/                   # /init-project 가 target 프로젝트로 복사·치환
│   ├── CLAUDE.md.tmpl
│   ├── INDEX.md.tmpl
│   ├── TESTING_FRAMEWORK.md.tmpl
│   ├── BASELINE.md.tmpl
│   ├── baseline.yml.tmpl
│   ├── settings.json.tmpl
│   └── gitignore.tmpl
├── docs/
│   ├── design-principles.md     # 🟢 D1/D3/D4/D5/D7/D8 generic 화 편입
│   ├── changelog-decisions.md   # 🟡 D2/D6/D9/D10/D11 내부 결정 로그
│   └── migration-guide.md       # 기존 /init-project 사용자용
├── README.md                    # 한국어 본문 + 영문 abstract (상단 3-5줄)
├── LICENSE                      # MIT
├── CHANGELOG.md
└── .gitignore
```

### 3.3 기존 → 신규 파일 매핑

| 기존 | 신규 | 비고 |
|---|---|---|
| `README.md` | `README.md` | 전면 재작성 (플러그인 사용자 시점으로 전환) |
| `CLAUDE_TEMPLATE.md` | `templates/CLAUDE.md.tmpl` | `.tmpl` 확장자로 — 실제 설정 인식 방지 |
| `INDEX_TEMPLATE.md` | `templates/INDEX.md.tmpl` | 동일 |
| `TESTING_FRAMEWORK_TEMPLATE.md` | `templates/TESTING_FRAMEWORK.md.tmpl` | 동일 |
| `BASELINE_TEMPLATE.md` | `templates/BASELINE.md.tmpl` | 동일 |
| `.gitignore.template` | `templates/gitignore.tmpl` | 점 제거 (패키징 안전) |
| `~/.claude/commands/init-project.md.bak` (글로벌 백업) | `commands/init-project.md` | ⚠ 원본이 `_PROJECT_FRAMEWORK` 가 아닌 **글로벌 커맨드**. 백업본에서 이관, 경로 참조를 `${CLAUDE_PLUGIN_ROOT}` 로 치환 |
| `commands/baseline-review.md` | `commands/baseline-review.md` | 동일 |
| `hooks/install-hooks.sh` | `scripts/install-hooks.sh` | scripts/ 로 — hook 설치 도구지 Claude Code hook 아님 |
| `hooks/pre-commit-framework.sh` | `scripts/pre-commit-framework.sh` | 동일 |
| `hooks/settings.json.template` | `templates/settings.json.tmpl` | templates/ 로 재분류 |
| `scripts/*.py` | `scripts/*.py` | 동일 |
| `scripts/baseline.yml.template` | `templates/baseline.yml.tmpl` | templates/ 로 재분류 (설정 템플릿) |
| `docs/DESIGN_DECISIONS.md` | `docs/design-principles.md` (🟢) + `docs/changelog-decisions.md` (🟡) | D1~D12 권장안 분리 |

### 3.4 핵심 설계 결정

1. **`.tmpl` 확장자 통일** — 템플릿 파일이 Claude Code 에 의해 "실제 설정" 으로 오인되지 않도록.
2. **"hook" 용어의 3가지 맥락 분리** — (1) Claude Code PostToolUse hook 은 **target 프로젝트의 `.claude/settings.json`** 에 복사되어 동작 — 플러그인 레벨 전역 hook 을 두지 않음 (프로젝트마다 matcher regex 가 다르므로 전역화 부적합). (2) Git pre-commit hook 은 `scripts/pre-commit-framework.sh` 가 target 프로젝트의 `.git/hooks/pre-commit` 으로 symlink. (3) 이들을 **설치하는** bash 스크립트 `scripts/install-hooks.sh` 는 플러그인 내부에서만 실행. 세 개념 혼동 방지 위해 디렉토리 분리, 플러그인 루트 `hooks/` 는 **두지 않음**.
3. **docs/ 3개 문서로 계층화** — 공개 가치 있는 것 (`design-principles.md`), 내부 결정 로그 (`changelog-decisions.md`), 사용자 마이그레이션 (`migration-guide.md`). README 는 간결 유지.

---

## 4. Generic 화 & 콘텐츠 변환

### 4.1 사적 맥락 변환 규칙 (31건)

| 유형 | 규칙 | 예시 |
|---|---|---|
| **"SunnyWay" 고유명사** | 맥락 따라 삭제 or "실제 프로덕션 프로젝트" 로 치환 | "SunnyWay TESTING_FRAMEWORK.md §13 참조" → 삭제 |
| **구체 사고 날짜+내부 맥락** | 일반화된 리스크 설명으로 재작성. 날짜·Lane명·건수 제거 | "2026-04-14 Lane B Codex 가 ... 303건 중 262건 손실" → "병렬 AI 테스트에서 워커가 자신의 리포트 내 '운영 권고' 를 자율 집행하면 cross-kill 리스크. 실제 사고 사례 존재." |
| **ID 예시** (`PRV-06-R14`, `DEV-066`) | 범용 placeholder | `PRV-06-R14` → `APP-01-R01`, `DEV-066` → `DEV-XXX` |
| **경로 예시** (`sunnyway/apps/...`) | Generic 경로 | `sunnyway/apps/student_app_ios/SunnyWay` → `apps/ios/` |
| **"보호자/가족/학부모" 용어** | 삭제 대신 **교육적 예시로 유지** + 라벨 | "프로젝트 고유 용어 정의 예시 (실제 프로덕션 프로젝트의 경우)" |
| **GitHub PR 번호 / Notion URL** | 삭제 |

### 4.2 파일별 재작성 강도

| 파일 | 강도 | 주요 작업 |
|---|---|---|
| `README.md` | 🔴 전면 재작성 | 플러그인 사용자 시점으로 전환 |
| `templates/CLAUDE.md.tmpl` | 🟡 부분 수정 | 10건 SunnyWay 언급 제거, Lane B 사고 섹션 generic 화 |
| `templates/TESTING_FRAMEWORK.md.tmpl` | 🟡 부분 수정 | 4건 SunnyWay 참조 제거 |
| `templates/BASELINE.md.tmpl` | 🟢 1건만 | `EXAMPLE-S01` → `APP-01-R01` |
| `scripts/baseline_status.py` | 🟢 주석만 | `--help` 예시 `PRV-06-R14` → `APP-01-R01` |
| `scripts/check_accessibility_identifiers.py` | 🟢 주석만 | 경로 예시 generic 화 |
| `docs/design-principles.md` (신규) | 🟢 편집 | 🟢 6건 편입 |
| `docs/changelog-decisions.md` (신규) | 🟢 편집 | 🟡 5건 편입 |

### 4.3 DESIGN_DECISIONS.md 재분류 (D1~D12)

**🟢 `docs/design-principles.md` 로 편입 (6건)** — 공개 설계 원칙:

| ID | 원제 | 편입 형태 |
|---|---|---|
| D1 | 네거티브 우선 + 4층 범례 | 문서 서두 — 이 플러그인의 설계 철학 |
| D3 | 3 Template 규약 (A/B/C) | `BASELINE.md.tmpl` 구조 근거 섹션 |
| D4 | 판정 canonical = status.json | 베이스라인 데이터 모델 섹션 |
| D5 | 이중 배치 지양 + 3계층 발견 | 플러그인 구조 근거 (hook/command/template 분리 이유) |
| D7 | 하네스 도입 = `baseline.yml` entry | `/init-project` 동작 근거 |
| D8 | 트리거 기반 동기화 | `/baseline-review` 커맨드 존재 근거 |

**🟡 `docs/changelog-decisions.md` 로 편입 (5건)** — 내부 결정 로그:

| ID | 원제 | 비고 |
|---|---|---|
| D2 | 섹션 마커 철회 | "왜 없는 기능인지" 역사 기록 |
| D6 | `.claude/rules/` 철폐 + `.secret/` | Claude Code 컨벤션 진화 민감 |
| D9 | 위험 명령 차단 hook 철회 | 공개 논쟁 여지 — 사용자 PR 재논의 가능 |
| D10 | MEMORY.md 프로젝트 단위 | 실증 로그 |
| D11 | 100단어 답변 예외 | Opus 4.7 세대 고유 |

**⚪ 삭제 (1건)**: D12 Markdown 링크 유지 — generic 노하우, 자체 가치 낮음

### 4.4 언어·라이선스

| 항목 | 결정 | 근거 |
|---|---|---|
| 본문 언어 | 한국어 | 저자·주 사용자 모두 한국어 화자 예상. 니치 포지션 차별화 |
| README 영문 | 상단 3~5줄 abstract | 영어권 유입 시 최소 이해. 전면 영문화는 v1.0 이후 |
| 라이선스 | **MIT** | 가장 허용적. 포함된 Python 스크립트 전량 저자 작성이므로 결정 자유 |
| 저작권 | `Copyright (c) 2026 Yu Seungjae (yu.seungjae@gmail.com)` | 공개 이메일이므로 CLAUDE.md 비밀 노출 금지 규칙과 무관 |

### 4.5 "보호자" 용어 처리

**방식**: 삭제하지 않고 "프로젝트 고유 용어 정의의 예시" 로 유지하되 메타 설명 추가.

**변환 예시** (`templates/CLAUDE.md.tmpl`):

```markdown
### 📐 프로젝트 고유 용어 정의 (예시)

모든 프로젝트는 고유한 도메인 용어를 가지며, 팀 안에서 **하나의 용어로 통일** 해야
자동화 도구와 문서가 일관성을 유지할 수 있습니다.

예시 (실제 프로덕션 프로젝트의 경우):
- "보호자" 를 사용, "가족"/"학부모" 금지 — 도메인이 학원 셔틀 서비스
- "배송 건" 을 사용, "주문"/"패키지" 금지 — 도메인이 물류

본인 프로젝트의 도메인 용어를 여기에 명시하세요.
```

의도: "왜 용어 통일이 필요한지" 는 범용 교훈. "보호자" 는 그 교훈을 보여주는 **두 예시 중 하나** 로 격하. 사용자가 실제 자기 도메인 용어로 덮어쓰도록 유도.

---

## 5. 설치·배포·검증

### 5.1 5단계 흐름

```
Stage 1 (로컬 개발) → Stage 2 (GitHub push) → Stage 3 (로컬 검증)
                                                      ↓
                      Stage 5 (기존 저장소 archive) ← Stage 4 (마켓플레이스 공개)
```

| Stage | 작업 | 산출 |
|---|---|---|
| **1. 로컬 개발** | `~/Documents/GitHub/claude-project-bootstrap/` 신규 생성. 섹션 3 디렉토리 트리 + 섹션 4 generic 화 일괄 | 로컬 플러그인 저장소 완성 |
| **2. GitHub push** | `seungjaeyuu/claude-project-bootstrap` (public) 생성. `git init` → initial commit → push | 공개 저장소 live |
| **3. 로컬 검증** | 빈 테스트 디렉토리에서 `claude plugin marketplace add` → `install` → `/init-project` 실행. 5.2 체크리스트 통과 | 동작 검증 완료 |
| **4. 마켓플레이스 공개** | 저장소 public 시점에 marketplace.json 공개 — URL 공유만으로 설치 가능 | 사용자 설치 가능 |
| **5. 기존 저장소 archive** | GitHub `seungjaeyuu/_PROJECT_FRAMEWORK` Settings → Archive. 직전에 README 에 "Moved to X" 노트 추가 | 기존 저장소 read-only |

### 5.2 로컬 검증 체크리스트 (Stage 3)

| # | 검증 항목 | 기대 |
|---|---|---|
| 1 | `claude plugin marketplace add <repo-url>` | marketplace 등록 성공, `claude plugin list` 에 표시 |
| 2 | `claude plugin install claude-project-bootstrap` | 설치 성공, `/init-project` 와 `/baseline-review` 발견 |
| 3 | `/init-project` 최소 질의 (이름·유형·언어만) | `CLAUDE.md`, `INDEX.md`, `.gitignore`, `.secret/.gitkeep` 생성. 플레이스홀더 치환 완료 |
| 4 | `/init-project` + E2E Yes + iOS | `TESTING_FRAMEWORK.md`, `IOS_MASTER_TEST_BASELINE.md`, `scripts/baseline.yml` 생성. `baseline.yml` 에 **iOS entry 만** (타 타입 예시 포함 안 됨) |
| 5 | `/init-project` + E2E Yes + Hook Yes | `.claude/settings.json`, `.git/hooks/pre-commit` symlink, `scripts/check_*.py` + `scripts/baseline_*.py` + `scripts/pre-commit-framework.sh` 복사 완료 (단, `install-hooks.sh` 는 복사 안 됨 — 플러그인 내부 전용) |
| 6 | Swift/Kotlin/TSX 편집 시 | PostToolUse hook 이 `check_accessibility_identifiers.py` 실행. 위반 시 경고 (차단 아님 — D9) |
| 7 | 커밋 시도 | pre-commit 이 `check_baseline_sync.py` + `check_dict_duplicates.py` 실행. UI 수정 + baseline 미갱신 시 경고 |
| 8 | `/baseline-review` 실행 | `baseline_update_suggest.py` 호출, Git diff 분석 결과 출력 |
| 9 | **회귀**: 기존 `CLAUDE.md` 있는 디렉토리에서 `/init-project` | **중단** + 알림 (덮어쓰기 방지) |
| 10 | **정적 검증**: generic 화 누락 | 플러그인 저장소 전체 `grep -r "SunnyWay\|Lane B\|PRV-06\|sunnyway" .` **0건** (보호자는 예시 섹션만 허용) |

### 5.3 버전·태깅

| 버전 | 트리거 |
|---|---|
| **v0.1.0** | 5.2 검증 전체 통과. 본인만 사용. |
| **v0.1.x** | 버그 수정 누적. API 변경 가능. |
| **v0.2.0+** | 첫 외부 피드백 반영. 주요 기능 추가. |
| **v1.0.0** | API 안정화. 공식 커뮤니티 리스트 제출 고려 시점. |

각 릴리즈는 `git tag v0.1.0` + GitHub Releases + `CHANGELOG.md` 반영.

### 5.4 기존 `~/.claude/commands/init-project.md.bak` 최종 처리

- Stage 3 검증 9번 통과 확인 후: `rm ~/.claude/commands/init-project.md.bak`
- 미통과 시: `mv ... init-project.md` 로 원복 후 플러그인 재작업

### 5.5 🚫 주의 사항

- **현재 작업 디렉토리는 SunnyWay worktree** — 플러그인 저장소는 **별도 위치** (`~/Documents/GitHub/claude-project-bootstrap/`) 생성. SunnyWay 워크트리에 섞이면 안 됨.
- **기존 `~/Documents/GitHub/_PROJECT_FRAMEWORK/` 는 읽기만** (참조용). archive 대상이므로 파일 수정 금지.
- **`git reset --hard` 는 Stage 5 archive 준비에서만 허용** (사용자 이번 한정 승인). 플러그인 저장소 초기화는 `git init` 으로 깨끗하게.

---

## 6. 불확실 항목 (구현 단계에서 확인)

본 설계는 Claude Code 플러그인 규약에 대한 **부분적 지식** 에 기반함. 다음은 `plugin-dev:plugin-structure`, `plugin-dev:command-development`, `plugin-dev:hook-development` skill 을 통해 구현 단계에서 재확인:

| # | 항목 | 영향 |
|---|---|---|
| 1 | `plugin.json` 스키마 (commands/hooks/skills 선언 방식) | commands/*.md 가 자동 발견되는지 vs plugin.json 에 명시해야 하는지 |
| | ✅ **확인 (2026-04-23, plugin-dev:plugin-structure)**: 필수 필드 `name` 만 (kebab-case). 권장: `version`, `description`, `author{name,email,url}`, `homepage`, `repository`, `license`, `keywords`. **자동 발견**: `commands/*.md`, `agents/*.md`, `skills/*/SKILL.md`, `hooks/hooks.json`, `.mcp.json` 모두 auto-discovery. plugin.json 의 `commands`/`agents`/`hooks` 필드는 path override (supplement, not replace) 용도. → **plugin.json 에 commands 배열 명시 불필요**. |
| 2 | `marketplace.json` 의 플러그인 등록 형식 | 저장소 URL, 이름, 버전 필드 규약 |
| | ✅ **확인 (2026-04-23, 실제 예시 Notion/superpowers)**: 루트 필드 `name`, `description`(옵션), `owner`(name+email/url), `plugins`(배열). 플러그인 entry 필드 `name`, `description`, `version`, `source`, `author`, `homepage`. **같은 저장소 플러그인은 `"source": "./"`** (superpowers 예시). `category` 필드는 공식 예시에 없음 — 우리 draft 에서 제거 필요. |
| 3 | 플러그인 hook vs settings.json hook 실제 동작 차이 | PostToolUse 가 플러그인 범위에서 자동 트리거되는지, 사용자가 opt-in 해야 하는지 |
| | ✅ **확인 (2026-04-23, plugin-dev:hook-development)**: **플러그인 hook (`hooks/hooks.json`)** 은 `{"hooks":{...events...}}` wrapper. **Target 프로젝트 (`.claude/settings.json`)** 도 동일 wrapper. 우리 기존 `settings.json.template` 구조 그대로 OK. **우리 설계 결정 재확인**: 플러그인 레벨 hook 은 두지 않음 (프로젝트마다 matcher regex 다름), target 프로젝트 `.claude/settings.json` 만 사용. Phase 3 에서 `hooks/` 디렉토리 안 만듦. |
| 4 | `${CLAUDE_PLUGIN_ROOT}` 가 커맨드·hook 파일에서 해석되는 맥락 | `/init-project` 내부에서 이 변수가 bash 컨텍스트·Claude 프롬프트 컨텍스트 어디서 resolve 되는지 |
| | ✅ **확인 (2026-04-23)**: 환경 변수. hook 실행 시 bash 셸에 노출. MCP server args·component files 에서 사용 가능. 플러그인 설치 위치로 runtime resolve. `/init-project` 본문의 `cp ${CLAUDE_PLUGIN_ROOT}/templates/...` 같은 bash 명령에서 정상 치환됨. → 계획상 경로 치환 방식 그대로 진행 가능. |
| 5 | 커맨드 네임스페이스 (`/init-project` vs `/claude-project-bootstrap:init-project`) | 공존 정책 |
| | ✅ **확인 (2026-04-23, plugin-dev:command-development)**: 플러그인 커맨드는 **`/init-project` 그대로** 노출 (prefix 강제 없음). `/help` 에서만 `(claude-project-bootstrap)` 라벨 붙음. 기존 글로벌 `~/.claude/commands/init-project.md.bak` 과 충돌 가능 — 백업 파일이 활성 상태가 아니므로 OK (이미 Phase 4 단계에서 백업으로 이동 완료). |

**추가 발견 (frontmatter 필드)**:
- 슬래시 커맨드 frontmatter: `description`, `allowed-tools`, `model`, `argument-hint`, `disable-model-invocation`
- 우리 `init-project.md.bak` 은 `description`·`argument-hint` 만 설정 → **`allowed-tools` 필드 추가 필요** (bash cp/mkdir/Edit/Read 권한). Phase 5 Task 5.1 에 반영.
- Bash 실행 구문: `` !`bash_command` ``. `${CLAUDE_PLUGIN_ROOT}` 를 직접 사용 가능.
- 파일 포함 구문: `@${CLAUDE_PLUGIN_ROOT}/path/to/file`.

**추가 발견 (계획 조정 필요)**:
- `templates/` 는 Claude Code 플러그인 **표준 디렉토리 아님** (하지만 보조 파일로 허용). auto-discovery 대상 아니므로 우리 설계의 `/init-project` 가 명시적으로 복사하는 방식과 호환.
- 모든 컴포넌트 디렉토리는 **플러그인 루트** 에 위치. `.claude-plugin/` 안에 넣으면 안 됨 (이미 우리 설계는 이 규약 준수).
- 컴포넌트 파일·디렉토리 **kebab-case** 강제. 우리 파일명 (`init-project.md`, `claude-project-bootstrap`) 모두 준수.

---

## 7. 공식 커뮤니티 리스트 대응

**결론: 필수 아님.**

현재 이해하는 Claude Code 플러그인 배포 모델:
- **Decentralized marketplace** — 각 GitHub 공개 저장소 자체가 marketplace
- `claude plugin marketplace add <github-url>` 로 누구나 등록 가능
- Stage 4 (GitHub public) 시점에 실질 공개 배포 완료

Anthropic 이 "추천 플러그인 리스트" 를 운영할 수는 있지만 **거기 등록 여부와 무관하게** URL 만 알면 설치 가능. 본인 블로그·SNS·README 공유로 배포 완료. **v1.0.0 시점에 재검토**.

---

## 8. 성공 기준

- ✅ 5.2 검증 체크리스트 10항목 전부 통과
- ✅ `seungjaeyuu/claude-project-bootstrap` (public) live
- ✅ 플러그인 저장소 전체 generic 화 완료 (정적 grep 0건)
- ✅ `seungjaeyuu/_PROJECT_FRAMEWORK` archive 처리
- ✅ `docs/design-principles.md`, `docs/changelog-decisions.md`, `docs/migration-guide.md` 작성
- ✅ README 에 설치·사용법 1회 시도로 성공 가능할 만큼 명확

---

## 9. 참조

- **기존 저장소**: https://github.com/seungjaeyuu/_PROJECT_FRAMEWORK
- **원본 DESIGN_DECISIONS.md**: `~/Documents/GitHub/_PROJECT_FRAMEWORK/docs/DESIGN_DECISIONS.md`
- **선행 대화**: 2026-04-21~22 (네거티브 우선 설계 개편 세션)
- **글로벌 CLAUDE.md 정리**: 2026-04-23 (본 세션에서 `_PROJECT_FRAMEWORK` 참조 2건 제거)

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-04-23 | 초판 — 브레인스토밍 Q1~Q6 + 섹션 A/B/C 승인 결과 통합 |
