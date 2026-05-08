#!/bin/bash
# 릴리스 원클릭 스크립트
#
# 사용법: scripts/release.sh <new_version>
#   예: scripts/release.sh 0.3.0
#
# 수행 항목:
#   1. plugin.json version 갱신
#   2. marketplace.json plugins[0].version 갱신
#   3. CHANGELOG.md [Unreleased] → [<version>] - <date> 변환
#   4. git add + commit + tag

set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Usage: $0 <new_version>"
  echo "  예: $0 0.3.0"
  exit 1
fi

NEW_VER="$1"
ROOT="$(git rev-parse --show-toplevel)"
PLUGIN_JSON="$ROOT/.claude-plugin/plugin.json"
MARKETPLACE_JSON="$ROOT/.claude-plugin/marketplace.json"
CHANGELOG="$ROOT/CHANGELOG.md"
TODAY=$(date +%Y-%m-%d)

if [[ ! "$NEW_VER" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "❌ 유효하지 않은 버전 형식: $NEW_VER (expected: X.Y.Z)"
  exit 1
fi

OLD_VER=$(python3 -c "import json; print(json.load(open('$PLUGIN_JSON'))['version'])")
echo "📦 $OLD_VER → $NEW_VER"

# 1) plugin.json
python3 -c "
import json, pathlib
p = pathlib.Path('$PLUGIN_JSON')
d = json.loads(p.read_text())
d['version'] = '$NEW_VER'
p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + '\n')
"
echo "  ✅ plugin.json"

# 2) marketplace.json
python3 -c "
import json, pathlib
p = pathlib.Path('$MARKETPLACE_JSON')
d = json.loads(p.read_text())
for plugin in d.get('plugins', []):
    if plugin.get('name') == 'claude-project-bootstrap':
        plugin['version'] = '$NEW_VER'
        break
p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + '\n')
"
echo "  ✅ marketplace.json"

# 3) CHANGELOG.md — [Unreleased] 헤더를 [<version>] - <date> 로 변환하고 새 [Unreleased] 추가
if [ -f "$CHANGELOG" ]; then
  if grep -q '## \[Unreleased\]' "$CHANGELOG"; then
    sed -i '' "s/## \[Unreleased\]/## [Unreleased]\n\n## [$NEW_VER] - $TODAY/" "$CHANGELOG"
    echo "  ✅ CHANGELOG.md ([Unreleased] → [$NEW_VER] - $TODAY)"
  else
    echo "  ⚠ CHANGELOG.md 에 [Unreleased] 섹션 없음 — 수동 편집 필요"
  fi
fi

# 4) 확인 후 커밋 + 태그
echo ""
echo "변경 파일:"
git diff --name-only
echo ""
read -p "커밋 + 태그 v$NEW_VER 생성? (y/N) " CONFIRM
if [[ "$CONFIRM" =~ ^[Yy]$ ]]; then
  git add "$PLUGIN_JSON" "$MARKETPLACE_JSON" "$CHANGELOG"
  git commit -m "chore(release): v$NEW_VER"
  git tag "v$NEW_VER"
  echo ""
  echo "✅ 커밋 + 태그 v$NEW_VER 완료"
  echo "   push: git push origin main --tags"
  echo "   릴리스: gh release create v$NEW_VER --title \"v$NEW_VER — <제목>\" --notes-file -"
else
  echo "⏸ 커밋 건너뜀. 변경사항은 unstaged 상태로 유지."
fi
