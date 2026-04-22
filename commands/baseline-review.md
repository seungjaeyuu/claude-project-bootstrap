---
description: 베이스라인 갱신 제안 조회 (Git diff 기반, TESTING_FRAMEWORK.md §20.7)
argument-hint: [--app ios|android|...] [--since 14days]
allowed-tools: Read, Edit, Bash(python3:*), Bash(git:*)
---

# /baseline-review — 베이스라인 동기화 검토

사용자 트리거 (E2E 테스트 세션 시작 / 릴리스 준비 / 정기 점검) 시 호출되는 slash command.

## 실행 절차

1. **스크립트 실행** — 사용자 인자를 그대로 전달:

   ```bash
   python3 scripts/baseline_update_suggest.py $ARGUMENTS
   ```

   인자 없으면 기본값 (`default_app`, 최근 14일) 사용.

2. **출력 분석** — 다음 3가지를 확인:
   - UI/Service 변경 파일 목록 + 관련 커밋 메시지
   - 해당 앱 baseline 의 최근 수정일과 UI 변경 시점의 gap
   - 변경 성격 분류 (신규 기능 / 기존 수정 / 폐기)

3. **사용자에게 요약 보고** — 너무 길면 주요 변경만 간추림.

4. **제안 생성** — 각 UI 변경에 대해:
   - 기존 baseline ID 에 해당하는가? (커밋 메시지 패턴, 파일 경로, `scripts/baseline_status.py --id <ID>` 로 확인)
   - 신규 ID 가 필요한가? (Template A/B 중 어느 섹션에 들어가야 하는가)
   - "재검증 필요" 표기만으로 충분한가?

5. **사용자 승인 대기** — 사용자가 반영할 항목을 선택할 때까지 baseline 편집하지 않는다.

6. **승인 후 일괄 반영** — [TESTING_FRAMEWORK.md §20.7](../../TESTING_FRAMEWORK.md) 규약 준수:
   - 신규 기능 → Template A 또는 B 중 섹션 성격에 맞게 행 추가
   - 기존 수정 → 해당 ID 를 "재검증 필요" 로 표기
   - 삭제/폐기 → `deprecated` 표기 (행 삭제 금지)
   - 커밋 메시지에 기준 ID 명시 (예: `docs(baseline): CONS-01 신규 추가`)

## 참조 문서

- [TESTING_FRAMEWORK.md §20.7](../../TESTING_FRAMEWORK.md) — 업데이트 의무
- [TESTING_FRAMEWORK.md §20.4](../../TESTING_FRAMEWORK.md) — Template A/B/C 스키마
- [TESTING_FRAMEWORK.md §20.8](../../TESTING_FRAMEWORK.md) — 스크립트 사용 규약

## 관련 명령

- `python3 scripts/baseline_status.py --app <name> --id <ID>` — 현재 판정 확인
- `python3 scripts/baseline_status.py --app <name> --expected <ID>` — 기준 항목 추출
- `python3 scripts/baseline_status.py --app <name> --by-prefix` — 현 집계
