#!/usr/bin/env python3
"""baseline_status.py — 멀티플랫폼 베이스라인 상태 조회 도구.

TESTING_FRAMEWORK.md §20.8 규약.
Raw Read 대신 본 스크립트 사용 권장 (대용량 baseline markdown + 다수 status.json 집계).

사용 예:
  baseline_status.py                        # default app 전체 요약
  baseline_status.py --by-prefix            # prefix 별 P/F/B 집계
  baseline_status.py --id PRV-06-R14        # 특정 ID 최신 판정 + 이력
  baseline_status.py --expected PRV-06-R14  # baseline 의 기준 항목 추출
  baseline_status.py --run 20260420         # 파일명 substring 매칭 범위
  baseline_status.py --failed               # 현재 FAIL 상태인 ID
  baseline_status.py --blocked              # 현재 BLOCKED 상태인 ID
  baseline_status.py --app android          # 특정 앱
  baseline_status.py --all-apps --summary   # 모든 활성 앱 교차

의존성:
  python >= 3.8
  pyyaml  (`pip3 install pyyaml`)
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    sys.stderr.write(
        "❌ pyyaml 미설치. 설치 명령:\n"
        "   pip3 install pyyaml\n"
    )
    sys.exit(2)


# ─────────────────────────────────────────────────────────────────────────────
# 설정 로드
# ─────────────────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = REPO_ROOT / "scripts" / "baseline.yml"

KNOWN_STATUS = {"PASS", "FAIL", "BLOCKED", "SKIP"}
# 분류:
#   KNOWN_STATUS = 정상 판정값
#   UNRECORDED   = status 필드가 null 또는 빈 문자열 (테스터 기입 누락)
#   OTHER        = 그 외 예상 외 값 (오타·신규 enum 등)


@dataclass
class AppConfig:
    name: str
    baseline: Path
    status_dir: Path
    ui_file_patterns: list[str]
    exclude_prefixes: list[str]
    runner_field: str
    platform: str

    @classmethod
    def from_dict(cls, name: str, d: dict[str, Any], repo_root: Path) -> "AppConfig":
        return cls(
            name=name,
            baseline=repo_root / d["baseline"],
            status_dir=repo_root / d["status_dir"],
            ui_file_patterns=d.get("ui_file_patterns", []),
            exclude_prefixes=d.get("exclude_prefixes", []),
            runner_field=d.get("runner_field", "runner_id"),
            platform=d.get("platform", "unknown"),
        )


def load_config(path: Path) -> tuple[str, dict[str, AppConfig]]:
    if not path.exists():
        sys.stderr.write(f"❌ 설정 파일 없음: {path}\n")
        sys.exit(2)
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    default_app = data.get("default_app", "ios")
    apps: dict[str, AppConfig] = {}
    for name, cfg in (data.get("apps") or {}).items():
        if cfg is None:
            continue  # commented-out entry
        apps[name] = AppConfig.from_dict(name, cfg, REPO_ROOT)
    return default_app, apps


# ─────────────────────────────────────────────────────────────────────────────
# status.json 파싱
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Record:
    """ID 하나의 단일 status.json 판정 기록."""
    app: str
    id: str
    status: str            # PASS / FAIL / BLOCKED / SKIP / OTHER
    source_file: Path
    mtime: float
    evidence: list[str] = field(default_factory=list)
    note: str = ""
    lane: str | None = None
    charter: str | None = None
    runner_id: str | None = None


def normalize_status(raw) -> str:
    """raw 값 정규화 (TESTING_FRAMEWORK §20.5).

    - None / 빈 문자열 → UNRECORDED (테스터 기입 누락)
    - KNOWN_STATUS 매칭 → 해당 enum
    - 그 외 → OTHER (오타·신규 enum, stderr warning 대상)
    """
    if raw is None:
        return "UNRECORDED"
    s = str(raw).strip().upper()
    if not s:
        return "UNRECORDED"
    if s in KNOWN_STATUS:
        return s
    return "OTHER"


def load_status_records(app: AppConfig, run_tag: str | None = None) -> list[Record]:
    """status_dir 의 모든 *.json 을 순회하여 Record 리스트 생성."""
    records: list[Record] = []
    if not app.status_dir.exists():
        sys.stderr.write(f"⚠️  status_dir 없음: {app.status_dir} ({app.name})\n")
        return records

    pattern = str(app.status_dir / "*.json")
    other_statuses: Counter[str] = Counter()
    matched_files: list[str] = []  # --run 투명성용

    for fp in sorted(glob.glob(pattern)):
        fpath = Path(fp)
        if run_tag and run_tag not in fpath.name:
            continue
        # aborted / preflight_blocked suffix 는 기본 제외 (ambiguous)
        stem_lower = fpath.stem.lower()
        if any(skip in stem_lower for skip in ("_ime_aborted", "_preflight_blocked")):
            continue
        matched_files.append(fpath.name)

        try:
            with open(fpath, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            sys.stderr.write(f"⚠️  파싱 실패: {fpath.name} ({e})\n")
            continue

        mtime = fpath.stat().st_mtime
        lane = data.get("lane")
        charter = data.get("charter")
        runner_id = None
        # Q3/Q4 (D-b 옵션 A): 파일 수정 없이 스크립트가 여러 필드명 흡수
        runner_obj = data.get("runner")
        if isinstance(runner_obj, dict):
            runner_id = runner_obj.get("id")
        if not runner_id:
            runner_id = data.get(app.runner_field) or data.get("udid") or data.get("device_id")

        results = data.get("results") or {}
        if not isinstance(results, dict):
            continue

        for id_, item in results.items():
            if not isinstance(item, dict):
                continue
            raw_status = item.get("status", "")
            status = normalize_status(raw_status)
            if status == "OTHER" and raw_status:
                other_statuses[raw_status] += 1

            records.append(Record(
                app=app.name,
                id=id_,
                status=status,
                source_file=fpath,
                mtime=mtime,
                evidence=item.get("evidence") or [],
                note=item.get("note") or "",
                lane=lane,
                charter=charter,
                runner_id=runner_id,
            ))

    if other_statuses:
        sys.stderr.write(
            f"⚠️  예상 외 status 값 ({app.name}): "
            + ", ".join(f"{k}×{v}" for k, v in other_statuses.items())
            + " — OTHER 로 분류됨\n"
        )
    # --run 투명성 (TESTING_FRAMEWORK §20.8 A+ — 매칭 파일 수 보고)
    if run_tag:
        if not matched_files:
            sys.stderr.write(
                f"⚠️  --run '{run_tag}' 매칭 파일 없음 ({app.name}). "
                f"status_dir: {app.status_dir}\n"
            )
        else:
            sys.stderr.write(
                f"📎 --run '{run_tag}' 매칭 ({app.name}): {len(matched_files)} 파일\n"
            )
    return records


def filter_exclude_prefixes(records: list[Record], exclude_prefixes: list[str]) -> list[Record]:
    if not exclude_prefixes:
        return records
    out = []
    for r in records:
        prefix = r.id.split("-", 1)[0] if "-" in r.id else r.id
        if prefix in exclude_prefixes:
            continue
        out.append(r)
    return out


def canonical_records(records: list[Record]) -> dict[str, Record]:
    """ID 별 mtime 최신본을 canonical 로 결정."""
    latest: dict[str, Record] = {}
    for r in records:
        cur = latest.get(r.id)
        if cur is None or r.mtime > cur.mtime:
            latest[r.id] = r
    return latest


# ─────────────────────────────────────────────────────────────────────────────
# baseline markdown — --expected 전용
# ─────────────────────────────────────────────────────────────────────────────

def find_expected_row(baseline_path: Path, target_id: str) -> dict[str, Any] | None:
    """baseline markdown 에서 | <ID> | ... | 형태의 행을 찾아 컬럼 dict 로 반환.

    13 변형 헤더 공통: 첫 3 컬럼 (기준 ID | 소속 | 환경) 고정.
    나머지 컬럼은 이름 다양하므로 raw list + 가장 가까운 상위 ## / ### 섹션 제목 포함.
    """
    if not baseline_path.exists():
        sys.stderr.write(f"❌ baseline 파일 없음: {baseline_path}\n")
        return None

    id_pattern = re.compile(
        r'^\|\s*\*?\*?' + re.escape(target_id) + r'\*?\*?\s*\|'
    )
    section_pattern = re.compile(r'^#{2,4}\s+(.+?)\s*$')
    header_pattern = re.compile(r'^\|\s*기준\s*ID\s*\|')

    current_section: str | None = None
    current_header: list[str] | None = None
    lines = baseline_path.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines, start=1):
        m_section = section_pattern.match(line)
        if m_section:
            current_section = m_section.group(1)
            current_header = None
            continue
        if header_pattern.match(line):
            current_header = [c.strip() for c in line.strip().strip("|").split("|")]
            continue
        if id_pattern.match(line):
            cols = [c.strip() for c in line.strip().strip("|").split("|")]
            return {
                "id": target_id,
                "lineno": i,
                "section": current_section,
                "header": current_header,
                "columns": cols,
            }
    return None


# ─────────────────────────────────────────────────────────────────────────────
# 출력 포맷
# ─────────────────────────────────────────────────────────────────────────────

def fmt_summary(app_name: str, canon: dict[str, Record]) -> str:
    total = len(canon)
    counts = Counter(r.status for r in canon.values())
    lines = [f"=== {app_name} — baseline status summary ==="]
    lines.append(f"Total unique IDs tested: {total}")
    for key in ("PASS", "FAIL", "BLOCKED", "SKIP", "UNRECORDED", "OTHER"):
        n = counts.get(key, 0)
        if n == 0 and key in ("SKIP", "UNRECORDED", "OTHER"):
            continue
        pct = (n / total * 100) if total else 0
        note = ""
        if key == "UNRECORDED":
            note = "  (status 필드 null/empty — 테스터 기입 누락)"
        elif key == "OTHER":
            note = "  (예상 외 값 — stderr warning 참조)"
        lines.append(f"  {key:11s} {n:4d}  ({pct:5.1f}%){note}")
    latest_run = max((r.mtime for r in canon.values()), default=0)
    if latest_run:
        dt = datetime.fromtimestamp(latest_run).strftime("%Y-%m-%d %H:%M")
        lines.append(f"Latest run recorded: {dt}")
    return "\n".join(lines)


def fmt_by_prefix(app_name: str, canon: dict[str, Record]) -> str:
    by_prefix: dict[str, Counter[str]] = defaultdict(Counter)
    for r in canon.values():
        prefix = r.id.split("-", 1)[0] if "-" in r.id else r.id
        by_prefix[prefix][r.status] += 1

    lines = [f"=== {app_name} — by prefix ==="]
    lines.append(
        f"{'prefix':<10} {'total':>6} {'PASS':>6} {'FAIL':>6} {'BLOCKED':>8} {'UNREC':>6} {'OTHER':>6}"
    )
    for prefix in sorted(by_prefix.keys()):
        c = by_prefix[prefix]
        total = sum(c.values())
        lines.append(
            f"{prefix:<10} {total:>6} {c.get('PASS', 0):>6} {c.get('FAIL', 0):>6} "
            f"{c.get('BLOCKED', 0):>8} {c.get('UNRECORDED', 0):>6} {c.get('OTHER', 0):>6}"
        )
    return "\n".join(lines)


def fmt_id_detail(app_name: str, target_id: str, all_records: list[Record]) -> str:
    matched = [r for r in all_records if r.id == target_id]
    if not matched:
        return f"=== {app_name} — {target_id} ===\n(status.json 어디에도 기록 없음)"

    matched.sort(key=lambda r: r.mtime, reverse=True)
    latest = matched[0]
    lines = [f"=== {app_name} — {target_id} ==="]
    latest_dt = datetime.fromtimestamp(latest.mtime).strftime("%Y-%m-%d %H:%M")
    lines.append(f"latest: {latest.status} ({latest_dt}, {latest.source_file.name})")
    if latest.lane:
        lines.append(f"  lane:    {latest.lane}")
    if latest.runner_id:
        lines.append(f"  runner:  {latest.runner_id}")
    if latest.charter:
        lines.append(f"  charter: {latest.charter}")
    if latest.note:
        lines.append(f"  note:    {latest.note}")
    if latest.evidence:
        lines.append(f"  evidence:")
        for e in latest.evidence:
            lines.append(f"    - {e}")

    if len(matched) > 1:
        lines.append("")
        lines.append(f"history (older → newer, total {len(matched)}):")
        for r in reversed(matched[1:]):
            dt = datetime.fromtimestamp(r.mtime).strftime("%Y-%m-%d")
            lines.append(f"  {dt}  {r.status:8s}  {r.source_file.name}")
    return "\n".join(lines)


def fmt_filter(app_name: str, canon: dict[str, Record], status_filter: str) -> str:
    matched = sorted(
        (r for r in canon.values() if r.status == status_filter),
        key=lambda r: r.id,
    )
    lines = [f"=== {app_name} — status={status_filter} ({len(matched)}건) ==="]
    for r in matched:
        dt = datetime.fromtimestamp(r.mtime).strftime("%Y-%m-%d")
        note = r.note[:60] + ("…" if len(r.note) > 60 else "")
        lines.append(f"  {r.id:20s}  {dt}  {note}")
    return "\n".join(lines)


def fmt_expected(app_name: str, baseline_path: Path, target_id: str) -> str:
    row = find_expected_row(baseline_path, target_id)
    if row is None:
        return f"=== {app_name} — expected {target_id} ===\n(baseline 에서 찾을 수 없음: {baseline_path})"

    lines = [f"=== {app_name} — expected {target_id} ==="]
    lines.append(f"Location: {baseline_path}:{row['lineno']}")
    if row["section"]:
        lines.append(f"Section:  {row['section']}")
    header = row["header"] or []
    cols = row["columns"]
    if header and len(header) >= len(cols):
        # header 와 cols 정렬 (빈 trailing 컬럼 처리)
        for k, v in zip(header, cols):
            if not v:
                continue
            lines.append(f"  {k}: {v}")
    else:
        # header 없이 원시 컬럼만
        for i, v in enumerate(cols):
            if not v:
                continue
            lines.append(f"  col{i}: {v}")
    lines.append("")
    lines.append("→ 판정 이력은 `--id` 옵션으로 조회")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# 엔트리
# ─────────────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Multi-platform baseline status query tool. See TESTING_FRAMEWORK.md §20.8.",
    )
    p.add_argument("--app", help="앱 이름 (baseline.yml 의 apps 키). 미지정 시 default_app.")
    p.add_argument("--all-apps", action="store_true", help="모든 활성 앱 교차 집계.")
    p.add_argument("--config", default=str(DEFAULT_CONFIG), help=f"baseline.yml 경로 (기본: {DEFAULT_CONFIG})")

    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--summary", action="store_true", help="전체 요약 (기본)")
    mode.add_argument("--by-prefix", action="store_true", help="prefix 별 P/F/B")
    mode.add_argument("--id", dest="target_id", help="특정 ID 최신 판정 + 이력")
    mode.add_argument("--expected", dest="expected_id", help="baseline 에서 기준 항목 추출")
    mode.add_argument("--failed", action="store_true", help="현재 FAIL 상태 ID 목록")
    mode.add_argument("--blocked", action="store_true", help="현재 BLOCKED 상태 ID 목록")

    p.add_argument("--run", help="파일명 substring 매칭으로 범위 제한")
    return p


def select_apps(default_app: str, apps: dict[str, AppConfig], args: argparse.Namespace) -> list[AppConfig]:
    if args.all_apps:
        return list(apps.values())
    name = args.app or default_app
    if name not in apps:
        sys.stderr.write(
            f"❌ '{name}' 앱이 baseline.yml 에 없음 (활성 앱: {', '.join(apps) or '(none)'})\n"
        )
        sys.exit(2)
    return [apps[name]]


def run_for_app(app: AppConfig, args: argparse.Namespace) -> str:
    records = load_status_records(app, run_tag=args.run)
    records = filter_exclude_prefixes(records, app.exclude_prefixes)
    canon = canonical_records(records)

    if args.by_prefix:
        return fmt_by_prefix(app.name, canon)
    if args.target_id:
        return fmt_id_detail(app.name, args.target_id, records)
    if args.expected_id:
        return fmt_expected(app.name, app.baseline, args.expected_id)
    if args.failed:
        return fmt_filter(app.name, canon, "FAIL")
    if args.blocked:
        return fmt_filter(app.name, canon, "BLOCKED")
    return fmt_summary(app.name, canon)


def main() -> int:
    args = build_parser().parse_args()
    default_app, apps = load_config(Path(args.config))
    if not apps:
        sys.stderr.write("⚠️  활성 앱 없음 — baseline.yml 의 apps.<name> entry 를 하나 이상 활성화하세요.\n")
        return 1

    selected = select_apps(default_app, apps, args)
    outputs = [run_for_app(app, args) for app in selected]
    print("\n\n".join(outputs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
