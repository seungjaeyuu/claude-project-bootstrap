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

## [Unreleased]

다음 릴리스 예정 개선사항:
- Claude Code argument UI 제약 대응 — 4줄 설명 노출 방안 (#5)
- "Q1"~"Q5" 축약 표기 → 풀어쓴 설명으로 교체 (#6)
