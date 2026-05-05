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

---

#### Q0. Bash 권한 단계 — 1개 선택

Claude Code 의 Bash 명령 자동 실행 정책을 결정합니다. `.claude/settings.json` 의 `permissions` 키에 반영.

| 단계 | 한 줄 요약 | 사용자 체감 예시 |
|---|---|---|
| **(1) YOLO** | 거의 모든 Bash 자동. 파괴 명령(`rm -rf`, `git reset --hard`, `git push --force` to main, `firebase deploy`, DB drop)만 deny | "프로토타입 빨리 돌리고 싶고, 위험 명령은 안 쓸게" |
| **(2) Standard** *(권장)* | 읽기·일반 빌드 명령 자동, 파일 삭제·git 변경·deploy·패키지 변경·DB 마이그레이션은 ask | 보통 작업은 끊김 없이, 위험 명령에서만 한 번 묻기 |
| **(3) Strict** | 읽기 전용(`ls`, `cat`, `git status`, `git diff` 등)만 자동. 그 외 ask | "Claude 가 뭘 할 때마다 일단 보고 싶음" / 보안 민감 |
| **(4) None** | `permissions` 키 자체 미생성 — Claude Code 기본 동작 | "기본값으로 충분, 직접 안 건드림" |

**ask vs deny 원칙**: 롤백 가능 = ask, 롤백 불가 = deny. 모든 단계의 deny 리스트가 일관 적용.

선택값(1-4)을 받아 Step 0 에서 `.claude/settings.json` 에 머지 (None 이면 머지 생략).

---

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

##### Q2a. (Q2 == Yes 시) 어떤 백엔드?

  1. Firebase
  2. Supabase
  3. AWS Amplify
  4. 기타

##### Q2b. (Q2a == 1 Firebase 시) Firebase project ID?

예: `aidea-prod`. 이 ID 로 `.firebaserc` 자동 생성 + `firebase.json` predeploy hook 자동 등록 + `scripts/check_firebase_project.py` 복사 → 다른 프로젝트로 잘못 deploy 되는 사고 차단.

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

### Step 0: Bash permission 머지 (Q0 답변 따라)

Q0 답변에 따라 `.claude/settings.json` 의 `permissions` 키 머지:

```bash
mkdir -p .claude

# Q0 == 1 (YOLO)
cp ${CLAUDE_PLUGIN_ROOT}/templates/permissions/yolo.json .claude/settings.json

# Q0 == 2 (Standard)
cp ${CLAUDE_PLUGIN_ROOT}/templates/permissions/standard.json .claude/settings.json

# Q0 == 3 (Strict)
cp ${CLAUDE_PLUGIN_ROOT}/templates/permissions/strict.json .claude/settings.json

# Q0 == 4 (None) — 파일 미생성
```

**Q4 (Accessibility hook) 와 머지 정책**: Step 6 에서 Q4 Yes 시 `templates/settings.json.tmpl` 의 `hooks` 키가 같은 파일에 머지. Step 0 의 `permissions` 키와 Step 6 의 `hooks` 키는 별개 키이므로 충돌 없음. Q0 == None + Q4 == No 이면 `.claude/settings.json` 자체 미생성.

머지 시 기존 `_comment_*` 키는 Step 0 의 파일 생성 후 머지가 일어날 때 보존 (Claude Code 가 unknown 키를 무시).

### Step 1: tier 결정

Q1~Q5 답변을 기준으로 **CLAUDE.md tier** 선택:

| 조건 | Tier | 사용 템플릿 |
|---|---|---|
| Q1~Q5 **모두 N** | **Minimal** | `${CLAUDE_PLUGIN_ROOT}/templates/CLAUDE.minimal.md.tmpl` (~97줄) |
| Q1/Q2/Q3/Q4/Q5 중 하나라도 Yes | **Full** | `${CLAUDE_PLUGIN_ROOT}/templates/CLAUDE.md.tmpl` (120줄, 영역별 RULES 분리). |

### Step 2: CLAUDE.md 복사·치환

```bash
# Minimal tier
cp ${CLAUDE_PLUGIN_ROOT}/templates/CLAUDE.minimal.md.tmpl ./CLAUDE.md

# 또는 Full tier
cp ${CLAUDE_PLUGIN_ROOT}/templates/CLAUDE.md.tmpl ./CLAUDE.md
```

- `[프로젝트명]`, `YYYY-MM-DD` 플레이스홀더 실제 값으로 치환
- Full tier 경우 §Discovery 트리거 표 행을 Q1~Q4 답변에 따라 활성/삭제 (예: Q1 N 이면 RULES_E2E 행 삭제)
- Q2 == Yes + Q2a == 1 (Firebase) 인 경우 Step 4a 에서 본체에 §NEW Firebase 격리 3줄 추가

### Step 2a: Full tier 시 영역별 RULES 복사

Full tier 일 때만 (Minimal 이면 RULES 0개 복사 — `${CLAUDE_PLUGIN_ROOT}/docs/specs/2026-05-05-v0.2.0-permissions-and-doc-slimming-design.md` §5.5/§7.3 정책).

```bash
mkdir -p docs/rules

# 항상 복사 (Full tier 면)
cp ${CLAUDE_PLUGIN_ROOT}/templates/rules/RULES_TERMINOLOGY.md.tmpl docs/rules/RULES_TERMINOLOGY.md
cp ${CLAUDE_PLUGIN_ROOT}/templates/rules/RULES_REFACTORING.md.tmpl docs/rules/RULES_REFACTORING.md

# Q1 Yes 시
cp ${CLAUDE_PLUGIN_ROOT}/templates/rules/RULES_E2E.md.tmpl docs/rules/RULES_E2E.md

# Q2 Yes 시
cp ${CLAUDE_PLUGIN_ROOT}/templates/rules/RULES_DATA_INTEGRITY.md.tmpl docs/rules/RULES_DATA_INTEGRITY.md

# Q4 Yes 시
cp ${CLAUDE_PLUGIN_ROOT}/templates/rules/RULES_ACCESSIBILITY.md.tmpl docs/rules/RULES_ACCESSIBILITY.md

# Q3 Yes 또는 Q4 Yes 시
cp ${CLAUDE_PLUGIN_ROOT}/templates/rules/RULES_DICT_DUPLICATES.md.tmpl docs/rules/RULES_DICT_DUPLICATES.md
```

복사하지 않은 RULES 에 대응하는 §Discovery 표 행은 Step 2 의 CLAUDE.md 에서 삭제.

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

### Step 4a: Q2 Yes + Q2a == Firebase 시 Firebase 격리 설정

Q2 Yes + Q2a == 1 (Firebase) 인 경우만 실행. Q2b 에서 받은 project ID 를 `<FB_PROJECT_ID>` 라 한다.

**4a-1. `.firebaserc` 생성**:

```bash
cat > .firebaserc <<EOF
{
  "projects": {
    "default": "<FB_PROJECT_ID>"
  }
}
EOF
```

**4a-2. `firebase.json` predeploy hook 등록**:

기존 `firebase.json` 가 있으면 4개 영역(functions/hosting/firestore/storage)의 `predeploy` 키만 머지. 없으면 minimal 생성:

```bash
cp ${CLAUDE_PLUGIN_ROOT}/templates/firebase.json.tmpl ./firebase.json
```

(기존 파일 머지 케이스는 사용자 confirm 후 수동 머지 또는 jq 활용. 자세한 머지 로직은 `migrate_diagnose.py` 가 향후 사용 시 처리.)

**4a-3. 검증 스크립트 복사**:

```bash
mkdir -p scripts
cp ${CLAUDE_PLUGIN_ROOT}/scripts/check_firebase_project.py ./scripts/
chmod +x ./scripts/check_firebase_project.py
```

**4a-4. CLAUDE.md 본체에 §NEW Firebase 격리 inline (3줄)**:

Step 2 에서 복사한 `CLAUDE.md` 의 §변경이력 직전에 다음 3줄 삽입:

```markdown
## NEW. 🚫 Firebase 프로젝트 격리 (project: <FB_PROJECT_ID>)

- `firebase deploy` 단독 호출 금지. 반드시 `--project <FB_PROJECT_ID>` 명시
- 사용자에게 deploy 명령 안내 시 `--project` 명시 형태로 제공
- predeploy hook 이 활성 프로젝트와 `.firebaserc` 일치를 자동 검증
```

**4a-5. INDEX.md 에 직접 실행 체크리스트 추가**:

Step 3 에서 복사한 `INDEX.md` 끝(변경 이력 직전)에 다음 추가:

```markdown
## Firebase deploy (직접 실행 체크리스트)

터미널 직접 deploy 시 1초 검증:
1. `cat .firebaserc` → `projects.default` 가 `<FB_PROJECT_ID>` 인지 확인
2. `firebase deploy --project <FB_PROJECT_ID> --only <services>`
```

**4a-6. 글로벌 캐시 검증** (init 1회):

```bash
# ~/.config/configstore/firebase-tools.json 의 activeProjects 키에서
# 현재 init 디렉토리(절대경로)의 매핑 검사. 다른 ID 매핑 시 경고.
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check_firebase_project.py --init-check "<FB_PROJECT_ID>"
```

스크립트가 mismatch 발견 시 stderr 경고 출력, init 자체는 계속 진행.

### Step 5: Q3 Yes 시 Hook 설치 (Git pre-commit + 검증 스크립트 복사)

```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/install-hooks.sh
```

`install-hooks.sh` 는 **Git pre-commit hook** 과 **검증 스크립트들** 만 설치합니다. Claude Code PostToolUse hook (`.claude/settings.json`) 은 Q4 답변에 따라 Step 6 에서 조건부 설치.

### Step 6: Q4 Yes 시 Claude Code PostToolUse hook 설치

Q4 Yes 인 경우에만 `.claude/settings.json` 복사 (AX 검증 자동화):

```bash
# Q4 Yes 시만 실행
mkdir -p .claude
cp ${CLAUDE_PLUGIN_ROOT}/templates/settings.json.tmpl ./.claude/settings.json
```

이 hook 은 Edit/Write/MultiEdit 직후 `apps/.*\.(swift|kt|tsx)$` 파일에 대해 `scripts/posttooluse_ax_check.py` 를 호출합니다 (Python wrapper — Claude Code stdin JSON 스펙 준수).

**Q4 No 인 경우** `.claude/settings.json` 자체를 생성하지 않음 — AX 검증이 무의미한 프로젝트에 hook 을 두면 노이즈.

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

⚙  확인이 필요한 항목

   (hook 설치 사용자만 해당)
   scripts/baseline.yml 과 .claude/settings.json 의 ui_file_patterns / matcher regex
   → 기본값은 'apps/ios/.*\.swift$' 같은 통상 경로
   → 실제 프로젝트 구조 다르면 두 파일 같은 패턴으로 수정

   (Q2 == Firebase 사용자만 해당)
   Firebase 격리 확인:
   • .firebaserc default: <FB_PROJECT_ID>
   • firebase login 계정: (실행 시 firebase login:list 결과)
   • 글로벌 캐시 의심 여부: (4a-6 의 검증 결과 — OK 또는 경고)
   • 첫 deploy 전 권장: firebase use <FB_PROJECT_ID> (1회)

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
- **Minimal tier 는 RULES 0개 복사** (분리 RULES 사용 안 함). §Discovery 표도 Minimal 본체에 미수록.
- **Q0 == None + Q4 == No**: `.claude/settings.json` 자체 생성 안 함. 그 외 조합은 머지 대상.

## 참조

- 플러그인 설계 원칙: `${CLAUDE_PLUGIN_ROOT}/docs/design-principles.md`
- 마이그레이션 가이드: `${CLAUDE_PLUGIN_ROOT}/docs/migration-guide.md`
