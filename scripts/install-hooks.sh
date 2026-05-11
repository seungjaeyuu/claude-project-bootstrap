#!/bin/bash
# claude-project-bootstrap Hook 원클릭 설치
#
# 사용 (플러그인 내부):
#   bash ${CLAUDE_PLUGIN_ROOT}/scripts/install-hooks.sh
#
# 사용 (수동 실행):
#   스크립트가 위치한 플러그인 루트를 자동 추론
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

# 플러그인 설치 시: ${CLAUDE_PLUGIN_ROOT} 사용
# 수동 실행 시: 스크립트의 자기 상위 디렉토리 (scripts/ → 플러그인 루트)
FRAMEWORK="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
echo "📁 프로젝트 루트: $ROOT"
echo "📁 플러그인 루트: $FRAMEWORK"
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
  cp "$FRAMEWORK/scripts/pre-commit-framework.sh" "$HOOK_TARGET"
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
# 1-2. Git post-merge hook (XcodeGen xcodeproj 재생성)
# ─────────────────────────────────────────────────────────────
POST_MERGE_LINK="$HOOK_DIR/post-merge"
POST_MERGE_TARGET="$ROOT/scripts/post-merge.sh"

if [ ! -f "$POST_MERGE_TARGET" ] && [ -f "$FRAMEWORK/scripts/post-merge.sh" ]; then
  cp "$FRAMEWORK/scripts/post-merge.sh" "$POST_MERGE_TARGET"
  chmod +x "$POST_MERGE_TARGET"
  echo "✅ scripts/post-merge.sh 복사"
fi

if [ -L "$POST_MERGE_LINK" ]; then
  echo "ℹ️  post-merge hook 이미 설치됨: $(readlink "$POST_MERGE_LINK")"
elif [ -e "$POST_MERGE_LINK" ]; then
  echo "⚠️  post-merge hook 이 이미 있음 (symlink 아님). 수동 확인 권장."
else
  ln -sf "../../scripts/post-merge.sh" "$POST_MERGE_LINK"
  echo "✅ Git post-merge hook 설치"
fi

# ─────────────────────────────────────────────────────────────
# 2. 검증 스크립트 복사 (없을 때만)
# ─────────────────────────────────────────────────────────────
# 주의: .claude/settings.json (Claude Code PostToolUse hook) 은 본 스크립트에서
# 복사하지 않음. 대신 /init-project 커맨드가 Q4 (Accessibility identifier 검증)
# 답변에 따라 조건부로 별도 복사함. 이유: Q4 No 인 프로젝트에 AX hook 을 주면
# 무의미 + 잠재적 혼란.
for script in check_dict_duplicates.py check_accessibility_identifiers.py check_baseline_sync.py baseline_status.py baseline_update_suggest.py posttooluse_ax_check.py check_doc_size.py check_firebase_project.py; do
  if [ ! -f "$ROOT/scripts/$script" ] && [ -f "$FRAMEWORK/scripts/$script" ]; then
    cp "$FRAMEWORK/scripts/$script" "$ROOT/scripts/$script"
    chmod +x "$ROOT/scripts/$script"
    echo "✅ scripts/$script 복사"
  fi
done

# baseline.yml.tmpl → baseline.yml (없을 때만)
if [ ! -f "$ROOT/scripts/baseline.yml" ]; then
  cp "$FRAMEWORK/templates/baseline.yml.tmpl" "$ROOT/scripts/baseline.yml"
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
    echo "⚠️  .gitignore 에 .secret/ 패턴 없음 — ${CLAUDE_PLUGIN_ROOT:-플러그인}/templates/gitignore.tmpl 참고 후 수동 추가 필요"
  fi
else
  cp "$FRAMEWORK/templates/gitignore.tmpl" "$ROOT/.gitignore"
  echo "✅ .gitignore 초기화 (gitignore.tmpl 기반)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Hook 설치 완료. 다음 단계:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. scripts/baseline.yml 의 apps 를 프로젝트에 맞게 수정"
echo "2. BASELINE.md 생성 (플러그인 templates/BASELINE.md.tmpl 참조)"
echo "3. 테스트 커밋으로 Git pre-commit hook 동작 확인"
echo "   (Claude Code PostToolUse hook 은 초기 프로젝트 설정 시 Q4=Yes 선택 시 별도 설치됨)"
