---
description: Initialize a project — negative-first principle + context-optimization scaffold — 프로젝트 초기화 + 설정 변경
argument-hint: (선택 없음 — 대화형 질의) 또는 --bash | --firebase | --slim | --hook | --plugins
allowed-tools: Read, Write, Edit, Bash(cp:*), Bash(mkdir:*), Bash(touch:*), Bash(cat:*), Bash(chmod:*), Bash(ln:*), Bash(git:*), Bash(bash:*), Bash(test:*), Bash(ls:*), Bash(rm:*)
---

# /init — 프로젝트 초기화 + 설정 변경

`claude-project-bootstrap` 플러그인을 사용해 현재 작업 디렉토리를 프로젝트로 초기화.

## 직접 옵션 호출

| 호출 | 동작 | 기존 커맨드 호환 |
|---|---|---|
| `/init` | 메뉴 표시 (신규면 전체 흐름, 기존이면 설정 변경 메뉴) | `/init-project` |
| `/init --bash` | Bash 권한 변경 직행 | `/bash-permission` |
| `/init --firebase` | Firebase 격리 직행 | `/firebase-isolation` |
| `/init --slim` | CLAUDE.md 슬림화 직행 | `/slim-claude-md` |
| `/init --hook` | 문서 크기 hook 직행 | `/doc-size-hook` |
| `/init --plugins` | 플러그인 최적화 직행 | (신규) |

옵션 없이 호출 시 → 아래 전제 조건 확인부터 시작.

---

## 전제 조건 확인

1. `${CLAUDE_PLUGIN_ROOT}/docs/design-principles.md` 를 먼저 Read — 설계 원칙 확인.
2. 현재 디렉토리에 `CLAUDE.md` 존재 여부 확인 → 분기:

### CLAUDE.md 미존재 → 신규 초기화 (아래 대화형 질의 진행)

### CLAUDE.md 존재 → 설정 변경 메뉴

```
CLAUDE.md가 이미 존재합니다.

1) 처음부터 재초기화 (기존 파일 _backup/ 후 새로 생성)
2) 설정 변경:
   a) Bash 권한 단계 변경
   b) Firebase 격리 도입/변경
   c) CLAUDE.md 슬림화 + RULES 분리
   d) 문서 크기 hook 도입
   e) 플러그인 최적화 (enabledPlugins)
3) 취소
```

1 선택 시: 기존 CLAUDE.md, INDEX.md, docs/rules/ 를 `_backup/` 폴더로 이동 후 신규 초기화 흐름 진행.
2a~2e 선택 시: 해당 기능만 단독 실행 (아래 각 Step 참조).
3 선택 시: 중단.

---

## 대화형 질의 (신규 초기화)

### 필수 (반드시 답변, 3개)

1. **프로젝트 이름** (예: MyNewApp)
2. **프로젝트 유형**:
   - (a) 단일 웹 (Next.js / Vite / React)
   - (b) 단일 모바일 (SwiftUI / Flutter / Kotlin Compose)
   - (c) 모노레포 (웹 + 모바일 + 백엔드)
   - (d) 백엔드·서버
   - (e) 기타
3. **주요 언어·프레임워크** (자유 답변)

---

#### Q0. Bash 권한 단계 — 1개 선택

Claude Code 의 Bash 명령 자동 실행 정책. `.claude/settings.json` 의 `permissions` 키에 반영.

| 단계 | 한 줄 요약 |
|---|---|
| **(1) YOLO** | 거의 모든 Bash 자동. 파괴 명령만 deny |
| **(2) Standard** *(권장)* | 읽기·빌드 자동. 삭제·git 변경·deploy 는 ask |
| **(3) Strict** | 읽기 전용만 자동. 그 외 ask |
| **(4) None** | `permissions` 미생성 — Claude Code 기본 동작 |

---

#### Q1. E2E 테스트 프레임워크 도입? (기본: N)

- **무엇**: AI 워커로 End-to-End 테스트를 자동화하는 하네스. 테스트 항목을 `baseline` 파일로 관리.
- **생성**: `docs/test/TESTING_FRAMEWORK.md` + `docs/test/baseline/{APP}_BASELINE.md` + `scripts/`
- **기본 N 이유**: 초기 프로젝트는 단위·통합 테스트로 충분.

##### Q1 == Yes 시 하위 질의:

**Q1a. 어떤 앱 타입?** (복수 선택)
1. iOS 단일 (SwiftUI)
2. Android 단일 (Kotlin Compose)
3. Web (Next.js / React / Vite)
4. Flutter (mobile / desktop)
5. 서버·백엔드 (API)

**Q1b. Hook 자동 설치?** (기본: Y — 스마트 제안)
- Git pre-commit + Claude Code PostToolUse hook 자동 설치.
- **기본 Y 이유**: Q1 Yes 면 baseline 검증·dict 중복 검사가 유의미.

**Q1c. Accessibility identifier 검증?** (기본: Y — iOS/Android 선택 시만 표시)
- SwiftUI/Kotlin Compose 의 AX identifier 스키마 강제.
- **표시 조건**: Q1a 에서 iOS 또는 Android 선택 시만.

---

#### Q2. BaaS 사용? (기본: N)

- **무엇**: Backend-as-a-Service 보안 규칙의 "default deny" 안내 + `.env.example` 초안.
- **기본 N 이유**: BaaS 미사용 프로젝트에 불필요.

##### Q2 == Yes 시 하위 질의:

**Q2a.** 어떤 백엔드? (Firebase / Supabase / AWS Amplify / 기타)
**Q2b.** (Firebase 시) project ID? (예: `appfoo-prod`)

---

#### Q3. 개발 백로그 관리? (기본: N)

- **무엇**: 개발 백로그를 **인덱스(`TASK.md`) + 상세(`tasks/DEV-XXX.md`)** 2계층 구조화.
- **기본 N 이유**: 초기엔 GitHub Issues 로 충분.

---

**질의 수**: 필수 3 + Q0~Q3 = **최소 4회, 최대 8회**.

---

## 실행 절차

### Step 0: Bash permission 머지

Q0 답변에 따라 `.claude/settings.json` 생성:

```bash
mkdir -p .claude

# Q0 == 1 (YOLO)
cp ${CLAUDE_PLUGIN_ROOT}/templates/permissions/yolo.json .claude/settings.json

# Q0 == 2 (Standard)
cp ${CLAUDE_PLUGIN_ROOT}/templates/permissions/standard.json .claude/settings.json

# Q0 == 3 (Strict)
cp ${CLAUDE_PLUGIN_ROOT}/templates/permissions/strict.json .claude/settings.json

# Q0 == 4 (None) — 생성 생략
```

Q1b (Hook) Yes 시 Step 4b 에서 `hooks` 키가 같은 파일에 머지됨. `permissions` 와 `hooks` 는 별개 키이므로 충돌 없음.

### Step 1: tier 결정

| 조건 | Tier | 템플릿 |
|---|---|---|
| Q1~Q3 **모두 N** | **Minimal** | `CLAUDE.minimal.md.tmpl` (~67줄) |
| Q1/Q2/Q3 중 하나라도 Yes | **Full** | `CLAUDE.md.tmpl` (~94줄) |

### Step 2: CLAUDE.md 복사·치환

```bash
# Minimal tier
cp ${CLAUDE_PLUGIN_ROOT}/templates/CLAUDE.minimal.md.tmpl ./CLAUDE.md

# 또는 Full tier
cp ${CLAUDE_PLUGIN_ROOT}/templates/CLAUDE.md.tmpl ./CLAUDE.md
```

- `[프로젝트명]`, `YYYY-MM-DD` 플레이스홀더를 실제 값으로 치환
- Full tier: §3 발견 트리거 표 행을 Q1~Q3 답변에 따라 활성/삭제

### Step 2a: Full tier 시 영역별 RULES 복사

```bash
mkdir -p docs/rules

# 항상 복사 (Full tier 면)
cp ${CLAUDE_PLUGIN_ROOT}/templates/rules/RULES_TERMINOLOGY.md.tmpl docs/rules/RULES_TERMINOLOGY.md
cp ${CLAUDE_PLUGIN_ROOT}/templates/rules/RULES_REFACTORING.md.tmpl docs/rules/RULES_REFACTORING.md
cp ${CLAUDE_PLUGIN_ROOT}/templates/rules/RULES_VERSIONING.md.tmpl docs/rules/RULES_VERSIONING.md
cp ${CLAUDE_PLUGIN_ROOT}/templates/rules/RULES_PROJECT_LIFECYCLE.md.tmpl docs/rules/RULES_PROJECT_LIFECYCLE.md

# Q1 Yes 시
cp ${CLAUDE_PLUGIN_ROOT}/templates/rules/RULES_E2E.md.tmpl docs/rules/RULES_E2E.md

# Q2 Yes 시
cp ${CLAUDE_PLUGIN_ROOT}/templates/rules/RULES_DATA_INTEGRITY.md.tmpl docs/rules/RULES_DATA_INTEGRITY.md

# Q1c Yes 시 (Accessibility)
cp ${CLAUDE_PLUGIN_ROOT}/templates/rules/RULES_ACCESSIBILITY.md.tmpl docs/rules/RULES_ACCESSIBILITY.md

# Q1b Yes 시 (Hook — dict 중복 검사 포함)
cp ${CLAUDE_PLUGIN_ROOT}/templates/rules/RULES_DICT_DUPLICATES.md.tmpl docs/rules/RULES_DICT_DUPLICATES.md
```

### Step 3: INDEX.md + .gitignore + .claudeignore + commands + docs/ + apps/

```bash
# 핵심 파일
cp ${CLAUDE_PLUGIN_ROOT}/templates/INDEX.md.tmpl ./INDEX.md
cp ${CLAUDE_PLUGIN_ROOT}/templates/gitignore.tmpl ./.gitignore
cp ${CLAUDE_PLUGIN_ROOT}/templates/claudeignore.tmpl ./.claudeignore

# .claude/commands/ 기본 3개
mkdir -p .claude/commands
cp ${CLAUDE_PLUGIN_ROOT}/templates/commands/build.md.tmpl ./.claude/commands/build.md
cp ${CLAUDE_PLUGIN_ROOT}/templates/commands/check.md.tmpl ./.claude/commands/check.md
cp ${CLAUDE_PLUGIN_ROOT}/templates/commands/status.md.tmpl ./.claude/commands/status.md

# docs/ 표준 폴더 (7개)
mkdir -p docs/summary docs/error docs/event docs/cost-plan docs/handoff docs/test docs/rules
touch docs/summary/.gitkeep docs/error/.gitkeep docs/event/.gitkeep
touch docs/cost-plan/.gitkeep docs/handoff/.gitkeep

# apps/ 플랫폼 폴더 (프로젝트 유형에 따라)
# (a) 단일 웹
mkdir -p apps/web

# (b) 단일 모바일 SwiftUI
mkdir -p apps/ios

# (b) 단일 모바일 Kotlin
mkdir -p apps/android

# (b) 단일 모바일 Flutter
mkdir -p apps/flutter

# (c) 모노레포 — 선택한 플랫폼 전부 + shared
mkdir -p apps/shared

# (d) 백엔드
mkdir -p apps/server  # 또는 src/
```

- INDEX.md: 프로젝트 이름·구조 반영, apps/ 구조 업데이트
- .gitignore: 언어별 섹션 중 해당되는 것만 주석 해제
- .claudeignore: 프로젝트 유형에 맞는 섹션 주석 해제 (iOS/Android/Web/Flutter)
- .claude/commands/build.md: 프로젝트 유형에 맞는 빌드 명령으로 치환

### Step 4: Q1 Yes 시 E2E 설정

**4-1. 테스트 문서 복사** (경로: docs/test/):

```bash
cp ${CLAUDE_PLUGIN_ROOT}/templates/TESTING_FRAMEWORK.md.tmpl ./docs/test/TESTING_FRAMEWORK.md

# 선택한 각 타입마다:
mkdir -p docs/test/baseline
cp ${CLAUDE_PLUGIN_ROOT}/templates/BASELINE.md.tmpl ./docs/test/baseline/<TYPE_UPPER>_BASELINE.md
# <APP_NAME> 플레이스홀더 치환
```

**4-2. `scripts/baseline.yml` 동적 생성**:

선택한 타입에 맞는 entry 만 기록. 경로는 v0.3.0 형식 사용:

| 타입 | baseline | status_dir |
|---|---|---|
| iOS | `docs/test/baseline/IOS_BASELINE.md` | `docs/test/result/ios` |
| Android | `docs/test/baseline/ANDROID_BASELINE.md` | `docs/test/result/android` |
| Web | `docs/test/baseline/WEB_BASELINE.md` | `docs/test/result/web` |
| Flutter | `docs/test/baseline/FLUTTER_BASELINE.md` | `docs/test/result/flutter` |
| Backend | `docs/test/baseline/BACKEND_BASELINE.md` | `docs/test/result/backend` |

**4-3. 디렉토리 생성**:

```bash
# 선택한 각 타입마다:
mkdir -p docs/test/result/<app> && touch docs/test/result/<app>/.gitkeep
mkdir -p docs/test/feedback && touch docs/test/feedback/.gitkeep
```

**4-4. Python 스크립트 복사**:

```bash
mkdir -p scripts
cp ${CLAUDE_PLUGIN_ROOT}/scripts/baseline_status.py ./scripts/
cp ${CLAUDE_PLUGIN_ROOT}/scripts/baseline_update_suggest.py ./scripts/
cp ${CLAUDE_PLUGIN_ROOT}/scripts/check_baseline_sync.py ./scripts/
```

### Step 4b: Q1b Yes 시 Hook 설치

```bash
# Git pre-commit hook
bash ${CLAUDE_PLUGIN_ROOT}/scripts/install-hooks.sh

# Claude Code PostToolUse hook — settings.json 에 hooks 키 머지
# Q1c Yes 시 AX 검증 hook 도 포함
mkdir -p .claude
# settings.json 이 이미 있으면 hooks 키만 머지, 없으면 새로 생성
```

Q1c Yes (Accessibility) 시:
```bash
cp ${CLAUDE_PLUGIN_ROOT}/scripts/posttooluse_ax_check.py ./scripts/
# .claude/settings.json 의 hooks.PostToolUse 에 AX 검증 hook 추가
```

### Step 4c: Q2 Yes + Firebase 시 Firebase 격리

Q2a == Firebase 이고 Q2b 에서 받은 project ID 를 `<FB_PROJECT_ID>` 라 한다.

```bash
# .firebaserc 생성
cat > .firebaserc <<EOF
{
  "projects": {
    "default": "<FB_PROJECT_ID>"
  }
}
EOF

# firebase.json predeploy hook
cp ${CLAUDE_PLUGIN_ROOT}/templates/firebase.json.tmpl ./firebase.json

# 검증 스크립트
mkdir -p scripts
cp ${CLAUDE_PLUGIN_ROOT}/scripts/check_firebase_project.py ./scripts/
chmod +x ./scripts/check_firebase_project.py

# CLAUDE.md 에 Firebase 격리 섹션 (3줄) 삽입 — §변경이력 직전
# INDEX.md 에 직접 실행 체크리스트 추가

# 글로벌 캐시 검증
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check_firebase_project.py --init-check "<FB_PROJECT_ID>"
```

### Step 5: Q3 Yes 시 백로그 구조

```bash
mkdir -p tasks
cp ${CLAUDE_PLUGIN_ROOT}/templates/task.md.tmpl ./TASK.md
cp ${CLAUDE_PLUGIN_ROOT}/templates/task-detail.md.tmpl ./tasks/DEV-001.md
# YYYY-MM-DD 치환
```

### Step 6: `.secret/` 초기화

```bash
mkdir -p .secret && touch .secret/.gitkeep
```

### Step 7: Git 초기화 (선택)

사용자에게 Git 초기화 여부 확인 후:

```bash
git init && git add . && git commit -m "chore: initialize from claude-project-bootstrap"
# 원격 URL 제공 시: git remote add origin <URL>
# push 는 사용자 승인 후
```

---

## 완료 리포트

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 초기화 완료

📦 생성된 파일
   (실제 생성된 파일 목록 — 상대경로)

🔌 플러그인 추천 (프로젝트 타입 기반)
   ✅ firebase — 이미 활성
   💡 frontend-design — UI 폴리싱 시 활성화 권장
   💡 security-guidance — 출시 전 /release 실행 시 활성화 권장
   ℹ️ figma — Figma 디자인 연동 시 활성화

⚙  확인이 필요한 항목
   (조건부 — hook 설치 시 regex 확인, Firebase 시 격리 확인 등)

🛠  프로젝트별 추가 작업 (플러그인 범위 밖)
   • 실제 앱 스캐폴드 (Xcode/Next.js/Flutter 등)
   • Git 원격 설정 (선택)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 플러그인 추천 로직

| 프로젝트 유형 | 추천 플러그인 |
|---|---|
| 웹 (Next.js) | `vercel`, `frontend-design` |
| 모바일 (iOS/Android) | `frontend-design` |
| Firebase 사용 | `firebase` |
| 모든 프로젝트 | `superpowers` (상시), `security-guidance` (출시 전) |
| Figma 연동 시 | `figma` |

---

## 원칙

- **사용자 Yes 한 옵션만** 파일 생성. 미선택 옵션의 파일은 만들지 말 것.
- **기존 파일 덮어쓰기 금지** (CLAUDE.md 존재 시 설정 변경 메뉴 제시).
- **커밋은 사용자 승인 후**. 자동으로 커밋하지 말 것.
- **tier 결정 로직**: Q1~Q3 모두 N 이면 Minimal, 하나라도 Yes 면 Full.
- **Minimal tier 는 RULES 0개 복사**. §Discovery 트리거 표도 미수록.
- **Q0 == None + Q1b == No**: `.claude/settings.json` 자체 생성 안 함 (commands/ 는 생성).
- **.claudeignore 는 항상 생성** — 프로젝트 유형에 맞는 섹션 활성화.
- **.claude/commands/ 는 항상 생성** — build, check, status 기본 3개.
- **docs/ 표준 폴더 항상 생성** — summary, error, event, cost-plan, handoff, test, rules.
- **apps/ 폴더는 프로젝트 유형에 따라** 생성.

## 참조

- 플러그인 설계 원칙: `${CLAUDE_PLUGIN_ROOT}/docs/design-principles.md`
- 마이그레이션 가이드: `${CLAUDE_PLUGIN_ROOT}/docs/migration-guide.md`
- 프로젝트 라이프사이클: `docs/rules/RULES_PROJECT_LIFECYCLE.md` (Full tier)
