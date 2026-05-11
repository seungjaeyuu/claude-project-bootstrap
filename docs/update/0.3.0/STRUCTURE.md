# v0.3.0 자동생성 구조 상세

---

## 전체 구조 맵

```
프로젝트 루트/
│
│ ── 항상 생성 ──────────────────────────────────────────
├── CLAUDE.md                        Full ~90줄 / Minimal ~75줄
├── INDEX.md                         ~85줄
├── .gitignore                       ~83줄
├── .claudeignore                    🆕 ~30줄
├── .secret/.gitkeep
│
├── .claude/
│   ├── settings.json                Q0≠None 또는 Q1=Y 시
│   └── commands/                    🆕 항상 생성
│       ├── build.md                 프로젝트별 빌드 명령
│       ├── check.md                 lint + typecheck + test 일괄
│       └── status.md               git status + TODO + 빌드번호
│
├── apps/                            🆕 프로젝트 유형에 따라
│   ├── ios/                         유형 b (SwiftUI) 시
│   ├── android/                     유형 b (Kotlin) 시
│   ├── web/                         유형 a 시
│   └── shared/                      유형 c (모노레포) 시
│
├── docs/
│   ├── rules/                       Full tier 시
│   │   ├── RULES_VERSIONING.md      🆕 항상 (semver + 빌드번호)
│   │   ├── RULES_PROJECT_LIFECYCLE.md  🆕 항상 (6단계 체크리스트)
│   │   ├── RULES_TERMINOLOGY.md     항상
│   │   ├── RULES_REFACTORING.md     항상
│   │   ├── RULES_E2E.md             Q1=Y
│   │   ├── RULES_DATA_INTEGRITY.md  Q2=Y
│   │   ├── RULES_ACCESSIBILITY.md   Q1=Y + iOS/Android
│   │   └── RULES_DICT_DUPLICATES.md Q1=Y + Hook
│   ├── summary/.gitkeep             🆕 회의록·요약
│   ├── error/.gitkeep               🆕 에러 분석·트러블슈팅
│   ├── event/.gitkeep               🆕 이벤트 로그·변경 이력
│   ├── cost-plan/.gitkeep           🆕 비용 계획·요금제
│   ├── handoff/.gitkeep             🆕 인계 문서
│   └── test/                        🆕 테스트 전체
│       ├── TESTING_FRAMEWORK.md     Q1=Y (루트에서 이동)
│       ├── baseline/                Q1=Y
│       │   └── {APP}_BASELINE.md    (파일명 단축)
│       ├── result/                  Q1=Y
│       │   └── {app}/              (status.json)
│       └── feedback/.gitkeep        Q1=Y
│
│ ── 조건부 생성 ──────────────────────────────────────
├── .firebaserc                      Q2=Y + Firebase
├── firebase.json                    Q2=Y + Firebase
├── TASK.md                          🆕 Q3=Y (기존 개발예정사항.md 영문화)
├── tasks/                           🆕 Q3=Y (기존 개발예정사항_상세/)
│   └── DEV-001.md                   샘플
│
└── scripts/                         조건부
    ├── pre-commit-framework.sh      Q1=Y + Hook (§6 빌드번호 포함)
    ├── install-hooks.sh             Q1=Y + Hook
    ├── baseline.yml                 Q1=Y
    ├── baseline_status.py           Q1=Y
    ├── baseline_update_suggest.py   Q1=Y
    ├── check_baseline_sync.py       Q1=Y + Hook
    ├── posttooluse_ax_check.py      Q1=Y + AX
    └── check_firebase_project.py    Q2=Y + Firebase
```

---

## 파일 수 비교 (v0.2.1 → v0.3.0)

| 시나리오 | v0.2.1 | v0.3.0 | 증감 | 비고 |
|---|---|---|---|---|
| Minimal (모두 N) | 4 | 14 | +10 | .claudeignore, commands/3, docs/7(.gitkeep), apps/ |
| Full (모두 N) | 6 | 18 | +12 | + RULES 4개 (기존2+신규2) |
| Full + Q1만 Y | ~14 | ~25 | +11 | + docs/test/ 하위 |
| Full 전부 Y | ~27 | ~32 | +5 | 구조 재배치 중심 |

증가분 대부분은 `.gitkeep`(0줄) 또는 on-demand RULES.
**CLAUDE.md 토큰은 감소** (120→~90줄).

---

## docs/ 폴더 명명 규칙

### 🚫 안티패턴

```
docs/superpowers/          ← 플러그인/스킬 명칭
docs/figma-designs/        ← 도구 명칭
docs/claude-code/          ← 도구 명칭
docs/sprint-3/             ← 시간 기반 (카테고리 아님)
```

### ✅ 올바른 명명

```
docs/summary/              ← 문서의 목적/역할 기준
docs/error/                ← 문서의 목적/역할 기준
docs/test/                 ← 문서의 목적/역할 기준
```

**원칙**: docs/ 하위 폴더명은 **문서의 목적·역할** 기준.
도구·플러그인·스프린트 명칭으로 폴더를 만들지 않음.

---

## apps/ 플랫폼별 구조

프로젝트 유형(필수 질문 2번) 연동:

| 유형 | 생성 폴더 |
|---|---|
| (a) 단일 웹 | `apps/web/` |
| (b) 단일 모바일 SwiftUI | `apps/ios/` |
| (b) 단일 모바일 Kotlin | `apps/android/` |
| (b) 단일 모바일 Flutter | `apps/flutter/` |
| (c) 모노레포 | 선택한 플랫폼 전부 + `apps/shared/` |
| (d) 백엔드 | `apps/server/` 또는 `src/` (언어에 따라) |
| (e) 기타 | 사용자 지정 |

---

## .claudeignore 생성 규칙

프로젝트 유형에 따라 관련 섹션을 주석 해제:

```
# 공통 (모든 프로젝트) — 항상 포함
*.lock
*.min.js
*.min.css
*.map
*.png *.jpg *.jpeg *.gif *.ico *.svg
*.woff *.woff2 *.ttf *.eot
*.mp4 *.mp3 *.pdf

# iOS — 유형 b (SwiftUI) 시
DerivedData/
*.xcuserstate
*.ipa

# Android — 유형 b (Kotlin) 시
.gradle/
build/
*.apk *.aab

# Web — 유형 a 시
node_modules/
.next/
dist/
out/

# Flutter — 유형 b (Flutter) 시
.dart_tool/
build/
```

---

## .claude/commands/ 기본 3개

### build.md

```markdown
---
description: 프로젝트 빌드
---
프로젝트를 빌드합니다.

(프로젝트 유형별 빌드 명령 — init 시 자동 채움)
```

### check.md

```markdown
---
description: 빠른 품질 체크 (lint + typecheck + test)
---
lint, typecheck, 단위 테스트를 일괄 실행합니다.

(프로젝트 유형별 명령 — init 시 자동 채움)
```

### status.md

```markdown
---
description: 프로젝트 상태 요약
---
다음 항목을 확인하여 요약합니다:
1. git status (변경 파일, 현재 브랜치)
2. 현재 버전·빌드번호
3. TASK.md 미완료 항목 수 (있는 경우)
4. 최근 5개 커밋 요약
```

---

## CLAUDE.md Full tier 구조 (v0.3.0, ~90줄 목표)

```
§1 규칙 층위 범례                     ~16줄 (유지)
§2 횡단 가드레일                      ~24줄 (유지 + API키·빌드번호 병합)
   - Git 안전
   - 사용자 의견 피드백 의무
   - 개발 완료 보고
   - 대규모 변경 grep 검증
   - 🚫 API 키·시크릿 평문 금지     (기존 §7에서 1줄 병합)
   - 📐 빌드번호 단일 원천            (신규 1줄)
§3 발견 트리거 표                      ~20줄 (유지 + 2행 추가)
§4 문서·폴더 규칙                      ~12줄 (신규)
   - MD 파일명: YYYYMMDD_ 접두어
   - docs/ 폴더명: 목적 기준 (도구명 금지)
   - 완료 보고: ✅/⏳/📋 3상태
§5 모노레포 분산                       ~6줄 (해당 시만)
변경 이력                              ~2줄
```

삭제 항목:
- 기존 §4 빌드 명령 → `.claude/commands/build.md`로 이동
- 기존 §6 모노레포 → §5로 축소, 비모노레포 시 삭제
- 기존 §7 API 키 → §2에 🚫 1줄 병합 + INDEX.md에 경로 참조

---

## TASK.md + tasks/ 구조

기존 `개발예정사항.md` + `개발예정사항_상세/`를 영문화.

### TASK.md (인덱스)

```markdown
# 개발 백로그

| ID | 상태 | 제목 | 상세 |
|---|---|---|---|
| DEV-001 | 🟡 대기 | (샘플) | [상세](tasks/DEV-001.md) |
```

### tasks/DEV-001.md (상세)

```markdown
# DEV-001: (제목)

- **상태**: 🟡 대기
- **우선순위**: P2
- **생성일**: YYYY-MM-DD

## 설명

(상세 내용)

## 수용 기준

- [ ] (기준 1)
- [ ] (기준 2)
```

---

## 테스트 문서 이동 (루트 → docs/test/)

### v0.2.1 → v0.3.0 경로 변경

| v0.2.1 | v0.3.0 |
|---|---|
| `TESTING_FRAMEWORK.md` | `docs/test/TESTING_FRAMEWORK.md` |
| `IOS_MASTER_TEST_BASELINE.md` | `docs/test/baseline/IOS_BASELINE.md` |
| `ANDROID_MASTER_TEST_BASELINE.md` | `docs/test/baseline/ANDROID_BASELINE.md` |
| `docs/ios/testing_harness/run/` | `docs/test/result/ios/` |
| `docs/android/testing_harness/run/` | `docs/test/result/android/` |

### scripts/baseline.yml 경로 업데이트

```yaml
# v0.3.0
apps:
  ios:
    baseline: docs/test/baseline/IOS_BASELINE.md
    status_dir: docs/test/result/ios
```
