---
description: 새 프로젝트 초기화 — 네거티브 우선 원칙 + 베이스라인 하네스 스캐폴드
argument-hint: (선택 없음 — 대화형 질의)
allowed-tools: Read, Write, Edit, Bash(cp:*), Bash(mkdir:*), Bash(touch:*), Bash(cat:*), Bash(chmod:*), Bash(ln:*), Bash(git:*), Bash(bash:*), Bash(test:*), Bash(ls:*), Bash(rm:*)
---

# /init-project — 새 프로젝트 초기화

`claude-project-bootstrap` 플러그인을 사용해 현재 작업 디렉토리를 프로젝트로 초기화.

## 전제 조건 확인

1. 현재 디렉토리에 `CLAUDE.md` 가 **이미 있으면 중단** 하고 사용자에게 알림.
2. `${CLAUDE_PLUGIN_ROOT}/docs/design-principles.md` 를 먼저 Read — 설계 원칙 확인.

## 대화형 질의 (최소 필수 → 선택 순서)

### 필수 (반드시 답변)

1. **프로젝트 이름** (예: MyNewApp)
2. **프로젝트 유형** — 다음 중 하나:
   - 단일 웹 (Next.js / Vite / 기타)
   - 단일 모바일 (SwiftUI / Flutter / Kotlin Compose)
   - 모노레포 (웹 + 모바일 + 백엔드)
   - 백엔드·서버 (API, Cloud Functions 등)
   - 기타
3. **주요 언어·프레임워크** (자유 답변)
4. **Git 저장소 원격 URL** (선택, 생략 가능)

### 선택 (Yes/No, 기본 No)

| # | 옵션 | Yes 선택 시 생성 |
|---|---|---|
| Q1 | E2E 테스트 프레임워크 필요? | `TESTING_FRAMEWORK.md` + `{APP}_MASTER_TEST_BASELINE.md` + `scripts/baseline.yml` |
| Q2 | Firebase / Supabase / BaaS 사용? | 보안 규칙 default deny 섹션 + `.env.example` 초안 |
| Q3 | Hook 자동 설치? | `install-hooks.sh` 실행 → `.claude/settings.json` + pre-commit |
| Q4 | Accessibility identifier 검증? (UI 앱 한정) | `ACCESSIBILITY_IDENTIFIERS.md` + 관련 스크립트 |
| Q5 | 개발 백로그 관리? | `/개발예정사항.md` + `개발예정사항_상세/` |

## 실행 절차

답변을 받은 후:

1. **CLAUDE.md 복사·치환**
   - `cp ${CLAUDE_PLUGIN_ROOT}/templates/CLAUDE.md.tmpl ./CLAUDE.md`
   - `[프로젝트명]`, `[프레임워크]` 플레이스홀더 실제 값으로 치환
   - 해당하지 않는 섹션 삭제 (예: 모바일 없으면 모바일 규칙 제거)

2. **INDEX.md 생성**
   - `cp ${CLAUDE_PLUGIN_ROOT}/templates/INDEX.md.tmpl ./INDEX.md`
   - 프로젝트 이름·구조 반영

3. **.gitignore 초기화**
   - `cp ${CLAUDE_PLUGIN_ROOT}/templates/gitignore.tmpl ./.gitignore`
   - 언어별 섹션 중 해당되는 것만 주석 해제

4. **Q1 Yes 면** (E2E 테스트 프레임워크):

   **4-1. 추가 질의 — 하네스 대상 앱 타입**

   ```
   Q1a. 어떤 앱 타입의 하네스를 구축합니까? (복수 선택 가능)
     1) iOS 단일 (SwiftUI)
     2) Android 단일 (Kotlin Compose)
     3) Web (Next.js / React / Vite)
     4) Flutter (mobile 또는 desktop)
     5) 서버·백엔드 (API 테스트)
   ```

   **4-2. TESTING_FRAMEWORK · BASELINE 복사**
   - `cp ${CLAUDE_PLUGIN_ROOT}/templates/TESTING_FRAMEWORK.md.tmpl ./TESTING_FRAMEWORK.md`
   - 선택한 각 타입마다:
     - `cp ${CLAUDE_PLUGIN_ROOT}/templates/BASELINE.md.tmpl ./<TYPE_UPPER>_MASTER_TEST_BASELINE.md`
     - `<APP_NAME>` 플레이스홀더를 타입 이름으로 치환

   **4-3. `scripts/baseline.yml` 동적 생성 (heredoc)**

   `cp` 대신 선택한 타입에 맞는 entry 를 **heredoc 으로 직접 기록**. 불필요한 예시는 **포함하지 않음** (자동 맞춤).

   각 타입별 사전 정의 필드:

   | 타입 | baseline | status_dir | ui_file_patterns | runner_field | platform |
   |---|---|---|---|---|---|
   | iOS | `IOS_MASTER_TEST_BASELINE.md` | `docs/ios/testing_harness/run` | `'apps/ios/.*\.swift$'` 또는 프로젝트 경로 | `udid` | `ios_simulator` |
   | Android | `ANDROID_MASTER_TEST_BASELINE.md` | `docs/android/testing_harness/run` | `'apps/android/.*\.kt$'` | `device_id` | `android_emulator` |
   | Web | `WEB_MASTER_TEST_BASELINE.md` | `docs/web/testing_harness/run` | `'apps/web/.*\.(tsx\|ts)$'` | `browser` | `web` |
   | Flutter | `FLUTTER_MASTER_TEST_BASELINE.md` | `docs/flutter/testing_harness/run` | `'lib/.*\.dart$'` | `device_id` | `flutter` |
   | Backend | `BACKEND_MASTER_TEST_BASELINE.md` | `docs/backend/testing_harness/run` | `'src/.*\.(py\|ts\|go)$'` | `endpoint` | `backend` |

   예시 — 사용자가 iOS 만 선택:

   ```bash
   mkdir -p scripts
   cat > scripts/baseline.yml <<'EOF'
   # 프로젝트 베이스라인 설정
   # /init-project 가 자동 생성 — 수동 편집 시 규약 준수

   default_app: ios

   apps:
     ios:
       baseline: IOS_MASTER_TEST_BASELINE.md
       status_dir: docs/ios/testing_harness/run
       ui_file_patterns:
         - 'apps/ios/.*\.swift$'
       exclude_prefixes: [BUG]
       runner_field: udid
       platform: ios_simulator
   EOF
   ```

   사용자가 **iOS + Android 모노레포** 선택 시 `apps:` 아래 두 entry 모두 기록. `default_app` 은 사용자에게 추가 질의 (둘 중 주 타입).

   **4-4. 디렉토리 · .gitkeep**
   - 선택한 각 타입마다 `mkdir -p docs/<app>/testing_harness/run && touch docs/<app>/testing_harness/run/.gitkeep`

   **4-5. 스크립트 복사** — `install-hooks.sh` 가 처리하므로 Q3 Yes 면 자동 (아니면 수동):
   - `cp ${CLAUDE_PLUGIN_ROOT}/scripts/baseline_status.py ./scripts/`
   - `cp ${CLAUDE_PLUGIN_ROOT}/scripts/baseline_update_suggest.py ./scripts/`
   - `cp ${CLAUDE_PLUGIN_ROOT}/scripts/check_baseline_sync.py ./scripts/`

   **4-6. `ui_file_patterns` 검증**
   - 스모크 테스트: `python3 scripts/baseline_status.py --summary` 가 에러 없이 실행되는지
   - 사용자에게 "실제 UI 파일 경로가 `ui_file_patterns` regex 와 맞는지 확인하세요" 안내

5. **Q3 Yes 면**:
   - `bash ${CLAUDE_PLUGIN_ROOT}/scripts/install-hooks.sh` 실행

6. **Q4 Yes 면**:
   - `cp ${CLAUDE_PLUGIN_ROOT}/scripts/check_accessibility_identifiers.py ./scripts/` (install-hooks.sh 가 이미 복사했으면 skip)
   - `ACCESSIBILITY_IDENTIFIERS.md` 는 프로젝트별 카탈로그로 수동 정의 (UI 컴포넌트 구조에 따라 다름)

7. **.secret/ 폴더 초기화**
   - `mkdir -p .secret && touch .secret/.gitkeep`

8. **Git 초기화** (원격 URL 제공 시):
   - `git init && git add . && git commit -m "chore: initialize from claude-project-bootstrap"`
   - `git remote add origin <URL>`
   - push 여부는 사용자 판단에 맡김

## 보고

완료 후 사용자에게:
- 생성된 파일 목록
- 수동 치환 필요한 플레이스홀더 목록
- 다음 단계 안내 (예: "`scripts/baseline.yml` 의 `ui_file_patterns` 를 실제 UI 경로로 수정하세요")

## 원칙

- **사용자 Yes 한 옵션만** 파일 생성. 미선택 옵션의 파일은 만들지 말 것.
- **기존 파일 덮어쓰기 금지** (이미 `CLAUDE.md` 가 있으면 중단).
- **커밋은 사용자 승인 후**. 자동으로 커밋하지 말 것.

## 참조

- 플러그인 설계 원칙: `${CLAUDE_PLUGIN_ROOT}/docs/design-principles.md`
- 마이그레이션 가이드: `${CLAUDE_PLUGIN_ROOT}/docs/migration-guide.md`
