#!/usr/bin/env python3
"""
CLAUDE.md / RULES 문서 크기 검증.

claude-project-bootstrap v0.2.0 임계치:
- CLAUDE.md (본체)         : 120줄
- apps/*/CLAUDE.md         : 250줄
- docs/rules/RULES_*.md    : 250줄

초과 시 stderr 에 경고 (exit 0 — 차단 안 함, 인지 목적).
pre-commit 에서 호출 권장.

임계치는 아래 THRESHOLDS 상수에서 수정. 사용자 프로젝트 특성에 따라 조정 가능.

작성: claude-project-bootstrap v0.2.0
참조 spec: docs/specs/2026-05-05-v0.2.0-permissions-and-doc-slimming-design.md §5.6
"""

from __future__ import annotations

import sys
from pathlib import Path

# (glob 패턴, 임계치 줄 수)
THRESHOLDS: list[tuple[str, int]] = [
    ("CLAUDE.md", 120),
    ("apps/*/CLAUDE.md", 250),
    ("apps/*/*/CLAUDE.md", 250),  # 모노레포 다층 (apps/web/admin 같은)
    ("docs/rules/RULES_*.md", 250),
]


def count_lines(path: Path) -> int:
    """파일의 라인 수. 마지막 빈 줄 보정 없음 (wc -l 과 동일)."""
    try:
        with path.open(encoding="utf-8") as f:
            return sum(1 for _ in f)
    except (OSError, UnicodeDecodeError):
        return -1


def check_repo(root: Path) -> int:
    """저장소 root 에서 모든 임계치 패턴 검사. 경고 건수 반환."""
    warnings = 0
    for pattern, threshold in THRESHOLDS:
        for path in root.glob(pattern):
            if not path.is_file():
                continue
            lines = count_lines(path)
            if lines < 0:
                continue
            if lines > threshold:
                rel = path.relative_to(root) if path.is_relative_to(root) else path
                print(
                    f"⚠️  {rel}: {lines}줄 (임계치 {threshold}줄 초과 +{lines - threshold})",
                    file=sys.stderr,
                )
                warnings += 1
    return warnings


def main(argv: list[str]) -> int:
    root = Path.cwd()
    if len(argv) >= 2 and argv[1] not in ("-h", "--help"):
        root = Path(argv[1]).resolve()
    if argv[1:2] in (["-h"], ["--help"]):
        print(__doc__)
        return 0

    warnings = check_repo(root)
    if warnings:
        print(
            f"\n총 {warnings}개 파일이 임계치 초과 — 분리 검토 권장.",
            file=sys.stderr,
        )
        print(
            "분리 도구: claude-project-bootstrap 의 slim-claude-md 커맨드"
            " (또는 docs/rules/ 로 영역별 수동 분리)",
            file=sys.stderr,
        )
    # 차단 안 함 — 경고만
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
