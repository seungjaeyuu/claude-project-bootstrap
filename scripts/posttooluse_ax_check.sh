#!/bin/bash
# PostToolUse hook wrapper — accessibility identifier 검증
#
# Claude Code 의 .claude/settings.json PostToolUse hook 에서 호출.
# Edit/Write/MultiEdit 직후 UI 파일 (apps/.*\.(swift|kt|tsx)$) 매칭 시 실행.
#
# 인자:
#   $1 — $CLAUDE_TOOL_FILE_PATH (편집된 파일 경로)
#
# 동작:
#   - UI 파일 아닌 경우 조용히 종료
#   - check_accessibility_identifiers.py 실행 (non-quiet 모드)
#   - 위반 (exit 1) 감지 시 → systemMessage 로 경고 + 상세 출력
#   - 경고만 있을 때 (exit 0 + 경고 리포트) → systemMessage 로 경고 요약
#   - 둘 다 없으면 완전 조용
#
# 설계 원칙: Claude Code UI 가시화를 위해 stdout 에 반드시 출력.

set -u

FILE_PATH="${1:-}"

# 인자 없거나 UI 파일 아닌 경우 조용히 종료
if [ -z "$FILE_PATH" ]; then
  exit 0
fi
if ! echo "$FILE_PATH" | grep -qE 'apps/.*\.(swift|kt|tsx)$'; then
  exit 0
fi

SCRIPT="$CLAUDE_PROJECT_DIR/scripts/check_accessibility_identifiers.py"
if [ ! -f "$SCRIPT" ]; then
  # 스크립트 미설치 — 조용히 종료
  exit 0
fi

# non-quiet 모드로 실행해 전체 리포트 확보
OUTPUT=$(python3 "$SCRIPT" "$FILE_PATH" 2>&1)
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
  # 위반 감지
  echo "⚠️ accessibility identifier 위반 감지: $FILE_PATH"
  echo "$OUTPUT" | tail -20
  echo ""
  echo "→ 가이드: /ACCESSIBILITY_IDENTIFIERS.md"
  echo "→ 상세: python3 scripts/check_accessibility_identifiers.py $FILE_PATH"
  exit 0  # hook 자체는 성공 처리 (차단 아님, 경고만)
elif echo "$OUTPUT" | grep -qE '경고 \(.*\): [1-9]'; then
  # 경고 있음 (exit 0 이지만 informational)
  WARNING_COUNT=$(echo "$OUTPUT" | grep -oE '경고 \([^)]+\): [0-9]+' | head -1)
  echo "💡 $FILE_PATH — $WARNING_COUNT"
  echo "→ 상세: python3 scripts/check_accessibility_identifiers.py $FILE_PATH"
fi
# 위반·경고 모두 없으면 완전 조용
