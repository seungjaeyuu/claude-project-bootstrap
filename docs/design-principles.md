# claude-project-bootstrap 설계 원칙

> 본 플러그인은 실전 프로젝트에서 반복 시행착오로 결정화된 패턴을 **다음 프로젝트부터 기본값으로** 적용하기 위한 도구입니다. 여기서는 주요 설계 결정의 **근거** 를 기록합니다.

---

## 1. 네거티브 우선 + 4층 규칙 범례

**원칙**: 규칙을 "금지만" 적되, 프로젝트에 **특별히 해당되는 것만** 명시. 고성능 LLM (Opus 4.x+) 이 자력 판단 가능한 일반 모범 사례는 제외.

**4층**:

| 이모지 | 층위 | 의미 |
|---|---|---|
| 🚫 | Guardrail | 절대 금지. 롤백 불가한 피해 또는 사고 재발 방지. |
| 📐 | Schema | 스키마·용어·명명 계약. 일관성 확보. |
| 📎 | 참조 | 경로·환경·도구 메타. 지침 아님. |
| 💡 | 권장 | 모범 사례. 근거 제시 시 override 가능. |

**반영**: `templates/CLAUDE.md.tmpl` 상단 범례 표.

---

## 2. 3-Template 베이스라인 규약

**문제**: 한 프로젝트의 `MASTER_TEST_BASELINE.md` 에 **13가지 서로 다른 헤더 변형** 혼재. 의미 같은 것을 다른 이름으로 부름 (`항목` / `미실행 필수 항목` / `기준 항목`) → 스크립트 파싱 불가, 사람 혼란.

**해결**: **3개 표준 Template 만 허용**.

| Template | 대상 |
|---|---|
| A | 이미 실행된 ID |
| B | 미실행·소스 보강 |
| C | 버그 추적용 (집계 제외) |

**기존 데이터 취급**: 즉시 변환하지 않음 — 자연어 셀 재해석 시 정보 손실 위험. 편집 기회 시 점진 전환.

**반영**: `templates/BASELINE.md.tmpl` 이 3 Template 으로 구조화.

---

## 3. 판정 Canonical = status.json

**문제**: baseline markdown 에 "최신 판정/메모" 를 한 셀에서 관리하면 **판정·메모·후속과제·참조 4가지가 섞여** 자동화 불가.

**해결**: **canonical 은 `status.json` 만**. baseline 의 텍스트 컬럼은 historical narrative.

| 데이터 | 위치 |
|---|---|
| 판정 (PASS/FAIL/BLOCK) | `docs/<app>/testing_harness/run/*_status.json` |
| 요약 | baseline "최신 요약" (판정 없이) |
| 후속 과제 | 프로젝트의 백로그 시스템 |
| 참조 | baseline "이전 프롬프트 매핑" 링크 |

**반영**: `scripts/baseline_status.py` 가 `status.json` 만 집계.

---

## 4. 이중 배치 지양 + 3계층 발견 경로

**원칙**: 같은 규칙을 여러 파일에 복붙하지 않음. 대신 **"Claude 가 언제 Read 하는가"** 를 설계.

**이중 배치의 함정**: 동기화 실패 시 더 큰 혼란. "어디에 쓰느냐" 보다 "어떻게 발견하느냐" 가 관건.

**발견 계층 (강제력 순)**:

| 계층 | 메커니즘 | 특징 |
|---|---|---|
| **T1** | Hook (기계적 강제) | 가장 확실. Git pre-commit, Claude Code PostToolUse 등 |
| **T2** | 자동 로드 (루트 `CLAUDE.md`) | 매 세션 인지 |
| **T3** | 조건부 로드 (앱별 `CLAUDE.md`) | 해당 영역 작업 시 |
| **T4** | On-demand (`TESTING_FRAMEWORK.md` 등) | Claude 가 Read 해야 발견 |

**플러그인 구조 반영**: `commands/` (명시적 호출), `templates/` (스캐폴드 시 1회), `scripts/` (target 프로젝트 복사 후 hook 에서 호출) 로 발견 시점 분리.

---

## 5. 하네스 도입 = `baseline.yml` entry 활성화

**문제**: "E2E 하네스 도입" 시점이 모호하면 사람·자동화가 각자 다르게 판단.

**해결**: **`baseline.yml` 의 `apps.<name>` entry 가 활성화되는 순간** = 하네스 도입 순간. 단일 SSOT.

**이유**:
- 한 파일 수정으로 스크립트·hook 모두 자동 인식
- 백로그 항목이 "언제 실행할지" 모호성 제거
- 신규 앱 추가 = entry 추가만으로 완료

**반영**: `templates/baseline.yml.tmpl` 이 commented-out entry + 활성화 설명으로 구성.

---

## 6. 트리거 기반 베이스라인 동기화

**문제**: "매 기능 수정마다 baseline 갱신" 은 매 프롬프트마다 Claude 가 판단해야 해서 거짓양성·음성 다수. 개별 커밋마다 하면 비효율. "기능 완료 시점" 은 정의 모호.

**해결**: **트리거 시점 일괄 검토 + Git diff 자동 제안**.

**트리거**:
- E2E 테스트 세션 시작
- 릴리스/베타 준비
- 정기 점검 (주 1회 권장)

**도구**: `/baseline-review` 슬래시 커맨드 → `scripts/baseline_update_suggest.py` 호출.

**강제력 계층**:
- **L1** Git pre-commit hook 경고 (차단 아님) — 놓침 방지
- **L3** `/baseline-review` 명시 호출 — 일괄 검토
- **L4** 문서 규약 — `TESTING_FRAMEWORK.md §20.7`

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-04-23 | 초판 — 6개 설계 원칙 편입 (실전 프로젝트 경험 기반 generic 화) |
