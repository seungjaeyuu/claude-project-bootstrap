# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-04-23

### Added

**슬래시 커맨드 2개** (네임스페이스: `/claude-project-bootstrap:*`)
- `init-project` — 새 프로젝트 초기화 (Q1~Q5 대화형 질의 + 4줄 설명 + Q1a 앱 타입 선택 + iOS/Android 시 Q4 스마트 제안)
- `baseline-review` — Git diff 기반 베이스라인 갱신 제안

**템플릿 8개** (`templates/*.tmpl`)
- `CLAUDE.md.tmpl` — Full tier (네거티브 우선 + 4층 규칙 범례, 전체 규약, ~298줄)
- **`CLAUDE.minimal.md.tmpl` — Minimal tier (Q1~Q5 모두 N 시, ~97줄)**
- `INDEX.md.tmpl` — 프로젝트 지도
- `TESTING_FRAMEWORK.md.tmpl` — E2E 하네스 규약 (§20 베이스라인)
- `BASELINE.md.tmpl` — 3 Template (A/B/C) 구조
- `baseline.yml.tmpl` — 멀티플랫폼 베이스라인 설정
- `settings.json.tmpl` — Claude Code PostToolUse hook (stdin JSON + systemMessage 스펙 준수)
- `gitignore.tmpl` — 보안·생성물 보호 패턴

**Python 검증 스크립트 6개** (target 프로젝트로 복사)
- `baseline_status.py` — 베이스라인 판정 상태 집계
- `baseline_update_suggest.py` — Git diff 기반 베이스라인 갱신 제안
- `check_baseline_sync.py` — pre-commit UI 파일·baseline 동기화 검사
- `check_accessibility_identifiers.py` — SwiftUI accessibility 라벨 스키마 검증
- `check_dict_duplicates.py` — Swift/Kotlin/TypeScript dict literal 중복 키 검출
- **`posttooluse_ax_check.py` — Claude Code PostToolUse hook wrapper (stdin JSON 파싱 + systemMessage 응답)**

**Hook 스크립트 2개**
- `install-hooks.sh` — Git pre-commit + 검증 스크립트 원클릭 설치 (`.claude/settings.json` 은 Q4 조건부로 `/init-project` 가 별도 처리)
- `pre-commit-framework.sh` — Git pre-commit (target 프로젝트로 symlink)

**문서 3개**
- `docs/design-principles.md` — 6개 공개 설계 원칙 (네거티브 우선, 3-Template 규약, status.json canonical, 이중 배치 지양, baseline.yml entry 활성화, 트리거 기반 동기화)
- `docs/changelog-decisions.md` — 5개 내부 결정 로그
- `docs/migration-guide.md` — 기존 `_PROJECT_FRAMEWORK` 사용자 이관 가이드

### Improvements (Phase 7 피드백 반영)

- **Issue #1**: Minimal/Full 2-tier CLAUDE.md 템플릿 도입 — 단순 greenfield (Q1~Q5 모두 N) 프로젝트에 97줄 Minimal 사용
- **Issue #2**: `/init-project` Q1~Q5 각각에 "무엇/언제/생성/기본N이유" 4줄 설명 + iOS 선택 시 Q4 스마트 제안
- **Issue #3**: 완료 리포트 5항목 분산 → 📦 생성 파일 / ⚙ 확인 / 🛠 프로젝트별 추가 3블록 구조
- **Issue #4**: PostToolUse hook 을 Claude Code 공식 스펙 (stdin JSON + systemMessage) 기반으로 재구현. 기존 `$CLAUDE_TOOL_FILE_PATH` 환상 환경변수 참조 결함 해결

### Notes

- 커맨드는 `/claude-project-bootstrap:init-project` 형식 (plugin-name prefix 필수, Claude Code v2.1.117 기준)
- `${CLAUDE_PLUGIN_ROOT}` 변수 기반 이식성 확보
- Phase 7 로컬 검증 9/9 통과 + Phase 7 재검증 (Hook 재구현 후) E4 **완전체 PASS**
- v0.2 로드맵: Issues #5 (argument UI 대응), #6 (Q# 축약 표기 풀어쓰기)

## [0.1.1] - 2026-04-23

### Changed

- **`docs/design-principles.md` 전면 톤 개선** — 공개 가치 문서를 "문제→해결" 구조에서 "효과·가치 중심" 구조로 재작성
  - 6개 섹션 제목 자연어화: 예 `"판정 Canonical = status.json"` → `"테스트 결과와 문서 설명 분리"`
  - 각 섹션에 "이 구조가 제공하는 것" 불릿 3-4개 추가 (상태 관리 / 통일성 / 수정 개발 자동 도출 / 성과 측정 등)
  - 본문 구조 통일: "원칙 → 이 구조가 제공하는 것 → 적용 → 배경"
- **기술 용어 한국어 병기**: canonical → 기준 원본 / SSOT → 단일 원천 / historical narrative → 과거 맥락 요약 / tier → 단계 / PASS/FAIL/BLOCK → 통과/실패/보류

### Notes

- v0.1.0 → v0.1.1 은 **문서 톤 개선만**. 코드·기능 변경 없음 (완전 하위 호환, 재설치 불필요)
- 외부 피드백 반영 (2026-04-23): "문제→해결 구조는 특정 프로젝트 시행착오 인상, 효과·가치 중심이 범용적이고 공감대 높음"

## [0.2.0] - 2026-05-05

### Added — Bash 권한 4단계 (Q0)

`init-project` 의 필수 1-4 직후에 새 질문 추가. `.claude/settings.json` 의 `permissions` 키 머지.

- **YOLO** — 거의 모두 자동, 파괴 명령(`rm -rf`, `git reset --hard`, `git push --force` to main, DB drop)만 deny
- **Standard** *(권장)* — 안전 명령 자동, 위험 명령 ask, 절대 파괴 deny. ask vs deny 원칙: 롤백 가능 = ask, 롤백 불가 = deny
- **Strict** — 읽기 전용(`ls`, `cat`, `git status` 등)만 자동, 그 외 ask
- **None** — `permissions` 키 자체 미생성 (Claude Code 기본 동작)

신규 파일: `templates/permissions/{yolo,standard,strict}.json`

### Added — Firebase 격리 안전장치

사용자 사고 사례(appfoo 프로젝트가 `appbar-xxx` 같은 다른 프로젝트로 잘못 deploy) 재발 방지. `firebase deploy` 가 어디서 호출되든 (Claude / 사용자 직접 / CI) `predeploy` hook 이 활성 프로젝트 검증을 자동 실행.

`init-project` 에서 Q2 Yes 시 Q2a (백엔드 종류) → Q2a == Firebase 시 Q2b (project ID) sub-input.

생성:
- `.firebaserc` — `projects.default` = 입력값 (활성 프로젝트 결정 SSOT)
- `firebase.json` — 4개 영역(functions/hosting/firestore/storage) 의 `predeploy` hook 등록
- `scripts/check_firebase_project.py` — Firebase CLI 우선순위(env > .firebaserc > firebase use > configstore) 활용해 활성 프로젝트 결정 + mismatch 시 비-0 종료 + 명확한 에러 메시지
- CLAUDE.md 본체에 §NEW Firebase 격리 (3줄, Q2 Yes + Firebase 시만)
- INDEX.md 에 "Firebase deploy 직접 실행 체크리스트 2줄"
- 완료 리포트의 ⚙ 블록에 검증 요약 (`.firebaserc` default, login 계정, 글로벌 캐시 의심 여부)

신규 파일: `templates/.firebaserc.tmpl`, `templates/firebase.json.tmpl`, `scripts/check_firebase_project.py`

### Changed — CLAUDE.md.tmpl 슬림화 (298 → 120줄, 60% 축소)

v0.1.x 의 Full tier 가 298줄까지 비대해진 것은 본 플러그인의 *토큰 절약을 통한 개발 정확성 향상* 목적의 자기 위반. v0.2.0 에서 본체는 **횡단 가드레일 + 발견 트리거 표** 만 유지.

본체 구성 (정확히 120줄):
- §1 규칙 층위 범례 (4층 🚫 / 📐 / 📎 / 💡)
- §2 횡단 가드레일 4건 (Git 안전 / 사용자 의견 피드백 / 개발 완료 보고 / 대규모 변경 grep 검증)
- §3 발견 트리거 표 (작업 종류 → RULES read 매핑, fallback 행 포함)
- §4 빌드 / §5 문서 규칙 / §6 모노레포 분산 / §7 외부 API 키

`scripts/check_doc_size.py` 가 임계치 강제 (120줄 본체, 250줄 sub-CLAUDE.md/RULES). pre-commit 경고 (차단 안 함).

### Added — 영역별 RULES 6개 분리

CLAUDE.md 본체에서 영역별 상세 규칙을 분리. Full tier 사용 시 사용자 응답에 따라 조건부 복사.

- `RULES_E2E.md` (99줄) — E2E 테스트 / Codex orchestrator (Q1 Yes 시)
- `RULES_DATA_INTEGRITY.md` (61줄) — 백엔드 데이터 정합성 (Q2 Yes 시)
- `RULES_ACCESSIBILITY.md` (84줄) — UI accessibility identifier (Q4 Yes 시)
- `RULES_TERMINOLOGY.md` (62줄) — 스키마명 병기 + 도메인 용어 (Full tier 면 항상)
- `RULES_DICT_DUPLICATES.md` (86줄) — Swift/Kotlin/TS 중복 키 (Q3/Q4 Yes 시)
- `RULES_REFACTORING.md` (105줄) — 대규모 변경 grep 검증 (Full tier 면 항상)

**§Discovery 트리거 표가 토큰 절약 핵심 메커니즘**: LLM 은 본체에서 표만 보고 작업 시점에 매칭되는 1개 RULES 만 read. 분류 모호 시 fallback 행이 design-principles.md 로 회귀시켜 누락 차단.

신규 파일: `templates/rules/RULES_*.md.tmpl` (6개)

### Added — 문서 크기 검증 스크립트

`scripts/check_doc_size.py` — pre-commit 에서 호출되어 CLAUDE.md / RULES 줄 수가 임계치 초과 시 stderr 경고. 차단 안 함, 인지 목적. 임계치는 스크립트 상단 상수.

### Added — 4개 기능별 슬래시 커맨드 (마이그레이션 + 재설정)

기존 v0.1.x 프로젝트에 v0.2.0 새 기능을 도입하거나, 신규 프로젝트에서 init 후 후속 변경 시 사용. 마이그레이션 전용이 아닌 idempotent 도구.

- `/claude-project-bootstrap:bash-permission` — Bash 권한 단계 도입·변경
- `/claude-project-bootstrap:firebase-isolation` — Firebase 격리 도입
- `/claude-project-bootstrap:slim-claude-md` — CLAUDE.md 슬림화 + RULES 분리 (`migrate_diagnose.py` 가 분리 후보 진단)
- `/claude-project-bootstrap:doc-size-hook` — `check_doc_size.py` 도입

**4중 안전장치**: 자동 백업(`_backup_v0.1/`) / Diff preview / 영역별 독립 / 본체는 진단·확인 기반 (자동 분리 0건)

신규 파일: `commands/{bash-permission,firebase-isolation,slim-claude-md,doc-size-hook}.md`, `scripts/migrate_diagnose.py`

### Changed — design-principles.md §1, §4 보강

새 원칙 추가하지 않고 기존 §1, §4 에 구체값만 명시 — 본 플러그인의 SSOT 자기 위반 회피.

- §1 — CLAUDE.md 120줄 / sub 250줄 임계치 표 + 강제 메커니즘 명시
- §4 — 영역별 RULES 분리 매핑 + 트리거 표가 토큰 절약 핵심 메커니즘이라는 점

### Notes

- v0.1.x 와 100% 하위 호환 — 기존 프로젝트 자동 변경 없음
- 새 기능 도입은 4개 기능별 슬래시 커맨드로 *언제든* 가능
- v0.1.x 회귀 방지: CLAUDE.md.tmpl 자체가 120줄 — `check_doc_size.py` 가 본 플러그인 저장소에서도 자가 검증 가능
- 사용자 사고 사례(298줄 본체 / Firebase 잘못 deploy) 가 v0.2.0 설계의 출발점

## [0.2.1] - 2026-05-08

### Fixed — YOLO 권한 단계의 `firebase deploy` 과잉 차단

v0.2.0 의 `templates/permissions/yolo.json` `deny` 리스트에 `Bash(firebase deploy:*)` 가 포함되어 있어, **사용자가 명시적으로 Claude 에게 deploy 를 지시해도 권한 프롬프트조차 뜨지 않고 즉시 거부**되는 현상이 보고됨 (`Permission to use Bash with command firebase deploy ... has been denied.`).

원인 분석:
- spec 문서의 의도는 "LLM 이 자율로 deploy 호출하지 않게" 였으나, 사용자가 명시적으로 지시한 케이스까지 막혀 over-restriction.
- YOLO 자체 원칙("롤백 가능 = ask, 롤백 불가 = deny", "파괴 명령만 deny") 과도 모순. `firebase deploy` 는 롤백 가능(이전 버전 redeploy / `functions:delete`) 한 일반 배포 작업.
- v0.2.0 이 도입한 Firebase 격리의 핵심 안전망인 `predeploy` hook (`scripts/check_firebase_project.py`) 이 이미 잘못된 프로젝트 deploy 를 차단하므로 deny 는 안전장치 중복.

수정:
- `templates/permissions/yolo.json` — `Bash(firebase deploy:*)` 항목 제거. YOLO 에서 `firebase deploy` 는 다시 자동 실행 (`Bash(*)` allow 매치).
- 사용자 사고 방지(잘못된 프로젝트 deploy)는 v0.2.0 이 도입한 `predeploy` hook 가 단독으로 책임.
- `docs/specs/2026-05-05-v0.2.0-permissions-and-doc-slimming-design.md` §3.1 표, §3.3 yolo.json 예시·근거 단락 정합화.
- `CHANGELOG.md` v0.2.0 YOLO 설명에서 `firebase deploy` 제거.

영향:
- `Standard` / `Strict` 단계는 영향 없음 (Standard 는 `Bash(firebase:*)` 를 ask, Strict 는 미명시 → 기본 ask).
- 기존 v0.2.0 사용자: 플러그인 재설치 후 `init-project` 재실행하거나, `.claude/settings.json` 의 `permissions.deny` 에서 `Bash(firebase deploy:*)` 한 줄 직접 제거.

## [0.3.0] - 2026-05-11

### Added — 컨텍스트 최적화 3종

- **.claudeignore 자동 생성**: 프로젝트 유형별 바이너리·빌드 산출물 제외 (iOS/Android/Web/Flutter 섹션)
- **enabledPlugins**: `.claude/settings.json` 에서 불필요 플러그인 비활성화 → 0 토큰 소비. `/audit --context` 가 자동 제안
- **.claude/commands/ 기본 3개**: `/build`, `/check`, `/status` — 빌드 명령을 CLAUDE.md 에서 분리

### Added — 커맨드 체계 재설계 (8개 → 4개 메인 + 하위호환)

- `/init` — 신규 초기화 + 기존 프로젝트 설정 변경 메뉴 (기존 `/init-project` 흡수)
  - `--bash`, `--firebase`, `--slim`, `--hook`, `--plugins` 직접 옵션
  - Q3(Hook)/Q4(AX) → Q1(E2E) 하위 질의로 흡수 (최대 12회 → 8회)
  - Q5(개발예정사항) → Q3(TASK.md) 승격 + 영문화
- `/audit` — 품질·컨텍스트·베이스라인 일괄 점검 (기존 `/baseline-review` 흡수)
  - `--context`, `--baseline`, `--quality` 옵션
- `/release` — 출시 준비 체크 (보안·법적·버전·i18n·테스트 5개 카테고리)
- `/guide` — 프로젝트 단계 자동 감지 + 커맨드 안내
- 기존 5개 커맨드(`/bash-permission`, `/firebase-isolation`, `/slim-claude-md`, `/doc-size-hook`, `/init-project`)는 하위호환 유지

### Added — 프로젝트 라이프사이클 프레임워크

`RULES_PROJECT_LIFECYCLE.md` — SDLC + PMBOK 기반 6단계 모델 (기획→설계→개발→테스트→출시→운영). 강제가 아닌 체크리스트.

### Added — 빌드번호 자동 증가 + XcodeGen 동기화

- `RULES_VERSIONING.md` — semver + 빌드번호 SSOT 규칙 (iOS/Android/Web 플랫폼별 정본 위치)
- `pre-commit-framework.sh` §(6) — main 브랜치 커밋 시 정본 파일 +1 자동 staging
  - iOS: `project.yml` 다중 경로 탐색 (`iOS/`, 루트, `app/`) + `xcodegen generate` + `.xcodeproj` 재staging
  - 🚫 이중 증가 방지: 이 hook 이 유일한 빌드번호 증가 경로
- `post-merge.sh` — merge 후 `project.yml` 변경 감지 시 `.xcodeproj` 자동 재생성 (빌드번호 불변)
- `install-hooks.sh` — post-merge hook 설치 블록 추가
- CLAUDE.md §2 에 `📐 버전·빌드번호` + `🚫 빌드번호 이중 증가 방지` 가드레일 추가

### Added — 표준 폴더 구조

- `docs/` 표준 7개 폴더: summary, error, event, cost-plan, handoff, test, rules
- `apps/` 플랫폼별 폴더: 프로젝트 유형(a~e)에 따라 자동 생성
- 🚫 docs/ 하위 폴더명 안티패턴: 플러그인·도구 명칭으로 폴더 생성 금지

### Added — TASK.md + tasks/ 백로그 구조

기존 `개발예정사항.md` + `개발예정사항_상세/` 를 영문화. 인덱스(`TASK.md`) + 상세(`tasks/DEV-XXX.md`) 2계층.

### Changed — CLAUDE.md.tmpl 슬림화 (120 → ~94줄)

- §4 빌드 → `.claude/commands/build.md` 이동
- §7 API키 → §2 에 🚫 1줄 병합
- §3 발견 트리거에 VERSIONING, PROJECT_LIFECYCLE 행 추가
- §4 문서·폴더 규칙 신설 (YYYYMMDD 접두어 + 폴더 명명)
- §6 모노레포 → §5 축소

### Changed — CLAUDE.minimal.md.tmpl 슬림화 (97 → ~67줄)

Full 템플릿과 구조 통일 (§1 범례 → §2 횡단 가드레일 → §3 문서·폴더).

### Changed — TESTING_FRAMEWORK.md.tmpl 슬림화 (167 → ~130줄)

- §2 Cross-Lane: 25줄→3줄 (RULES_E2E.md 참조)
- §20.8 baseline_status.py: 15줄→5줄 (--help 참조)
- §20.9 새 플랫폼 추가: 삭제 (init이 자동 생성)
- 경로: docs/test/ 기준

### Changed — BASELINE.md.tmpl 슬림화

- 파일명: `{APP}_MASTER_TEST_BASELINE.md` → `{APP}_BASELINE.md`
- 상태 범례 표 삭제 → TESTING_FRAMEWORK 참조 1줄
- 경로: `docs/test/baseline/` 기준

### Changed — INDEX.md.tmpl 재설계

- E2E 전용 하드코딩 → 조건부 HTML 주석
- apps/ 플랫폼별 구조 반영
- 빌드·품질 명령 섹션 추가 (/build, /check, /status)
- docs/ 폴더 구조 가이드 + 안티패턴
- 주요 문서 인덱스 섹션 (사용자 등록)
- 스크립트·자동화 섹션 조건부

### Changed — design-principles.md §1 보강

"컨텍스트 예산" 관점 추가. 임계치 근거를 "가독성"에서 "컨텍스트 윈도우 유한 자원"으로 확장. enabledPlugins + .claudeignore 메커니즘 언급.

### Notes

- v0.2.x 와 100% 하위 호환 — 기존 프로젝트·커맨드 자동 변경 없음
- 기존 커맨드는 유지하되 v0.3.0 안내 메시지 추가
- CLAUDE.md 토큰은 전 버전 대비 감소 (120→~94줄)
- 신규 파일 대부분은 `.gitkeep`(0줄) 또는 on-demand RULES

## [Unreleased]

### Changed
- 공식 카탈로그(`anthropics/claude-plugins-official`) 제출 준비: `marketplace.json` 루트의 비표준 `repository` 키 제거 (`claude plugin validate` 통과), `plugin.json` 의 `repository` 를 객체형(`{type, url}`)으로 변경, 매니페스트 및 10개 커맨드 `description` 을 영문 우선(영/한 병기)으로 전환

다음 릴리스 예정 개선사항:
- `/retro-check` — 회고 커맨드 (v0.4.0 예정)
- Claude Code argument UI 제약 대응 (#5)
- YOLO 단계 deny 리스트 보강 (사용자 피드백 기반)
