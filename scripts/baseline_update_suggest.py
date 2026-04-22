#!/usr/bin/env python3
"""baseline_update_suggest.py — Git diff 기반 베이스라인 갱신 제안.

TESTING_FRAMEWORK.md §20.7 — "매 수정마다 갱신" 대신 **트리거 시점 (테스트 세션
시작 / 릴리스 준비) 에 일괄 검토**. 본 스크립트가 그 일괄 검토의 자동 제안 담당.

사용 예:
  baseline_update_suggest.py                    # default app, 최근 14일
  baseline_update_suggest.py --app ios --since 7days
  baseline_update_suggest.py --all-apps
  baseline_update_suggest.py --since 2026-04-01

의존성: python >= 3.8, pyyaml, git
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.stderr.write("❌ pyyaml 미설치: pip3 install pyyaml\n")
    sys.exit(2)


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = REPO_ROOT / "scripts" / "baseline.yml"


@dataclass
class AppCfg:
    name: str
    baseline: str
    ui_file_patterns: list[str]


def load_apps(config: Path) -> tuple[str, dict[str, AppCfg]]:
    if not config.exists():
        sys.stderr.write(f"❌ 설정 파일 없음: {config}\n")
        sys.exit(2)
    data = yaml.safe_load(config.read_text(encoding="utf-8"))
    default = data.get("default_app", "ios")
    apps: dict[str, AppCfg] = {}
    for name, cfg in (data.get("apps") or {}).items():
        if cfg is None:
            continue
        apps[name] = AppCfg(
            name=name,
            baseline=cfg["baseline"],
            ui_file_patterns=cfg.get("ui_file_patterns", []),
        )
    return default, apps


def git(*args: str) -> str:
    try:
        r = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            check=False,
        )
        return r.stdout
    except FileNotFoundError:
        sys.stderr.write("❌ git 명령 없음. Git 설치 필요.\n")
        sys.exit(2)


def normalize_since(since: str) -> str:
    """git log --since 에 그대로 전달 가능하도록 가공. 숫자만 입력 시 days 기본."""
    s = since.strip()
    if re.fullmatch(r"\d+", s):
        return f"{s}.days.ago"
    m = re.fullmatch(r"(\d+)\s*days?", s)
    if m:
        return f"{m.group(1)}.days.ago"
    return s  # ISO 8601 (YYYY-MM-DD) 등은 git 이 직접 해석


def collect_commits(since: str) -> list[dict[str, str]]:
    """최근 커밋 목록 (hash, date, subject, files)."""
    raw = git(
        "log",
        f"--since={since}",
        "--name-only",
        "--pretty=format:__COMMIT__%n%h|%ai|%s",
        "--no-merges",
    )
    commits = []
    blocks = raw.split("__COMMIT__")
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines = block.splitlines()
        header = lines[0]
        files = [l.strip() for l in lines[1:] if l.strip()]
        try:
            h, date, subject = header.split("|", 2)
        except ValueError:
            continue
        commits.append({
            "hash": h,
            "date": date[:10],
            "subject": subject,
            "files": files,
        })
    return commits


def match_files(patterns: list[str], files: list[str]) -> list[str]:
    compiled = [re.compile(p) for p in patterns]
    return [f for f in files if any(c.search(f) for c in compiled)]


def last_baseline_change_date(baseline: str, since: str) -> str | None:
    out = git(
        "log",
        f"--since={since}",
        "--pretty=format:%ai",
        "--",
        baseline,
    ).strip()
    if not out:
        return None
    return out.splitlines()[0][:10]


# ─────────────────────────────────────────────────────────────────────────────

def suggest_for_app(app: AppCfg, since: str) -> str:
    commits = collect_commits(since)

    # 앱 UI 변경 누적
    ui_commits: list[dict[str, str]] = []
    ui_files_by_file: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for c in commits:
        matched = match_files(app.ui_file_patterns, c["files"])
        if not matched:
            continue
        ui_commits.append({**c, "matched_files": matched})
        for f in matched:
            ui_files_by_file[f].append((c["date"], c["hash"], c["subject"]))

    # baseline 자체 변경 여부
    baseline_last = last_baseline_change_date(app.baseline, since)

    lines = [f"=== baseline 갱신 제안 — {app.name} (최근 {since}) ==="]

    if not ui_commits:
        lines.append("  ✅ UI/Service 변경 없음. 갱신 검토 불필요.")
        return "\n".join(lines)

    # 1. UI 변경 파일 목록
    lines.append("")
    lines.append(f"📦 UI/Service 변경 감지 ({len(ui_files_by_file)} 파일, {len(ui_commits)} 커밋):")
    for f in sorted(ui_files_by_file.keys()):
        recs = ui_files_by_file[f]
        lines.append(f"  {f}")
        for date, h, subj in recs[:3]:
            lines.append(f"    {date}  {h}  {subj[:70]}")
        if len(recs) > 3:
            lines.append(f"    … + {len(recs) - 3} 커밋")

    # 2. baseline 갱신 여부
    lines.append("")
    lines.append("🔍 baseline 갱신 여부:")
    if baseline_last:
        lines.append(f"  {app.baseline} — 최근 수정: {baseline_last}")
        # 마지막 UI 변경 날짜와 비교
        last_ui_date = max(c["date"] for c in ui_commits)
        if last_ui_date > baseline_last:
            gap_files = sum(
                1 for f, recs in ui_files_by_file.items()
                if max(r[0] for r in recs) > baseline_last
            )
            lines.append(f"  ⚠️  baseline 최종 수정({baseline_last}) 이후 UI 변경: {gap_files} 파일")
        else:
            lines.append(f"  ✅ baseline 이 최신 UI 변경({last_ui_date}) 이후에 수정됨")
    else:
        lines.append(f"  ⚠️  {app.baseline} — 최근 {since} 동안 수정 없음")
        lines.append(f"     (하지만 UI 는 {len(ui_commits)} 건 변경)")

    # 3. 권장
    lines.append("")
    lines.append("⏰ 권장 액션:")
    lines.append("  1. 위 UI 변경 중 '신규 기능' 항목 → baseline 에 ID 추가 (Template A 또는 B)")
    lines.append("  2. '수정' 항목 → 해당 ID 를 '재검증 필요' 로 표기")
    lines.append("  3. '삭제/폐기' → deprecated 표기")
    lines.append("  4. 변경 사항은 같은 커밋에 baseline 파일과 함께 반영 권장")
    lines.append("")
    lines.append(f"  상세 규약: TESTING_FRAMEWORK.md §20.7")
    lines.append(f"  집계 조회: python3 scripts/baseline_status.py --app {app.name} --by-prefix")

    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(
        description="Git diff 기반 베이스라인 갱신 제안. TESTING_FRAMEWORK.md §20.7.",
    )
    p.add_argument("--app", help="앱 이름. 미지정 시 default_app.")
    p.add_argument("--all-apps", action="store_true", help="모든 활성 앱 검토.")
    p.add_argument(
        "--since",
        default="14.days.ago",
        help="기간. 예: '14.days.ago', '7days', '2026-04-01'. 기본 14일.",
    )
    p.add_argument("--config", default=str(DEFAULT_CONFIG))
    args = p.parse_args()

    since = normalize_since(args.since)
    default, apps = load_apps(Path(args.config))
    if not apps:
        sys.stderr.write("⚠️  활성 앱 없음 — baseline.yml 확인\n")
        return 1

    if args.all_apps:
        selected = list(apps.values())
    else:
        name = args.app or default
        if name not in apps:
            sys.stderr.write(f"❌ '{name}' 앱 없음 (활성: {', '.join(apps)})\n")
            return 2
        selected = [apps[name]]

    outs = [suggest_for_app(a, since) for a in selected]
    print("\n\n".join(outs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
