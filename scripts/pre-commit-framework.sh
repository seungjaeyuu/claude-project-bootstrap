#!/bin/bash
# Git pre-commit hook (PROJECT_FRAMEWORK 기본 템플릿)
#
# 검사 항목:
#   (1) Swift/Kotlin/TS dictionary literal 중복 키 (차단)
#   (2) Accessibility identifier 스키마/중복 (차단, Swift 파일 감지 시)
#   (3) 베이스라인 동기화 경고 (경고만, TESTING_FRAMEWORK §20.7 L1)
#   (5) plugin.json ↔ marketplace.json 버전 동기화 (차단)
#
# 각 검사는 해당 스크립트가 scripts/ 에 있을 때만 실행.
# 프로젝트별로 불필요한 언어 검사는 grep 패턴 수정 또는 해당 블록 제거.
#
# 설치:
#   ln -s ../../scripts/pre-commit-framework.sh .git/hooks/pre-commit
#   또는 _PROJECT_FRAMEWORK/hooks/install-hooks.sh 실행

set -e

ROOT="$(git rev-parse --show-toplevel)"
DICT_SCRIPT="$ROOT/scripts/check_dict_duplicates.py"
ACCESSIBILITY_SCRIPT="$ROOT/scripts/check_accessibility_identifiers.py"
SYNC_SCRIPT="$ROOT/scripts/check_baseline_sync.py"

EXIT=0

# ─────────────────────────────────────────────────────────────
# (1) Dictionary literal 중복 키 (Swift/Kotlin/TS)
# ─────────────────────────────────────────────────────────────
if [ -f "$DICT_SCRIPT" ]; then
  FILES=$(git diff --cached --name-only --diff-filter=AM | grep -E '\.(swift|kt|ts|tsx)$' || true)
  if [ -n "$FILES" ]; then
    echo "🔍 Dictionary literal 중복 키 검사..."
    if ! echo "$FILES" | xargs python3 "$DICT_SCRIPT" --quiet; then
      echo ""
      echo "❌ 커밋 차단: dictionary literal 중복 키 발견"
      EXIT=1
    fi
  fi
fi

# ─────────────────────────────────────────────────────────────
# (2) Accessibility identifier 스키마 (Swift 기본; 프로젝트별 조정)
# ─────────────────────────────────────────────────────────────
if [ -f "$ACCESSIBILITY_SCRIPT" ]; then
  SWIFT_FILES=$(git diff --cached --name-only --diff-filter=AM | grep -E '\.swift$' || true)
  if [ -n "$SWIFT_FILES" ]; then
    echo "🔍 Accessibility identifier 스키마 검증..."
    if ! echo "$SWIFT_FILES" | xargs python3 "$ACCESSIBILITY_SCRIPT" --quiet; then
      echo ""
      echo "❌ 커밋 차단: accessibility identifier 스키마/중복 위반"
      echo "   가이드: /ACCESSIBILITY_IDENTIFIERS.md"
      EXIT=1
    fi
  fi
fi

# ─────────────────────────────────────────────────────────────
# (3) 베이스라인 동기화 경고 (차단 아님)
# ─────────────────────────────────────────────────────────────
if [ -f "$SYNC_SCRIPT" ]; then
  python3 "$SYNC_SCRIPT" || true
fi

# ─────────────────────────────────────────────────────────────
# (4) 문서 크기 경고 (차단 아님) — claude-project-bootstrap v0.2.0+
# ─────────────────────────────────────────────────────────────
DOC_SIZE_SCRIPT="$ROOT/scripts/check_doc_size.py"
if [ -f "$DOC_SIZE_SCRIPT" ]; then
  python3 "$DOC_SIZE_SCRIPT" "$ROOT" || true
fi

# ─────────────────────────────────────────────────────────────
# (5) plugin.json ↔ marketplace.json 버전 동기화 (차단)
# ─────────────────────────────────────────────────────────────
VERSION_SYNC_SCRIPT="$ROOT/scripts/check_version_sync.py"
if [ -f "$VERSION_SYNC_SCRIPT" ]; then
  STAGED_JSON=$(git diff --cached --name-only | grep -E '(plugin|marketplace)\.json$' || true)
  if [ -n "$STAGED_JSON" ]; then
    echo "🔍 plugin.json ↔ marketplace.json 버전 동기화 검사..."
    if ! python3 "$VERSION_SYNC_SCRIPT"; then
      EXIT=1
    fi
  fi
fi

exit $EXIT
