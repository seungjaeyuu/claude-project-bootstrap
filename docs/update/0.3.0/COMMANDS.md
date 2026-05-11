# v0.3.0 커맨드 체계 상세

---

## 커맨드 구조

```
┌──────────────────────────────────────────────┐
│  /guide   — 현재 단계 감지 + 커맨드 안내      │
└──────────────┬───────────────────────────────┘
               │
    ┌──────────┼──────────┬──────────┐
    ▼          ▼          ▼          ▼
  /init      /audit    /release   /baseline-review
  ② 설계     ③④ 점검   ⑤ 출시     ④ 테스트 (하위호환)
    │
    ├─ 신규 초기화
    └─ 설정 변경
       ├─ --bash
       ├─ --firebase
       ├─ --slim
       ├─ --hook
       └─ --plugins
```

---

## 1. `/init` — 프로젝트 초기화 + 설정 변경

### 신규 프로젝트 (CLAUDE.md 미존재)

대화형 질의 흐름:

```
필수 3개:
  1. 프로젝트 이름
  2. 프로젝트 유형 (a~e)
  3. 주요 언어·프레임워크

Q0. Bash 권한 단계 (YOLO/Standard/Strict/None)

Q1. E2E 테스트? (Y/N, 기본 N)
    └─ Y 시:
       Q1a. 앱 타입 (복수 선택)
       Q1b. Hook 설치? (Y/N, 기본 Y — 스마트 제안)
       Q1c. iOS/Android 시 Accessibility? (Y/N, 기본 Y — 스마트 제안)

Q2. BaaS? (Y/N, 기본 N)
    └─ Y 시:
       Q2a. 종류 (Firebase/Supabase/Amplify/기타)
       Q2b. Firebase 시 project ID

Q3. 개발 백로그? (Y/N, 기본 N)
    → TASK.md + tasks/ 구조
```

질의 수: 필수 3 + Q0~Q3 = **최소 4회, 최대 8회** (v0.2.1 최대 12회에서 축소).

### 기존 프로젝트 (CLAUDE.md 존재)

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

### 직접 옵션 호출

| 호출 | 동작 | 기존 커맨드 |
|---|---|---|
| `/init` | 메뉴 표시 (신규면 전체 흐름, 기존이면 선택 메뉴) | init-project |
| `/init --bash` | Bash 권한 변경 직행 | bash-permission |
| `/init --firebase` | Firebase 격리 직행 | firebase-isolation |
| `/init --slim` | CLAUDE.md 슬림화 직행 | slim-claude-md |
| `/init --hook` | 문서 크기 hook 직행 | doc-size-hook |
| `/init --plugins` | 플러그인 최적화 직행 | (신규) |

### 완료 시 출력 (신규 초기화)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 초기화 완료

📦 생성된 파일
   (실제 생성된 파일 목록)

🔌 플러그인 추천 (프로젝트 타입 기반)
   ✅ firebase — 이미 활성
   💡 frontend-design — UI 폴리싱 시 활성화 권장
   💡 security-guidance — 출시 전 /release 실행 시 활성화 권장
   ℹ️ figma — Figma 디자인 연동 시 활성화

⚙  확인이 필요한 항목
   (조건부 — hook 설치 시, Firebase 시 등)

🛠  프로젝트별 추가 작업 (플러그인 범위 밖)
   • 실제 앱 스캐폴드 (Xcode/Next.js/Flutter 등)
   • Git 원격 설정 (선택)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 2. `/audit` — 품질·컨텍스트·베이스라인 점검

### 실행 옵션

| 호출 | 점검 범위 |
|---|---|
| `/audit` | 전체 (아래 3개 모두) |
| `/audit --context` | 컨텍스트 최적화만 |
| `/audit --baseline` | 베이스라인 리뷰만 (= 기존 /baseline-review) |
| `/audit --quality` | 코드 품질만 |

### 컨텍스트 점검 (--context)

```
📊 컨텍스트 소비 현황

  CLAUDE.md         88줄  (상한 120)     ✅
  RULES 총합        420줄 (6개 파일)     ✅
  활성 플러그인      14개               ⚠️ 7개 비활성화 가능

  비활성화 권장:
    figma              — 현재 미사용 (Figma 파일 미감지)
    vercel             — 현재 미사용 (vercel.json 미감지)
    kotlin-lsp         — iOS 프로젝트에 불필요

  적용하시겠습니까? (Y/n)
  → Y: .claude/settings.json enabledPlugins 업데이트
```

### 베이스라인 점검 (--baseline)

기존 `/baseline-review` 와 동일 동작:
```bash
python3 scripts/baseline_update_suggest.py --app <name> --since 14days
```

### 품질 점검 (--quality)

```
📋 품질 점검

  CLAUDE.md 줄 수        88줄 / 120 상한    ✅
  RULES_E2E.md           99줄 / 250 상한    ✅
  미사용 RULES 감지       RULES_ACCESSIBILITY.md — 6개월간 UI 파일 변경 없음  ⚠️
  .claudeignore 존재      ✅
  .claude/commands/ 존재  ✅
```

---

## 3. `/release` — 출시 준비 체크

### 체크 항목 (5개 카테고리)

```
/release 실행 결과:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 출시 준비 점검

1. 버전·빌드번호
   ✅ 빌드번호: 47 (최신, main HEAD와 일치)
   ✅ CHANGELOG.md: 0.3.0 항목 존재
   ⚠️ package.json version: 0.2.1 — 업데이트 필요?

2. 보안
   ✅ .secret/ → .gitignore 보호됨
   ✅ .env 파일 커밋 없음
   ✅ Firebase predeploy hook 활성
   💡 security-guidance 플러그인 활성화 권장

3. 법적 문서
   ⚠️ 개인정보처리방침 미발견 — PRIVACY.md 생성 권장
   ⚠️ 이용약관 미발견 — TERMS.md 생성 권장

4. 국제화 (i18n)
   ❓ 다국어 지원이 필요합니까? (Y/N)
   → Y 시: 지원 언어 목록 질의 + 미번역 항목 점검 가이드

5. 테스트 (E2E 설정 시)
   ✅ PASS: 42건
   ⚠️ FAIL: 2건 (AUTH-S03, PAY-M01)
   ⚠️ BLOCKED: 1건

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 4. `/guide` — 단계 감지 + 커맨드 안내

### 단계 감지 휴리스틱

| 신호 | 추정 단계 |
|---|---|
| CLAUDE.md 없음 또는 소스 파일 0개 | ① 기획 / ② 설계 |
| 최근 커밋에 src/app 코드 변경 다수 | ③ 개발 |
| 최근 커밋에 test 파일 변경 다수 | ④ 테스트 |
| CHANGELOG 변경 또는 버전 파일 변경 | ⑤ 출시 준비 |
| git tag가 최근 커밋에 존재 | ⑤→⑥ 출시 완료 → 운영 |

### 출력 예시

```
/guide 실행 결과:

📍 현재 단계 추정: ③ 개발
   근거: 최근 7일간 apps/ios/ 변경 23건, test 변경 2건

🔧 지금 유용한 명령어:
   /audit              — 코드 품질·컨텍스트 점검
   RULES 자동 트리거    — CLAUDE.md §3 활성 중

📋 다음 단계 준비:
   ④ 테스트 →  /audit --baseline
   ⑤ 출시   →  /release

📖 전체 라이프사이클: docs/rules/RULES_PROJECT_LIFECYCLE.md

💡 단계별 플러그인 추천:
   ③ 개발    superpowers (활성), code-simplifier (비활성 — 리팩토링 시 활성화)
   ⑤ 출시    security-guidance (비활성 — 출시 전 활성화 권장)
```

---

## 5. 하위 호환

기존 커맨드는 유지하되, `/guide` 출력에서는 새 이름으로 안내.

| 기존 커맨드 | 동작 | 내부 라우팅 |
|---|---|---|
| `/bash-permission` | 그대로 작동 | = `/init --bash` |
| `/firebase-isolation` | 그대로 작동 | = `/init --firebase` |
| `/slim-claude-md` | 그대로 작동 | = `/init --slim` |
| `/doc-size-hook` | 그대로 작동 | = `/init --hook` |
| `/baseline-review` | 그대로 작동 | = `/audit --baseline` |
| `/init-project` | 그대로 작동 | = `/init` |

사용자 입장에서 기존 커맨드가 사라지지 않으므로 마이그레이션 부담 없음.
