# claude-project-bootstrap v0.3.0 — 업데이트 개요

> **버전**: 0.3.0
> **시작일**: 2026-05-11
> **성격**: 컨텍스트 최적화 + 프로젝트 라이프사이클 + 구조 개선

---

## 배경

v0.2.1까지 "네거티브 우선 + E2E 베이스라인 하네스"를 안정화했으나, 다음 문제가 확인됨:

1. **컨텍스트 윈도우 낭비** — 불필요한 플러그인이 세션마다 ~8,000토큰 선점
2. **init-project 질문 과다** — 최대 12회 질의, Q3/Q4가 Q1 종속임에도 독립 질문
3. **CLAUDE.md 과잉 정보** — 빌드 명령·모노레포 구조 등 참조 정보가 매 세션 attention
4. **프로젝트 단계별 가이드 부재** — 출시 준비 체크포인트 없음
5. **Claude Code 공식 권장사항 미적용** — .claudeignore, 커스텀 커맨드 등
6. **폴더·문서 구조 가이드 부재** — docs/ 체계 없음, 테스트 문서 루트 산재
7. **빌드번호 관리 부재** — 플랫폼별 SSOT 없음, 자동 증가 없음

---

## 변경 요약

### A. 커맨드 체계 재설계 (8개 → 4개 + 하위호환)

| 신규 | 역할 | 단계 |
|---|---|---|
| `/init` | 초기화 + 설정 변경 메뉴 (기존 4개 설정 커맨드 흡수) | ② 설계 |
| `/audit` | 품질·컨텍스트·베이스라인 점검 (기존 baseline-review 흡수) | ③④ 개발·테스트 |
| `/release` | 출시 준비 체크 (보안·법적·버전·i18n) | ⑤ 출시 |
| `/guide` | 단계 감지 + 커맨드 안내 | 전 단계 |

기존 커맨드(`/bash-permission`, `/firebase-isolation`, `/slim-claude-md`, `/doc-size-hook`, `/baseline-review`)는 하위 호환 유지.

### B. init-project 질문 최적화 (12회 → 최대 8회)

- Q3(Hook), Q4(Accessibility)를 Q1(E2E) 하위로 흡수
- Git URL을 필수에서 선택으로 이동
- Q5(백로그) → Q3으로 승격, 영문화 (TASK.md + tasks/)

### C. 자동생성 구조 확장

- `.claudeignore` 자동 생성 (프로젝트 타입별)
- `.claude/commands/` 기본 3개 (build, check, status)
- `docs/` 표준 폴더 7개 (summary, error, event, cost-plan, handoff, test, rules)
- `apps/` 플랫폼별 폴더 (프로젝트 유형 연동)
- 테스트 문서 `docs/test/`로 통합 (루트에서 이동)

### D. 신규 RULES 2개

- `RULES_VERSIONING.md` — semver + 빌드번호 SSOT + 자동 증가
- `RULES_PROJECT_LIFECYCLE.md` — 6단계 라이프사이클 체크리스트

### E. 기존 파일 슬림화

- `CLAUDE.md.tmpl`: 120줄 → ~90줄 (빌드 명령·모노레포·API키 이동)
- `CLAUDE.minimal.md.tmpl`: 97줄 → ~75줄
- `TESTING_FRAMEWORK.md.tmpl`: 167줄 → ~130줄 (§2 축소, docs/test/로 이동)
- `BASELINE.md.tmpl`: 84줄 → ~75줄 (중복 범례 제거, 파일명 단축)

### F. 빌드번호 자동 증가

- `pre-commit-framework.sh` §(6) 추가 — main 브랜치 감지, 플랫폼별 정본 +1
- 플랫폼 자동 감지: iOS(project.yml) / Android(build.gradle) / Web(package.json)

---

## 상세 문서

| 문서 | 내용 |
|---|---|
| [COMMANDS.md](COMMANDS.md) | 커맨드 체계 상세 (init 재실행 모드, audit 옵션, release 체크항목, guide 휴리스틱) |
| [STRUCTURE.md](STRUCTURE.md) | 자동생성 파일·폴더 구조 전체 맵 |
| [LIFECYCLE.md](LIFECYCLE.md) | 프로젝트 라이프사이클 6단계 + 플러그인 매핑 |
| [FILES.md](FILES.md) | 변경 파일 목록 + 파일별 변경 사양 |

---

## 마일스톤

| 순위 | 항목 | 상태 |
|---|---|---|
| P0 | init-project 질문 최적화 + 커맨드 재설계 | ⏳ |
| P0 | CLAUDE.md 슬림화 + .claudeignore + .claude/commands/ | ⏳ |
| P0 | docs/ 폴더 구조 + apps/ 플랫폼 폴더 | ⏳ |
| P1 | RULES_VERSIONING.md + 빌드번호 hook | ⏳ |
| P1 | RULES_PROJECT_LIFECYCLE.md | ⏳ |
| P1 | INDEX.md 재설계 | ⏳ |
| P2 | /audit 커맨드 (context-audit + baseline-review 통합) | ⏳ |
| P2 | /release 커맨드 | ⏳ |
| P2 | /guide 커맨드 | ⏳ |
| P3 | TESTING_FRAMEWORK / BASELINE 슬림화 + docs/test/ 이동 | ⏳ |
| P3 | design-principles.md §1 보강 | ⏳ |
| P3 | plugin.json + CHANGELOG | ⏳ |
