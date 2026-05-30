---
description: 프로젝트 초기화 + 설정 변경 (네거티브 우선 + 컨텍스트 최적화 스캐폴드)
argument-hint: (선택 없음 — 대화형 질의) 또는 --bash | --firebase | --slim | --hook | --plugins | --seo
allowed-tools: Read, Write, Edit, Bash(cp:*), Bash(mkdir:*), Bash(touch:*), Bash(cat:*), Bash(chmod:*), Bash(ln:*), Bash(git:*), Bash(bash:*), Bash(test:*), Bash(ls:*), Bash(rm:*)
---

# /kickoff — 프로젝트 초기화 + 설정 변경

`claude-project-bootstrap` 플러그인을 사용해 현재 작업 디렉토리를 프로젝트로 초기화.

## 직접 옵션 호출

| 호출 | 동작 | 기존 커맨드 호환 |
|---|---|---|
| `/kickoff` | 메뉴 표시 (신규면 전체 흐름, 기존이면 설정 변경 메뉴) | `/init`, `/init-project` |
| `/kickoff --bash` | Bash 권한 변경 직행 | `/bash-permission` |
| `/kickoff --firebase` | Firebase 격리 직행 | `/firebase-isolation` |
| `/kickoff --slim` | CLAUDE.md 슬림화 직행 | `/slim-claude-md` |
| `/kickoff --hook` | 문서 크기 hook 직행 | `/doc-size-hook` |
| `/kickoff --plugins` | 플러그인 최적화 직행 | (신규) |
| `/kickoff --seo` | SEO + GEO 가이드라인 도입 직행 | `/seo-setup` |

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
   f) SEO + GEO 가이드라인 도입
3) 취소
```

1 선택 시: 기존 CLAUDE.md, INDEX.md, docs/rules/ 를 `_backup/` 폴더로 이동 후 신규 초기화 흐름 진행.
2a~2f 선택 시: 해당 기능만 단독 실행 (2f SEO + GEO 는 `/seo-setup` 커맨드 실행).
3 선택 시: 중단.

---

## 대화형 질의 (신규 초기화)

### 필수 (반드시 답변, 3개)

1. **프로젝트 이름** (예: MyNewApp)
2. **프로젝트 유형**:
   - (a) 단일 웹 (Next.js / Vite / React)
   - (b) 단일 네이티브 앱 (모바일·데스크톱: SwiftUI / AppKit / Flutter / Kotlin Compose)
   - (c) 모노레포 (웹 + 모바일 + 백엔드)
   - (d) 백엔드·서버
   - (e) 기타
3. **주요 언어·프레임워크** (자유 답변)

#### 유형 후속 (유형 b·c 선택 시만): 네이티브 플랫폼 — 복수 선택

`apps/<platform>` 생성·build/check 빌드 명령·`RULES_MACOS_RELEASE` 트리거를 **결정론적으로** 정하기 위해, 자유 답변(언어) 추론 대신 명시적으로 묻는다 (Swift/SwiftUI 는 iOS·macOS 공통이라 추론 불가).

- **유형 (b) 단일 네이티브 앱**: 1) iOS (SwiftUI)  2) macOS (SwiftUI/AppKit)  3) Android (Kotlin Compose)  4) Flutter (mobile/desktop)
- **유형 (c) 모노레포**: 위 1~4 + Web (Next.js/React/Vite) / 백엔드 (복수)
- **유형 (a)**: Web 고정 · **(d)**: 백엔드 고정 · **(e)**: 자유 답변으로 판단 (질의 생략)

이 답변(이하 **플랫폼 답변**)이 Step 2b·Step 3·Q1a·Q1c 분기의 기준이다.

---

#### Q0. Bash 권한 단계 — 1개 선택

Claude Code 의 Bash 명령 자동 실행 정책. `.claude/settings.json` 의 `permissions` 키에 반영.

| 단계 | 한 줄 요약 | 사용자 체감 예시 |
|---|---|---|
| **(1) YOLO** | 거의 모든 Bash 자동. 파괴 명령(`rm -rf`, `git reset --hard`, `git push --force` to main, DB drop)만 deny | "프로토타입 빨리 돌리고 싶고, 위험 명령은 안 쓸게" |
| **(2) Standard** *(권장)* | 읽기·일반 빌드 명령 자동, 파일 삭제·git 변경·deploy·패키지 변경·DB 마이그레이션은 ask | 보통 작업은 끊김 없이, 위험 명령에서만 한 번 묻기 |
| **(3) Strict** | 읽기 전용(`ls`, `cat`, `git status`, `git diff` 등)만 자동. 그 외 ask | "Claude 가 뭘 할 때마다 일단 보고 싶음" / 보안 민감 |
| **(4) None** | `permissions` 키 자체 미생성 — Claude Code 기본 동작 | "기본값으로 충분, 직접 안 건드림" |

**ask vs deny 원칙**: 롤백 가능 = ask, 롤백 불가 = deny. 모든 단계의 deny 리스트가 일관 적용.

---

#### Q1. E2E 테스트 프레임워크 도입? (기본: N)

- **무엇**: AI 워커로 End-to-End 테스트를 자동화하는 하네스. 테스트 항목을 `baseline` 파일로 관리.
- **언제**: 사용자 흐름(로그인·결제 등)을 반복 검증하고 싶을 때.
- **생성**: `docs/test/TESTING_FRAMEWORK.md` + `docs/test/baseline/{APP}_BASELINE.md` + `scripts/`
- **기본 N 이유**: 초기 프로젝트는 단위·통합 테스트로 충분.

##### Q1 == Yes 시 하위 질의:

**Q1a. 어떤 앱 타입?** (복수 선택)
- **유형 (b)/(c) 에서 플랫폼 답변을 이미 받았으면 그 목록을 기본값으로 재사용** — E2E 대상만 좁히면 됨(재질문 생략). 유형 (a)→Web, (d)→서버·백엔드 자동.
- 그 외(유형 e 등)에서만 아래에서 선택:
1. iOS 단일 (SwiftUI)
2. Android 단일 (Kotlin Compose)
3. Web (Next.js / React / Vite)
4. Flutter (mobile / desktop)
5. 서버·백엔드 (API)
6. macOS (SwiftUI/AppKit)

**Q1b. Hook 자동 설치?** (기본: Y — 스마트 제안)
- Git pre-commit + Claude Code PostToolUse hook 자동 설치.
- **기본 Y 이유**: Q1 Yes 면 baseline 검증·dict 중복 검사가 유의미.

**Q1c. Accessibility identifier 검증?** (기본: Y — iOS/Android/macOS 선택 시만 표시)
- SwiftUI/Kotlin Compose 의 AX identifier 스키마 강제.
- **표시 조건**: **플랫폼 답변**에 iOS·Android·macOS 포함 시 (Q1a 단독이 아니라 통합 플랫폼 답변 기준).

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

#### Q4. 웹 SEO + GEO 가이드라인 적용? (기본: N, **웹 프로젝트 권장**)

- **무엇**: 랜딩 페이지 HTML 의 메타 태그·구조·구조화 데이터를 14개 항목으로 자동 검증 + LLM 검색엔진(ChatGPT, Perplexity 등) 최적화(GEO) 포함. pre-commit hook 으로 커밋 차단.
- **언제**: 검색 엔진 노출이 필요한 웹 사이트/랜딩 페이지.
- **생성**: `SEO_GUIDELINE.md` + `scripts/check_seo.py` + `docs/rules/RULES_SEO.md` + `docs/rules/RULES_GEO.md`
- **기본 N 이유**: 백엔드·모바일·내부 도구에는 불필요.
- **💡 스마트 제안**: Q4 Yes 시 Q1b (Hook 설치) 도 Yes 권장 — pre-commit 자동 검증 활성화.

##### Q4 == Yes 시 하위 질의:

**Q4a.** 랜딩 페이지 HTML 경로? (예: `index.html`, `public/index.html`)
**Q4b.** 사이트 URL? (선택, 생략 가능. 예: `https://example.com/`)

---

**질의 수**: 필수 3 (+ 유형 b/c 시 플랫폼 1) + Q0~Q4 = **최소 4회, 최대 11회**.

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
| Q1~Q4 **모두 N** | **Minimal** | `CLAUDE.minimal.md.tmpl` (~67줄) |
| Q1~Q4 중 하나라도 Yes | **Full** | `CLAUDE.md.tmpl` (~94줄) |

### Step 2: CLAUDE.md 복사·치환

```bash
# Minimal tier
cp ${CLAUDE_PLUGIN_ROOT}/templates/CLAUDE.minimal.md.tmpl ./CLAUDE.md

# 또는 Full tier
cp ${CLAUDE_PLUGIN_ROOT}/templates/CLAUDE.md.tmpl ./CLAUDE.md
```

- `[프로젝트명]`, `YYYY-MM-DD` 플레이스홀더를 실제 값으로 치환
- Full tier: §3 발견 트리거 표 행을 Q1~Q4 답변에 따라 활성/삭제

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

# Q4 Yes 시 (SEO + GEO)
cp ${CLAUDE_PLUGIN_ROOT}/templates/rules/RULES_SEO.md.tmpl docs/rules/RULES_SEO.md
cp ${CLAUDE_PLUGIN_ROOT}/templates/rules/RULES_GEO.md.tmpl docs/rules/RULES_GEO.md

# (macOS 배포 가드레일은 tier 무관 — Step 2b 에서 별도 처리)
```

### Step 2b: macOS 배포 가드레일 (tier 무관)

**플랫폼 답변에 macOS 포함 시**, Minimal/Full 무관하게 실행. `RULES_MACOS_RELEASE` 는 🚫 가드레일급(공증 없는 배포·hardened runtime·ad-hoc 서명·서명키 커밋 = 롤백 불가 피해)이라 Git·시크릿 가드레일과 동급으로 tier 무관 제공한다.

```bash
mkdir -p docs/rules
cp ${CLAUDE_PLUGIN_ROOT}/templates/rules/RULES_MACOS_RELEASE.md.tmpl docs/rules/RULES_MACOS_RELEASE.md
```

- **Full tier**: `CLAUDE.md` §3 발견 트리거 표에 codesign/notarytool/dmg 행이 이미 있으므로 추가 작업 없음.
- **Minimal tier**: §발견 트리거 표가 없으므로, 복사한 `CLAUDE.md` 의 `## 📎 참조` 섹션 맨 위에 발견 포인터 1줄을 주입:
  `- 🚫 macOS 서명·공증·배포(codesign/notarytool/dmg) 작업 시: docs/rules/RULES_MACOS_RELEASE.md 먼저 read (배포 가드레일).`

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

# (b) 단일 네이티브 앱 — iOS (SwiftUI)
mkdir -p apps/ios

# (b) 단일 네이티브 앱 — Android (Kotlin)
mkdir -p apps/android

# (b) 단일 네이티브 앱 — Flutter
mkdir -p apps/flutter

# (b) 단일 네이티브 앱 — macOS (SwiftUI/AppKit)
mkdir -p apps/macos

# (c) 모노레포 — 선택한 플랫폼 전부 + shared
mkdir -p apps/shared

# (d) 백엔드
mkdir -p apps/server  # 또는 src/
```

- INDEX.md: 프로젝트 이름·구조 반영, apps/ 구조 업데이트
- .gitignore: 언어별 섹션 중 해당되는 것만 주석 해제
- .claudeignore: 프로젝트 유형에 맞는 섹션 주석 해제 (iOS/Android/macOS/Web/Flutter)
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

| 타입 | baseline | status_dir | ui_file_patterns | runner_field | platform |
|---|---|---|---|---|---|
| iOS | `docs/test/baseline/IOS_BASELINE.md` | `docs/test/result/ios` | `'apps/ios/.*\.swift$'` | `udid` | `ios_simulator` |
| Android | `docs/test/baseline/ANDROID_BASELINE.md` | `docs/test/result/android` | `'apps/android/.*\.kt$'` | `device_id` | `android_emulator` |
| Web | `docs/test/baseline/WEB_BASELINE.md` | `docs/test/result/web` | `'apps/web/.*\.(tsx\|ts)$'` | `browser` | `web` |
| Flutter | `docs/test/baseline/FLUTTER_BASELINE.md` | `docs/test/result/flutter` | `'lib/.*\.dart$'` | `device_id` | `flutter` |
| Backend | `docs/test/baseline/BACKEND_BASELINE.md` | `docs/test/result/backend` | `'src/.*\.(py\|ts\|go)$'` | `endpoint` | `backend` |
| macOS | `docs/test/baseline/MACOS_BASELINE.md` | `docs/test/result/macos` | `'apps/macos/.*\.swift$'` | `bundle_id` | `macos` |

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
# 기존 firebase.json 가 있으면 4개 영역(functions/hosting/firestore/storage)의
# predeploy 키만 머지. 없으면 minimal 생성:
cp ${CLAUDE_PLUGIN_ROOT}/templates/firebase.json.tmpl ./firebase.json
# (기존 파일 머지 케이스는 사용자 confirm 후 jq 활용)

# 검증 스크립트
mkdir -p scripts
cp ${CLAUDE_PLUGIN_ROOT}/scripts/check_firebase_project.py ./scripts/
chmod +x ./scripts/check_firebase_project.py

# CLAUDE.md 에 Firebase 격리 섹션 (3줄) 삽입 — §변경이력 직전
# INDEX.md 에 직접 실행 체크리스트 추가

# 글로벌 캐시 검증
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check_firebase_project.py --init-check "<FB_PROJECT_ID>"
```

### Step 4d: Q4 Yes 시 SEO + GEO 설정

Q4a 에서 받은 HTML 경로 = `<HTML_PATH>`, Q4b 의 사이트 URL = `<SITE_URL>`.

```bash
# SEO_GUIDELINE.md 복사·치환
cp ${CLAUDE_PLUGIN_ROOT}/templates/SEO_GUIDELINE.md.tmpl ./SEO_GUIDELINE.md
# [HTML_PATH], [SITE_URL], YYYY-MM-DD 치환. Q4b 생략 시 [SITE_URL] 유지.

# check_seo.py 복사
mkdir -p scripts
cp ${CLAUDE_PLUGIN_ROOT}/scripts/check_seo.py ./scripts/check_seo.py
chmod +x ./scripts/check_seo.py

# CLAUDE.md 에 SEO + GEO 섹션 삽입 — §변경이력 직전
```

```markdown
## NEW. 🚫 웹 SEO + GEO 가이드라인 (자동 검증)

- HTML 메타 태그 수정 시 `SEO_GUIDELINE.md` 참조 필수
- 수동 검증: `python3 scripts/check_seo.py <HTML_PATH>`
- pre-commit hook 에서 자동 검증 (커밋 차단)
- GEO: `llms.txt` + `llms-full.txt` 작성 필요 (규격: `docs/rules/RULES_GEO.md`)
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

   (hook 설치 사용자만 해당)
   scripts/baseline.yml 과 .claude/settings.json 의 ui_file_patterns / matcher regex
   → 기본값은 'apps/ios/.*\.swift$' 같은 통상 경로
   → 실제 프로젝트 구조 다르면 두 파일 같은 패턴으로 수정

   (Q2 == Firebase 사용자만 해당)
   Firebase 격리 확인:
   • .firebaserc default: <FB_PROJECT_ID>
   • firebase login 계정: (firebase login:list 결과)
   • 첫 deploy 전 권장: firebase use <FB_PROJECT_ID> (1회)

   (Q4 == SEO + GEO 사용자만 해당)
   SEO + GEO 검증 확인:
   • 대상 HTML: <HTML_PATH>
   • 수동 검증: python3 scripts/check_seo.py <HTML_PATH>
   • Q4b 미입력 시: SEO_GUIDELINE.md 의 [SITE_URL] 을 실제 URL 로 교체 필요
   • GEO: llms.txt + llms-full.txt 작성 필요 (상세: docs/rules/RULES_GEO.md §llms.txt 구조 규격)

🛠  프로젝트별 추가 작업 (플러그인 범위 밖)
   • 실제 앱 스캐폴드 (Xcode/Next.js/Flutter 등)
   • Git 원격 설정 (선택)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 플러그인 추천 로직

| 프로젝트 유형 | 추천 플러그인 |
|---|---|
| 웹 (Next.js) | `vercel`, `frontend-design` |
| 모바일·데스크톱 (iOS/Android/macOS) | `frontend-design` |
| Firebase 사용 | `firebase` |
| 모든 프로젝트 | `superpowers` (상시), `security-guidance` (출시 전) |
| Figma 연동 시 | `figma` |

---

## 원칙

- **사용자 Yes 한 옵션만** 파일 생성. 미선택 옵션의 파일은 만들지 말 것.
- **기존 파일 덮어쓰기 금지** (CLAUDE.md 존재 시 설정 변경 메뉴 제시).
- **커밋은 사용자 승인 후**. 자동으로 커밋하지 말 것.
- **tier 결정 로직**: Q1~Q4 모두 N 이면 Minimal, 하나라도 Yes 면 Full.
- **Minimal tier 는 RULES 0개 복사**. §Discovery 트리거 표도 미수록. 단, **플랫폼 답변에 macOS 포함 시** `RULES_MACOS_RELEASE` 1개를 가드레일급으로 복사 + 📎참조에 발견 포인터 1줄 주입 (§Step 2b).
- **Q0 == None + Q1b == No**: `.claude/settings.json` 자체 생성 안 함 (commands/ 는 생성).
- **.claudeignore 는 항상 생성** — 프로젝트 유형에 맞는 섹션 활성화.
- **.claude/commands/ 는 항상 생성** — build, check, status 기본 3개.
- **docs/ 표준 폴더 항상 생성** — summary, error, event, cost-plan, handoff, test, rules.
- **apps/ 폴더는 프로젝트 유형 + 플랫폼 답변에 따라** 생성.

## 참조

- 플러그인 설계 원칙: `${CLAUDE_PLUGIN_ROOT}/docs/design-principles.md`
- 마이그레이션 가이드: `${CLAUDE_PLUGIN_ROOT}/docs/migration-guide.md`
- 프로젝트 라이프사이클: `docs/rules/RULES_PROJECT_LIFECYCLE.md` (Full tier)
- Minimal tier RULES 0개 정책 근거: `${CLAUDE_PLUGIN_ROOT}/docs/specs/2026-05-05-v0.2.0-permissions-and-doc-slimming-design.md` §5.5/§7.3
