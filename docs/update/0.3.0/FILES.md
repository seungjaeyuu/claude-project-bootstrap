# v0.3.0 변경 파일 목록 + 파일별 변경 사양

---

## 신규 파일 (11개)

### 커맨드

| 파일 | 용도 | 참조 |
|---|---|---|
| `commands/audit.md` | /audit — 품질·컨텍스트·베이스라인 점검 | [COMMANDS.md §2](COMMANDS.md) |
| `commands/release.md` | /release — 출시 준비 체크 | [COMMANDS.md §3](COMMANDS.md) |
| `commands/guide.md` | /guide — 단계 감지 + 커맨드 안내 | [COMMANDS.md §4](COMMANDS.md) |

### 템플릿

| 파일 | 용도 | 참조 |
|---|---|---|
| `templates/claudeignore.tmpl` | .claudeignore — Claude Code 컨텍스트 제외 | [STRUCTURE.md](STRUCTURE.md) |
| `templates/commands/build.md.tmpl` | 타겟 프로젝트 /build 커맨드 | [STRUCTURE.md](STRUCTURE.md) |
| `templates/commands/check.md.tmpl` | 타겟 프로젝트 /check 커맨드 | [STRUCTURE.md](STRUCTURE.md) |
| `templates/commands/status.md.tmpl` | 타겟 프로젝트 /status 커맨드 | [STRUCTURE.md](STRUCTURE.md) |
| `templates/rules/RULES_VERSIONING.md.tmpl` | semver + 빌드번호 SSOT + 자동 증가 | 빌드번호 스펙 문서 |
| `templates/rules/RULES_PROJECT_LIFECYCLE.md.tmpl` | 6단계 라이프사이클 체크리스트 | [LIFECYCLE.md](LIFECYCLE.md) |
| `templates/task.md.tmpl` | TASK.md 인덱스 템플릿 | [STRUCTURE.md](STRUCTURE.md) |
| `templates/task-detail.md.tmpl` | tasks/DEV-001.md 상세 템플릿 | [STRUCTURE.md](STRUCTURE.md) |

---

## 수정 파일 (11개)

### commands/init-project.md → commands/init.md (이름 변경 + 개선)

변경 내용:
1. 파일명 `init-project.md` → `init.md` (단축)
2. 질문 최적화: Q3(Hook)/Q4(AX)를 Q1 하위로 흡수
3. Git URL을 필수에서 선택으로 이동
4. Q5(백로그) → Q3 승격, TASK.md + tasks/로 영문화
5. 기존 프로젝트 재실행 모드 추가 (설정 변경 메뉴)
6. 자동생성 목록 확장:
   - .claudeignore 생성 (프로젝트 타입별)
   - .claude/commands/ 기본 3개 생성
   - docs/ 표준 폴더 7개 생성
   - apps/ 플랫폼별 폴더 생성
   - 테스트 문서 경로 docs/test/로 변경
7. 완료 리포트에 플러그인 추천 섹션 추가
8. TESTING_FRAMEWORK.md → docs/test/TESTING_FRAMEWORK.md
9. BASELINE.md → docs/test/baseline/{APP}_BASELINE.md (파일명 단축)

### templates/CLAUDE.md.tmpl

변경 내용 (120줄 → ~90줄):
1. §2 횡단 가드레일: API키 금지 1줄 + 빌드번호 SSOT 1줄 병합
2. §3 발견 트리거: RULES_VERSIONING, RULES_PROJECT_LIFECYCLE 행 추가
3. §4 빌드 명령: **삭제** → .claude/commands/build.md로 이동
4. §4 → 문서·폴더 규칙 (신규): MD 파일명 + 폴더 명명 안티패턴 + 완료 보고
5. §6 모노레포: 비모노레포 시 삭제 가능하도록 조건부 표시
6. §7 API 키: **삭제** → §2에 1줄 병합 + INDEX.md에 경로 참조

### templates/CLAUDE.minimal.md.tmpl

변경 내용 (97줄 → ~75줄):
1. §3 코드 수정 원칙: 상세 삭제 → RULES_REFACTORING.md 참조 트리거 1줄
2. 빌드번호 SSOT 1줄 추가
3. 문서·폴더 규칙 섹션 추가 (3줄)

### templates/INDEX.md.tmpl

변경 내용 (73줄 → ~85줄, 재설계):
1. E2E 전용 하드코딩 제거 → 조건부 섹션
2. 프로젝트 구조: apps/ 플랫폼별 구조 반영
3. 빌드 명령 참조 섹션 추가 (CLAUDE.md에서 이동)
4. docs/ 폴더 구조 가이드 + 🚫 폴더 명명 안티패턴
5. 주요 문서 인덱스 섹션 (사용자가 등록)
6. 스크립트·자동화 섹션: 조건부 (E2E 미선택 시 생략)
7. API 키 경로 참조 (CLAUDE.md에서 이동)

### templates/TESTING_FRAMEWORK.md.tmpl

변경 내용 (167줄 → ~130줄):
1. §2 Cross-Lane Destructive Op: 25줄 → 3줄 (RULES_E2E.md 참조)
2. §20.8 baseline_status.py 사용 규약: 15줄 → 5줄 (--help 참조)
3. §20.9 새 플랫폼 추가 체크리스트: 10줄 → 삭제 (init이 자동 생성)
4. 경로 참조 업데이트: docs/test/ 기준

### templates/BASELINE.md.tmpl

변경 내용 (84줄 → ~75줄):
1. 파일명: {APP}_MASTER_TEST_BASELINE.md → {APP}_BASELINE.md
2. 상태 범례 표(7줄): 삭제 → TESTING_FRAMEWORK §20.4 참조 1줄
3. 경로 참조: docs/test/baseline/ 기준

### templates/settings.json.tmpl

변경 내용:
1. enabledPlugins 섹션 추가 (프로젝트 타입별 기본값)
2. 기존 hooks 섹션 유지

### scripts/pre-commit-framework.sh

변경 내용:
1. §(6) 빌드번호 자동 증가 섹션 추가
   - main 브랜치 감지
   - 플랫폼 자동 감지 (iOS project.yml / Android build.gradle / Web package.json)
   - 정본 파일 +1 → git add
2. baseline 관련 경로: docs/test/ 기준으로 업데이트

### docs/design-principles.md

변경 내용:
1. §1 보강: "컨텍스트 예산" 관점 추가
   - 임계치 근거를 "가독성"에서 "컨텍스트 윈도우 유한 자원"으로 확장
   - enabledPlugins 메커니즘 언급
2. 기존 6개 원칙 유지, 신규 원칙 추가하지 않음 (§1 확장으로 처리)

### .claude-plugin/plugin.json

변경 내용:
1. version: "0.2.1" → "0.3.0"

### CHANGELOG.md

변경 내용:
1. v0.3.0 항목 추가

---

## 하위 호환 유지 파일 (5개, 수정 없음)

기존 커맨드 파일은 삭제하지 않고 유지. 내부에서 새 커맨드로 라우팅.

| 파일 | 라우팅 대상 |
|---|---|
| `commands/init-project.md` | → `commands/init.md` |
| `commands/bash-permission.md` | → `commands/init.md --bash` |
| `commands/firebase-isolation.md` | → `commands/init.md --firebase` |
| `commands/slim-claude-md.md` | → `commands/init.md --slim` |
| `commands/doc-size-hook.md` | → `commands/init.md --hook` |

각 파일에 "이 커맨드는 `/init`에 통합되었습니다. 동일 기능 실행 중..." 안내 후 새 커맨드 로직 호출.

`commands/baseline-review.md`는 기존 유지 + `/audit --baseline`과 동일 동작 확인.

---

## 구현 우선순위

| 순위 | 항목 | 파일 |
|---|---|---|
| P0 | init 질문 최적화 + 재실행 모드 | commands/init.md |
| P0 | CLAUDE.md 슬림화 | templates/CLAUDE.md.tmpl, CLAUDE.minimal.md.tmpl |
| P0 | .claudeignore + .claude/commands/ | templates/claudeignore.tmpl, templates/commands/*.tmpl |
| P0 | docs/ 폴더 + apps/ 폴더 | commands/init.md (Step 3 확장) |
| P1 | RULES_VERSIONING.md + 빌드번호 hook | templates/rules/RULES_VERSIONING.md.tmpl, scripts/pre-commit-framework.sh |
| P1 | RULES_PROJECT_LIFECYCLE.md | templates/rules/RULES_PROJECT_LIFECYCLE.md.tmpl |
| P1 | INDEX.md 재설계 | templates/INDEX.md.tmpl |
| P1 | TASK.md + tasks/ | templates/task.md.tmpl, templates/task-detail.md.tmpl |
| P2 | /audit 커맨드 | commands/audit.md |
| P2 | /release 커맨드 | commands/release.md |
| P2 | /guide 커맨드 | commands/guide.md |
| P2 | TESTING_FRAMEWORK + BASELINE 이동·슬림화 | templates/*.tmpl |
| P2 | settings.json enabledPlugins | templates/settings.json.tmpl |
| P3 | design-principles.md 보강 | docs/design-principles.md |
| P3 | 하위 호환 라우팅 | commands/{기존 5개}.md |
| P3 | plugin.json + CHANGELOG | .claude-plugin/plugin.json, CHANGELOG.md |
