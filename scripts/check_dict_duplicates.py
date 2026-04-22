#!/usr/bin/env python3
"""
check_dict_duplicates.py — Swift/Kotlin/TS dictionary literal 중복 키 검출

Swift `Dictionary literal`에 중복 키가 있으면 **런타임에 fatal error**를 발생시킨다.
(컴파일 타임에는 경고도 에러도 발생하지 않음)

이 스크립트는 지정된 파일에서 dictionary literal을 찾고 중복 키를 검출한다.

Usage:
    # 단일 파일 검사
    python3 scripts/check_dict_duplicates.py <file>

    # 여러 파일 검사
    python3 scripts/check_dict_duplicates.py <file1> <file2> ...

    # 디렉터리 전체 검사 (Swift/Kotlin/TS)
    python3 scripts/check_dict_duplicates.py --recursive <dir>

    # Git pre-commit hook
    git diff --cached --name-only --diff-filter=AM | \\
        grep -E '\\.(swift|kt|ts|tsx)$' | \\
        xargs python3 scripts/check_dict_duplicates.py

Exit code:
    0 — 중복 없음
    1 — 중복 발견 (commit 차단)
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path


def check_file(filepath: Path) -> list[tuple[str, int, str, int]]:
    """파일에서 dictionary literal 중복 키 검출.

    Returns:
        [(variable_name, line_number, duplicate_key, count), ...]
    """
    if not filepath.exists():
        return []

    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return []

    findings = []

    # Swift: let name: [String: String] = [ "key": "value", ... ]
    # Swift: private let _name: [String: String] = [ ... ]
    # Swift: static let name = [ "key": "value" ]
    swift_pattern = re.compile(
        r"(?:let|var)\s+(\w+)\s*(?::\s*\[[^\]]+\])?\s*=\s*\[(.+?)\]",
        re.DOTALL,
    )

    for match in swift_pattern.finditer(content):
        var_name = match.group(1)
        body = match.group(2)

        # Skip if body doesn't look like a dictionary (no ":")
        if ":" not in body:
            continue

        # Extract string keys (Swift/Kotlin/TS style)
        keys = re.findall(r'"([^"]+)"\s*:', body)
        if not keys:
            continue

        counts = Counter(keys)
        dups = {k: v for k, v in counts.items() if v > 1}

        if dups:
            # Find line number of the variable declaration
            line_num = content[: match.start()].count("\n") + 1
            for key, count in dups.items():
                findings.append((var_name, line_num, key, count))

    return findings


def find_source_files(directory: Path) -> list[Path]:
    """디렉터리에서 Swift/Kotlin/TypeScript 파일 재귀 검색."""
    extensions = {".swift", ".kt", ".ts", ".tsx"}
    files = []
    for ext in extensions:
        files.extend(directory.rglob(f"*{ext}"))

    # Skip common build/dependency directories
    exclude_dirs = {"node_modules", "DerivedData", ".build", "Pods", "build", ".git"}
    return [f for f in files if not any(part in exclude_dirs for part in f.parts)]


def main():
    parser = argparse.ArgumentParser(
        description="Swift/Kotlin/TS dictionary literal 중복 키 검출"
    )
    parser.add_argument("paths", nargs="*", help="검사할 파일 또는 디렉터리")
    parser.add_argument(
        "--recursive", "-r", action="store_true",
        help="디렉터리를 재귀적으로 검사"
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true",
        help="중복이 없는 파일은 출력하지 않음"
    )

    args = parser.parse_args()

    if not args.paths:
        # stdin에서 파일 목록 읽기 (git hook 용)
        files = [Path(line.strip()) for line in sys.stdin if line.strip()]
    else:
        files = []
        for p in args.paths:
            path = Path(p)
            if path.is_dir() or args.recursive:
                files.extend(find_source_files(path))
            else:
                files.append(path)

    # 지원 확장자만 필터
    supported = {".swift", ".kt", ".ts", ".tsx"}
    files = [f for f in files if f.suffix in supported]

    if not files:
        print("검사할 파일이 없습니다.", file=sys.stderr)
        sys.exit(0)

    total_files = 0
    files_with_dups = 0
    total_dups = 0

    for filepath in files:
        findings = check_file(filepath)
        total_files += 1

        if findings:
            files_with_dups += 1
            total_dups += len(findings)
            print(f"\n❌ {filepath}")
            for var_name, line_num, key, count in findings:
                print(f"   Line {line_num}: {var_name} — '{key}' {count}회 중복")
        elif not args.quiet:
            print(f"✓ {filepath}")

    print()
    print("=" * 60)
    print(f"검사 파일: {total_files}")
    print(f"중복 발견: {files_with_dups} 파일, {total_dups} 건")
    print("=" * 60)

    if files_with_dups > 0:
        print()
        print("⚠️  Swift Dictionary literal 중복 키는 런타임에 fatal error를 발생시킵니다.")
        print("   (컴파일 타임에 경고도 에러도 발생하지 않음)")
        print("   중복 키를 반드시 제거하세요.")
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
