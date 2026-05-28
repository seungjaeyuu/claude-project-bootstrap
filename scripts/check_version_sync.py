#!/usr/bin/env python3
"""plugin.json ↔ marketplace.json 버전 동기화 검증.

pre-commit hook 에서 호출. 두 파일의 version 이 다르면 비-0 종료.
"""

import json
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    plugin_path = root / ".claude-plugin" / "plugin.json"
    marketplace_path = root / ".claude-plugin" / "marketplace.json"

    if not plugin_path.exists():
        print(f"⚠ {plugin_path.relative_to(root)} 없음 — 건너뜀", file=sys.stderr)
        return 0
    if not marketplace_path.exists():
        print(f"⚠ {marketplace_path.relative_to(root)} 없음 — 건너뜀", file=sys.stderr)
        return 0

    plugin_ver = json.loads(plugin_path.read_text(encoding="utf-8")).get("version", "")
    mp_data = json.loads(marketplace_path.read_text(encoding="utf-8"))
    mp_ver = ""
    for p in mp_data.get("plugins", []):
        if p.get("name") == "claude-project-bootstrap":
            mp_ver = p.get("version", "")
            break

    if not mp_ver:
        print("⚠ marketplace.json 에서 claude-project-bootstrap 플러그인 미발견", file=sys.stderr)
        return 1

    if plugin_ver != mp_ver:
        print(f"❌ 버전 불일치: plugin.json={plugin_ver}  marketplace.json={mp_ver}", file=sys.stderr)
        print("   scripts/release.sh <version> 으로 양쪽 동시 갱신하세요.", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
