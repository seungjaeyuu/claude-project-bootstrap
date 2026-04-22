---
description: 새 프로젝트 초기화 — 네거티브 우선 원칙 + 베이스라인 하네스 스캐폴드
argument-hint: (선택 없음 — 대화형 질의)
allowed-tools: Read, Write, Edit, Bash(cp:*), Bash(mkdir:*), Bash(touch:*), Bash(cat:*), Bash(chmod:*), Bash(ln:*), Bash(git:*), Bash(bash:*), Bash(test:*), Bash(ls:*), Bash(rm:*)
---

# /init-project — 새 프로젝트 초기화

`claude-project-bootstrap` 플러그인을 사용해 현재 작업 디렉토리를 프로젝트로 초기화.

## 전제 조건 확인

1. 현재 디렉토리에 `CLAUDE.md` 가 **이미 있으면 중단** 하고 사용자에게 알림 (재초기화 옵션 3가지 제시).
2. `${CLAUDE_PLUGIN_ROOT}/docs/design-principles.md` 를 먼저 Read — 설계 원칙 확인.

---

## 대화형 질의 (최소 필수 → 선택 순서)

### 필수 (반드시 답변)

1. **프로젝트 이름** (예: MyNewApp)
2. **프로젝트 유형**:
   - (a) 단일 웹 (Next.js / Vite / React)
   - (b) 단일 모바일 (SwiftUI / Flutter / Kotlin Compose)
   - (c) 모노레포 (웹 + 모바일 + 백엔드)
   - (d) 백엔드·서버
   - (e) 기타
3. **주요 언어·프레임워크** (자유 답변)
4. **Git 저장소 원격 URL** (선택, 생략 가능)

### 선택 옵션 (Y/N, 기본 N)

각 옵션의 **무엇인지 / 언제 필요한지 / 생성 파일 / 기본 N 이유** 를 함께 제시하고 Y/N 받기.

---

#### Q1. E2E 테스트 프레임워크 도입? (기본: N)

- **무엇인지**: AI 워커 (Codex/Claude) 로 End-to-End 테스트를 자동화하는 하네스. 테스트 항목을 `baseline` 파일로 관리.
- **언제**: 사용자 흐름 (로그인 → 장바구니 → 결제 등) 을 반복 검증하고 싶을 때.
- **생성**: `TESTING_FRAMEWORK.md` + `{APP}_MASTER_TEST_BASELINE.md` + `scripts/baseline.yml` (총 ~400줄)
- **기본 N 이유**: 초기 프로젝트는 단위·통합 테스트로 충분. UI flow 복잡해진 후 도입 권장.

---

#### Q2. Firebase / Supabase / BaaS 사용? (기본: N)

- **무엇인지**: Backend-as-a-Service (Firebase/Supabase/Amplify 등) 보안 규칙의 "default deny" 안내 섹션 추가.
- **언제**: 서버리스 백엔드에 의존하는 앱. **실제 SDK 설치는 별개** — 이 옵션은 CLAUDE.md 에 보안 섹션 + `.env.example` 초안 추가만.
- **생성**: CLAUDE.md 에 보안 규칙 섹션 + `.env.example` 초안
- **기본 N 이유**: BaaS 미사용 프로젝트에는 불필요한 섹션.

---

#### Q3. Hook 자동 설치? (기본: N)

- **무엇인지**: 두 종류 hook 자동 설치 — (1) Claude Code **PostToolUse** (`.claude/settings.json`), (2) **Git pre-commit** (`.git/hooks/pre-commit` symlink).
- **언제**: Swift/Kotlin/TypeScript 편집 시 accessibility 검증, 커밋 시 dict 중복 검사 자동화.
- **생성**: `.claude/settings.json`, `.git/hooks/pre-commit` symlink, `scripts/check_*.py` + `baseline_*.py` 6개 복사
- **기본 N 이유**: Q1 N 이면 baseline 체크가 의미 없음. Q1 Yes 권장 시 함께 Yes.
- **주의**: Q1 N 인데 Q3 Yes 면 pre-commit 에 의미 없는 `check_baseline_sync.py` 가 돌아 경고 노이즈 발생.

---

#### Q4. Accessibility identifier 검증? (기본: N, **UI 앱 한정**)

- **무엇인지**: SwiftUI Button/TextField 등에 `.accessibilityIdentifier()` 를 **엄격한 스키마** (`{feature}_{screen}_{element}_{type}`) 로 강제하는 검증.
- **언제**: iOS SwiftUI 앱 + AI E2E 테스트 조합. 이 경우 UI 탐색이 identifier 기반이라 스키마 위반 시 테스트 실패.
- **적용 대상**: SwiftUI (iOS), Kotlin Compose (Android). **Next.js/웹/Flutter 는 해당 없음**.
- **생성**: `ACCESSIBILITY_IDENTIFIERS.md` 카탈로그 템플릿 + `scripts/check_accessibility_identifiers.py` (Q3 Yes 시 이미 복사되므로 중복 방지)
- **기본 N 이유**: 웹·백엔드·Flutter 는 무관. **iOS/Android + Q1 Yes** 조합일 때 Yes 권장.

---

#### Q5. 개발 백로그 관리? (기본: N)

- **무엇인지**: 개발 백로그를 **인덱스(`/개발예정사항.md`) + 상세(`개발예정사항_상세/DEV-XXX.md`)** 2계층으로 구조화. 항목당 1줄 요약 + 상세 링크.
- **언제**: 프로젝트가 성장해 todo 가 수십 개 이상 쌓일 때. 초기엔 GitHub Issues 나 Notion 으로 충분.
- **생성**: `/개발예정사항.md` + `개발예정사항_상세/` 디렉토리 + `DEV-001.md` 샘플
- **기본 N 이유**: 초기 프로젝트에는 과잉 구조. GitHub Issues 로 시작 권장.

---

## 실행 절차

답변을 받은 후:

### Step 1: tier 결정

Q1~Q5 답변을 기준으로 **CLAUDE.md tier** 선택:

| 조건 | Tier | 사용 템플릿 |
|---|---|---|
| Q1~Q5 **모두 N** | **Minimal** | `${CLAUDE_PLUGIN_ROOT}/templates/CLAUDE.minimal.md.tmpl` (~97줄) |
| Q1 Yes 또는 Q3 Yes 또는 Q4 Yes 또는 Q5 Yes | **Full** | `${CLAUDE_PLUGIN_ROOT}/templates/CLAUDE.md.tmpl` (~298줄). 불필요 섹션 삭제. |

### Step 2: CLAUDE.md 복사·치환

```bash
# Minimal tier
cp ${CLAUDE_PLUGIN_ROOT}/templates/CLAUDE.minimal.md.tmpl ./CLAUDE.md

# 또는 Full tier
cp ${CLAUDE_PLUGIN_ROOT}/templates/CLAUDE.md.tmpl ./CLAUDE.md
```

- `[프로젝트명]`, `YYYY-MM-DD` 플레이스홀더 실제 값으로 치환
- Full tier 경우 Q2/Q4 등 No 옵션에 해당하는 섹션 삭제

### Step 3: INDEX.md + .gitignore

```bash
cp ${CLAUDE_PLUGIN_ROOT}/templates/INDEX.md.tmpl ./INDEX.md
cp ${CLAUDE_PLUGIN_ROOT}/templates/gitignore.tmpl ./.gitignore
```

- INDEX.md: 프로젝트 이름·구조 반영
- .gitignore: 언어별 섹션 중 해당되는 것만 주석 해제

### Step 4: Q1 Yes 시 E2E 설정

**4-1. 추가 질의 — 하네스 대상 앱 타입 (복수 선택)**:

```
Q1a. 어떤 앱 타입?
 1) iOS 단일 (SwiftUI)
 2) Android 단일 (Kotlin Compose)
 3) Web (Next.js / React / Vite)
 4) Flutter (mobile / desktop)
 5) 서버·백엔드 (API)
```

**💡 스마트 제안**: iOS 또는 Android 선택 시 Q4 (Accessibility ID 검증) 도 권장하겠습니까? (따로 Yes 받기)

**4-2. TESTING_FRAMEWORK + BASELINE 복사**:

```bash
cp ${CLAUDE_PLUGIN_ROOT}/templates/TESTING_FRAMEWORK.md.tmpl ./TESTING_FRAMEWORK.md

# 선택한 각 타입마다:
cp ${CLAUDE_PLUGIN_ROOT}/templates/BASELINE.md.tmpl ./<TYPE_UPPER>_MASTER_TEST_BASELINE.md
# <APP_NAME> 플레이스홀더 치환
```

**4-3. `scripts/baseline.yml` 동적 생성 (heredoc)**:

선택한 타입에 맞는 entry 만 기록 — 불필요한 예시 미포함.

타입별 필드:

| 타입 | baseline | status_dir | ui_file_patterns | runner_field | platform |
|---|---|---|---|---|---|
| iOS | `IOS_MASTER_TEST_BASELINE.md` | `docs/ios/testing_harness/run` | `'apps/ios/.*\.swift$'` | `udid` | `ios_simulator` |
| Android | `ANDROID_MASTER_TEST_BASELINE.md` | `docs/android/testing_harness/run` | `'apps/android/.*\.kt$'` | `device_id` | `android_emulator` |
| Web | `WEB_MASTER_TEST_BASELINE.md` | `docs/web/testing_harness/run` | `'apps/web/.*\.(tsx\|ts)$'` | `browser` | `web` |
| Flutter | `FLUTTER_MASTER_TEST_BASELINE.md` | `docs/flutter/testing_harness/run` | `'lib/.*\.dart$'` | `device_id` | `flutter` |
| Backend | `BACKEND_MASTER_TEST_BASELINE.md` | `docs/backend/testing_harness/run` | `'src/.*\.(py\|ts\|go)$'` | `endpoint` | `backend` |

**4-4. 디렉토리 생성**:

```bash
# 선택한 각 타입마다:
mkdir -p docs/<app>/testing_harness/run && touch docs/<app>/testing_harness/run/.gitkeep
```

**4-5. Python 스크립트 복사**:

`install-hooks.sh` 가 처리하므로 Q3 Yes 면 자동. Q3 N 이면 수동:

```bash
cp ${CLAUDE_PLUGIN_ROOT}/scripts/baseline_status.py ./scripts/
cp ${CLAUDE_PLUGIN_ROOT}/scripts/baseline_update_suggest.py ./scripts/
cp ${CLAUDE_PLUGIN_ROOT}/scripts/check_baseline_sync.py ./scripts/
```

### Step 5: Q3 Yes 시 Hook 설치

```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/install-hooks.sh
```

### Step 6: Q4 Yes 시 Accessibility 검증

```bash
# install-hooks.sh 가 이미 복사했으면 skip
cp ${CLAUDE_PLUGIN_ROOT}/scripts/check_accessibility_identifiers.py ./scripts/ 2>/dev/null || true
```

`ACCESSIBILITY_IDENTIFIERS.md` 는 프로젝트별 카탈로그이므로 **수동 작성** (플랫폼별 UI 컴포넌트 구조에 따라 다름).

### Step 7: Q5 Yes 시 백로그 구조

```bash
mkdir -p 개발예정사항_상세
cat > 개발예정사항.md <<'EOF'
# 개발예정사항

| ID | 상태 | 제목 | 상세 |
|---|---|---|---|
| DEV-001 | 🟡 대기 | (샘플) | [상세](개발예정사항_상세/DEV-001.md) |
EOF
# DEV-001.md 샘플도 생성
```

### Step 8: `.secret/` 초기화

```bash
mkdir -p .secret && touch .secret/.gitkeep
```

### Step 9: Git 초기화 (원격 URL 제공 시)

```bash
git init && git add . && git commit -m "chore: initialize from claude-project-bootstrap"
git remote add origin <URL>  # push 는 사용자 판단
```

---

## 완료 리포트 (3블록 구조)

실행 후 사용자에게 다음 형식으로 보고:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 초기화 완료

📦 생성된 파일
   (실제 생성된 파일 목록 — 절대경로 아닌 상대경로)

⚙  1개만 확인하세요
   (hook 설치 사용자만 해당)
   scripts/baseline.yml 과 .claude/settings.json 의 ui_file_patterns / matcher regex
   → 기본값은 'apps/ios/.*\.swift$' 같은 통상 경로
   → 실제 프로젝트 구조 다르면 두 파일 같은 패턴으로 수정

🛠  프로젝트별 추가 작업 (플러그인 범위 밖)
   • Xcode/Next.js/Flutter 등 실제 프로젝트 스캐폴드
   • Git 원격 설정 (필요 시)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 원칙

- **사용자 Yes 한 옵션만** 파일 생성. 미선택 옵션의 파일은 만들지 말 것.
- **기존 파일 덮어쓰기 금지** (이미 `CLAUDE.md` 가 있으면 중단 + 3가지 복구 옵션 제시).
- **커밋은 사용자 승인 후**. 자동으로 커밋하지 말 것.
- **tier 결정 로직**: Q1~Q5 모두 N 이면 Minimal, 하나라도 Yes 면 Full.

## 참조

- 플러그인 설계 원칙: `${CLAUDE_PLUGIN_ROOT}/docs/design-principles.md`
- 마이그레이션 가이드: `${CLAUDE_PLUGIN_ROOT}/docs/migration-guide.md`
