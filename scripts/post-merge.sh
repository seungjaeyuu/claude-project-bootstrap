#!/bin/bash
# Git post-merge hook
#
# project.yml 이 merge 에 포함되었으면 .xcodeproj 자동 재생성.
# Xcode 에 표시되는 빌드번호가 project.yml 과 항상 일치하도록 보장.
#
# 🚫 이 hook 에서는 빌드번호를 증가시키지 않음 — pre-commit hook 과의 이중 증가 방지.
#    빌드번호 증가는 후속 커밋의 pre-commit hook 이 담당.
#
# 설치:
#   ln -s ../../scripts/post-merge.sh .git/hooks/post-merge

ROOT="$(git rev-parse --show-toplevel)"

# project.yml 경로 자동 탐색
PROJYML=""
for candidate in "iOS/project.yml" "project.yml" "app/project.yml"; do
  if [ -f "$ROOT/$candidate" ]; then
    PROJYML="$candidate"
    break
  fi
done

if [ -n "$PROJYML" ] && git diff-tree -r --name-only --no-commit-id ORIG_HEAD HEAD | grep -q "^$PROJYML$"; then
  PROJYML_DIR="$(dirname "$ROOT/$PROJYML")"
  if command -v xcodegen &>/dev/null; then
    echo "🔄 project.yml 변경 감지 — .xcodeproj 재생성 중..."
    (cd "$PROJYML_DIR" && xcodegen generate --quiet 2>/dev/null)
    echo "✅ .xcodeproj 재생성 완료"
  else
    echo "⚠️  project.yml 이 변경되었으나 xcodegen 미설치. 수동 실행: cd $(basename "$PROJYML_DIR") && xcodegen generate"
  fi
fi
