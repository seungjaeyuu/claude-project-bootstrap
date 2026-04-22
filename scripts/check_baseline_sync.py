#!/usr/bin/env python3
"""check_baseline_sync.py — pre-commit hook 보조.

TESTING_FRAMEWORK.md §20.7 L1 구현.
Staged UI 파일이 있는데 해당 앱의 baseline 이 같은 커밋에 없으면 **경고 출력**
(차단 아님). baseline.yml 의 ui_file_patterns 로 멀티앱 자동 대응.

exit code: 항상 0 (경고만, 커밋 차단하지 않음).
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    # pyyaml 없으면 조용히 건너뜀 (hook 방해 금지)
    sys.exit(0)


ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "scripts" / "baseline.yml"


def staged_files() -> list[str]:
    r = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=AM"],
        capture_output=True, text=True, check=False, cwd=str(ROOT),
    )
    return [l.strip() for l in r.stdout.splitlines() if l.strip()]


def main() -> int:
    if not CONFIG.exists():
        return 0
    try:
        with open(CONFIG, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception:
        return 0

    staged = staged_files()
    if not staged:
        return 0

    any_warned = False
    for app_name, cfg in (data.get("apps") or {}).items():
        if cfg is None:
            continue
        patterns = [re.compile(p) for p in cfg.get("ui_file_patterns", [])]
        if not patterns:
            continue

        ui_hits = [f for f in staged if any(p.search(f) for p in patterns)]
        if not ui_hits:
            continue

        baseline = cfg.get("baseline")
        if not baseline:
            continue
        if baseline in staged:
            continue  # baseline 도 같이 staged — OK

        any_warned = True
        print(f"\n⚠️  baseline 동기화 경고 ({app_name}) — TESTING_FRAMEWORK §20.7 L1", file=sys.stderr)
        print(f"   UI 파일 {len(ui_hits)} 건 staged, {baseline} 미갱신:", file=sys.stderr)
        for f in ui_hits[:3]:
            print(f"     - {f}", file=sys.stderr)
        if len(ui_hits) > 3:
            print(f"     ... + {len(ui_hits) - 3} 건", file=sys.stderr)
        print(f"   권장: /baseline-review --app {app_name}", file=sys.stderr)

    if any_warned:
        print(f"   (경고만 — 커밋 진행됨. 필요 시 --no-verify 없이 baseline 반영 후 재커밋)\n", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
