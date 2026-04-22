#!/bin/bash
# PROJECT_FRAMEWORK Hook 원클릭 설치
#
# 사용:
#   bash ~/Documents/GitHub/_PROJECT_FRAMEWORK/hooks/install-hooks.sh
#
# 이 스크립트가 하는 일:
#   1. Git pre-commit hook symlink 설치 (scripts/pre-commit-framework.sh → .git/hooks/pre-commit)
#   2. .claude/settings.json 템플릿 복사 (없을 때만)
#   3. .secret/ 폴더 생성 + .gitignore 확인
#
# 이미 설치된 항목은 건너뜀.

set -e

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [ -z "$ROOT" ]; then
  echo "❌ Git 저장소 안에서 실행해야 합니다."
  exit 1
fi

FRAMEWORK="$(cd "$(dirname "$0")/.." && pwd)"
echo "📁 프로젝트 루트: $ROOT"
echo "📁 프레임워크: $FRAMEWORK"
echo ""

# ─────────────────────────────────────────────────────────────
# 1. Git pre-commit hook
# ─────────────────────────────────────────────────────────────
HOOK_DIR="$ROOT/.git/hooks"
if [ ! -d "$HOOK_DIR" ]; then
  HOOK_DIR="$(git rev-parse --git-common-dir)/hooks"
fi
HOOK_LINK="$HOOK_DIR/pre-commit"
HOOK_TARGET="$ROOT/scripts/pre-commit-framework.sh"

# scripts/pre-commit-framework.sh 가 없으면 복사
if [ ! -f "$HOOK_TARGET" ]; then
  mkdir -p "$ROOT/scripts"
  cp "$FRAMEWORK/hooks/pre-commit-framework.sh" "$HOOK_TARGET"
  chmod +x "$HOOK_TARGET"
  echo "✅ scripts/pre-commit-framework.sh 복사"
fi

if [ -L "$HOOK_LINK" ]; then
  echo "ℹ️  pre-commit hook 이미 설치됨: $(readlink "$HOOK_LINK")"
elif [ -e "$HOOK_LINK" ]; then
  echo "⚠️  pre-commit hook 이 이미 있음 (symlink 아님). 수동 확인 권장."
else
  ln -sf "../../scripts/pre-commit-framework.sh" "$HOOK_LINK"
  echo "✅ Git pre-commit hook 설치"
fi

# ─────────────────────────────────────────────────────────────
# 2. .claude/settings.json
# ─────────────────────────────────────────────────────────────
CC_DIR="$ROOT/.claude"
CC_SETTINGS="$CC_DIR/settings.json"
if [ -f "$CC_SETTINGS" ]; then
  echo "ℹ️  .claude/settings.json 이미 존재 — 건너뜀"
else
  mkdir -p "$CC_DIR"
  cp "$FRAMEWORK/hooks/settings.json.template" "$CC_SETTINGS"
  echo "✅ .claude/settings.json 초기화 — matcher regex 를 프로젝트 UI 경로에 맞게 수정하세요"
fi

# ─────────────────────────────────────────────────────────────
# 3. 검증 스크립트 복사 (없을 때만)
# ─────────────────────────────────────────────────────────────
for script in check_dict_duplicates.py check_accessibility_identifiers.py check_baseline_sync.py baseline_status.py baseline_update_suggest.py; do
  if [ ! -f "$ROOT/scripts/$script" ] && [ -f "$FRAMEWORK/scripts/$script" ]; then
    cp "$FRAMEWORK/scripts/$script" "$ROOT/scripts/$script"
    chmod +x "$ROOT/scripts/$script"
    echo "✅ scripts/$script 복사"
  fi
done

# baseline.yml.template → baseline.yml (없을 때만)
if [ ! -f "$ROOT/scripts/baseline.yml" ]; then
  cp "$FRAMEWORK/scripts/baseline.yml.template" "$ROOT/scripts/baseline.yml"
  echo "✅ scripts/baseline.yml 초기화 — apps 를 프로젝트에 맞게 수정하세요"
fi

# ─────────────────────────────────────────────────────────────
# 4. .secret/ 폴더 + .gitignore 확인
# ─────────────────────────────────────────────────────────────
mkdir -p "$ROOT/.secret"
if [ ! -f "$ROOT/.secret/.gitkeep" ]; then
  touch "$ROOT/.secret/.gitkeep"
fi

if [ -f "$ROOT/.gitignore" ]; then
  if ! grep -q "^\.secret/" "$ROOT/.gitignore"; then
    echo "⚠️  .gitignore 에 .secret/ 패턴 없음 — _PROJECT_FRAMEWORK/.gitignore.template 참고 후 수동 추가 필요"
  fi
else
  cp "$FRAMEWORK/.gitignore.template" "$ROOT/.gitignore"
  echo "✅ .gitignore 초기화 (.gitignore.template 기반)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Hook 설치 완료. 다음 단계:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. scripts/baseline.yml 의 apps 를 프로젝트에 맞게 수정"
echo "2. .claude/settings.json 의 matcher regex 확인"
echo "3. BASELINE.md 생성 (_PROJECT_FRAMEWORK/BASELINE_TEMPLATE.md 참조)"
echo "4. 테스트 커밋으로 hook 동작 확인"
