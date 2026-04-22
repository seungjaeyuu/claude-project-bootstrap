# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-04-23

### Added

**슬래시 커맨드 2개** (네임스페이스: `/claude-project-bootstrap:*`)
- `init-project` — 새 프로젝트 초기화 (대화형 Q1~Q5 + Q1a 앱 타입 선택)
- `baseline-review` — Git diff 기반 베이스라인 갱신 제안

**템플릿 7개** (`templates/*.tmpl`)
- `CLAUDE.md.tmpl` — 네거티브 우선 + 4층 규칙 범례
- `INDEX.md.tmpl` — 프로젝트 지도
- `TESTING_FRAMEWORK.md.tmpl` — E2E 하네스 규약 (§20 베이스라인)
- `BASELINE.md.tmpl` — 3 Template (A/B/C) 구조
- `baseline.yml.tmpl` — 멀티플랫폼 베이스라인 설정
- `settings.json.tmpl` — Claude Code PostToolUse hook
- `gitignore.tmpl` — 보안·생성물 보호 패턴

**Python 검증 스크립트 5개** (target 프로젝트로 복사)
- `baseline_status.py` — 베이스라인 판정 상태 집계
- `baseline_update_suggest.py` — Git diff 기반 베이스라인 갱신 제안
- `check_baseline_sync.py` — pre-commit UI 파일·baseline 동기화 검사
- `check_accessibility_identifiers.py` — SwiftUI accessibility 라벨 스키마 검증
- `check_dict_duplicates.py` — Swift/Kotlin/TypeScript dict literal 중복 키 검출

**Hook 스크립트 2개**
- `install-hooks.sh` — Git pre-commit + `.claude/settings.json` 원클릭 설치 (플러그인 내부 실행)
- `pre-commit-framework.sh` — Git pre-commit (target 프로젝트로 symlink)

**문서 3개**
- `docs/design-principles.md` — 6개 공개 설계 원칙 (네거티브 우선, 3-Template 규약, status.json canonical, 이중 배치 지양, baseline.yml entry 활성화, 트리거 기반 동기화)
- `docs/changelog-decisions.md` — 5개 내부 결정 로그
- `docs/migration-guide.md` — 기존 `_PROJECT_FRAMEWORK` 사용자 이관 가이드

### Notes

- v0.1.0 은 Claude Code v2.1.117 기준 로컬 검증 9/9 통과
- 커맨드는 `/claude-project-bootstrap:init-project` 형식 (plugin-name prefix 필수)
- `${CLAUDE_PLUGIN_ROOT}` 변수 기반 이식성 확보
- 4개 개선 과제는 v0.2 로드맵 (GitHub Issues #1-#4)

## [Unreleased]

다음 릴리스 예정 개선사항:
- Minimal/Standard/Full 3-tier CLAUDE.md 템플릿 (#1)
- `/init-project` 옵션 질의 상세화 (#2)
- 완료 리포트 간소화 (#3)
- PostToolUse hook 경고 표시 개선 (#4)
