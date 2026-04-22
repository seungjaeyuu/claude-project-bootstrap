#!/usr/bin/env python3
"""
check_accessibility_identifiers.py — iOS SwiftUI `.accessibilityIdentifier()` 스키마 검증

E2E 테스트 하네스(AX 탐색)는 `.accessibilityIdentifier()` 문자열로 UI 요소를 식별한다.
`/ACCESSIBILITY_IDENTIFIERS.md` 에서 정의한 엄격 스키마를 준수하지 않으면 테스트 실패·BLOCKED 로 이어진다.

검사 항목:
1. 인터랙티브 요소 (Button / TextField / SecureField / TextEditor / Toggle / Picker /
   DatePicker / Slider / Stepper / Menu / NavigationLink / Link / DisclosureGroup) 에
   `.accessibilityIdentifier()` 미부여 검출
2. identifier 문자열이 스키마 `{feature}_{screen}_{element}_{type}` 형식 이탈
3. 전역 중복 identifier (dynamic `\\(id)` suffix 포함 identifier 는 제외)

사용법:
    # 특정 파일 검사
    python3 scripts/check_accessibility_identifiers.py <file1> [file2] ...

    # 전체 iOS View 계층 검사
    python3 scripts/check_accessibility_identifiers.py --recursive \
        sunnyway/apps/student_app_ios/SunnyWay

    # 조용히 (CI/hook 용)
    python3 scripts/check_accessibility_identifiers.py --quiet <files>

Exit code:
    0 — 위반 없음
    1 — 위반 발견 (세부 내역 stderr)
    2 — 스크립트 사용 오류

규칙 원본: /ACCESSIBILITY_IDENTIFIERS.md
사고 이력: /TESTING_FRAMEWORK.md §13.5 (AX 병합·stale identifier)
"""

import argparse
import pathlib
import re
import sys
from collections import defaultdict
from typing import Iterable

# 엄격 스키마: {feature}_{screen_context}_{element_role}_{type}
# - snake_case + ASCII 만 허용
# - 끝부분은 type 접미사 또는 dynamic suffix
# - dynamic suffix 는 `_\\(...)` 또는 identifier 안에 나타날 수 있음
VALID_TYPES = (
    "button field editor toggle picker slider stepper menu row tab link group "
    "label title badge status count message error icon"
).split()

# {feature} 시작부 검증 (확장 가능)
VALID_FEATURES = {
    "auth", "dashboard", "notice", "academy_notice", "settings", "guardian",
    "location", "attendance", "academy", "course", "common", "schedule",
    "notification",
}

# 문자열 literal 기반 정적 identifier 의 엄격 규칙
# 예: "auth_login_submit_button"  /  "notice_list_row_\(notice.id)"
#     feature_____screen__________elem__type
IDENTIFIER_PATTERN = re.compile(
    r'^[a-z][a-z0-9]*(?:_[a-z0-9]+)*_(?:'
    + "|".join(VALID_TYPES)
    + r')(?:_.*)?$'
)

# .accessibilityIdentifier("...") 또는 .accessibilityIdentifier("...\(x)...") 추출
# Swift 문자열 보간은 `\(...)` 형태로, 여는 괄호까지만 찾으면 중괄호 중첩을 피할 수 있음.
# 여기서는 간단히 가장 바깥 "..." 안의 전체 문자열을 뽑는다.
ACCESSIBILITY_CALL = re.compile(
    r'\.accessibilityIdentifier\(\s*"((?:[^"\\]|\\.)*)"\s*\)'
)

# 인터랙티브 요소 시작 토큰
# Swift DSL 문법 기반 — 정확한 AST 파싱이 아니라 소스 라인 매칭이므로 false positive 가능.
# 여기서는 ".accessibilityIdentifier" 가 modifier chain 의 뒤쪽에 오는 경우를 고려하여
# 전방 10줄 범위 내 동일 요소에 부여된 것으로 간주한다.
INTERACTIVE_ELEMENTS = [
    "Button",
    "TextField",
    "SecureField",
    "TextEditor",
    "Toggle",
    "Picker",
    "DatePicker",
    "Slider",
    "Stepper",
    "Menu",
    "NavigationLink",
    "Link",
    "DisclosureGroup",
]

# 요소 선언 라인 매칭 (선행 공백 허용)
ELEMENT_DECL = re.compile(
    r'^\s*(?:\w+\s+)*(' + "|".join(INTERACTIVE_ELEMENTS) + r')\b'
)

# identifier 에 dynamic suffix 가 포함된 경우 전역 중복 판정에서 제외
DYNAMIC_SUFFIX = re.compile(r'\\\(')


def strip_dynamic_interpolations(identifier: str) -> str:
    """
    Swift 문자열 보간 `\\(...)` 를 중첩 괄호까지 고려하여 제거한다.
    단순 regex 로는 `\\(foo.bar())` 처럼 내부에 `)` 가 있는 경우 처리 못함.
    """
    result: list[str] = []
    i = 0
    n = len(identifier)
    while i < n:
        if identifier[i] == '\\' and i + 1 < n and identifier[i + 1] == '(':
            depth = 1
            i += 2
            while i < n and depth > 0:
                if identifier[i] == '(':
                    depth += 1
                elif identifier[i] == ')':
                    depth -= 1
                i += 1
        else:
            result.append(identifier[i])
            i += 1
    return "".join(result)


def extract_identifiers(lines: list[str]) -> list[tuple[int, str]]:
    """파일에서 (라인번호, identifier) 목록 추출."""
    out: list[tuple[int, str]] = []
    for idx, line in enumerate(lines, start=1):
        m = ACCESSIBILITY_CALL.search(line)
        if m:
            out.append((idx, m.group(1)))
    return out


def find_missing_interactives(lines: list[str]) -> list[tuple[int, str]]:
    """
    인터랙티브 요소 선언 후 10줄 내에 `.accessibilityIdentifier` 가 없으면 누락으로 집계.
    전방 10줄 윈도우는 modifier chain 이 길어지는 SwiftUI 관습을 수용.
    False positive 가 있을 수 있으므로 warning 으로만 취급 (exit code 에는 영향 X).
    """
    missing: list[tuple[int, str]] = []
    n = len(lines)
    for i in range(n):
        m = ELEMENT_DECL.match(lines[i])
        if not m:
            continue
        window = lines[i : min(n, i + 10)]
        if not any(".accessibilityIdentifier(" in line for line in window):
            missing.append((i + 1, m.group(1)))
    return missing


def validate_schema(identifier: str) -> str | None:
    """
    스키마 위반 시 사유 문자열 반환 (None 이면 pass).
    - snake_case + ASCII
    - type 접미사 포함
    - feature prefix 카탈로그 매칭
    """
    # dynamic suffix 제거 후 정적 prefix 만 검증 (중첩 괄호 지원)
    static_part = strip_dynamic_interpolations(identifier)
    # 연속된 `_` 를 단일 `_` 로 병합 (dynamic 이 중간에 있으면 __ 가 생김)
    static_part = re.sub(r'_+', '_', static_part)
    # 양 끝 `_` 정리
    static_part = static_part.strip("_")

    if not re.match(r'^[a-z][a-z0-9_]*$', static_part):
        return "snake_case/ASCII 위반"

    parts = static_part.split("_")
    if len(parts) < 3:
        return f"형식 부족 ({len(parts)} 토큰, 최소 3: feature/screen/element + type)"

    # feature prefix 검증 (복합 feature 인 academy_notice 도 지원)
    feature_candidates = [parts[0], f"{parts[0]}_{parts[1]}" if len(parts) > 1 else None]
    if not any(c in VALID_FEATURES for c in feature_candidates if c):
        return f"미등록 feature prefix: '{parts[0]}' (허용: {', '.join(sorted(VALID_FEATURES))})"

    # type 접미사 검증 (마지막 토큰 또는 dynamic 직전 토큰)
    if parts[-1] not in VALID_TYPES:
        return f"type 접미사 누락/오류 (마지막 토큰: '{parts[-1]}', 허용: {', '.join(VALID_TYPES)})"

    return None


def check_file(
    path: pathlib.Path, all_identifiers: dict[str, list[str]], quiet: bool
) -> tuple[int, int]:
    """
    단일 파일 검사.
    Returns: (위반 수, 경고 수)
    """
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return 0, 0

    lines = content.splitlines()
    violations = 0
    warnings = 0

    # identifier 추출 + 스키마 검증
    for line_no, identifier in extract_identifiers(lines):
        reason = validate_schema(identifier)
        if reason:
            violations += 1
            if not quiet:
                print(
                    f"[VIOLATION] {path}:{line_no} — \"{identifier}\" — {reason}",
                    file=sys.stderr,
                )
        # 전역 중복 검사용 인덱스 축적 (dynamic suffix 포함 identifier 는 제외)
        if not DYNAMIC_SUFFIX.search(identifier):
            all_identifiers[identifier].append(f"{path}:{line_no}")

    # 인터랙티브 요소 누락 (warning — exit code 영향 없음)
    for line_no, element in find_missing_interactives(lines):
        warnings += 1
        if not quiet:
            print(
                f"[WARNING] {path}:{line_no} — {element} 에 .accessibilityIdentifier() 누락 가능",
                file=sys.stderr,
            )

    return violations, warnings


def gather_files(targets: list[str], recursive: bool) -> Iterable[pathlib.Path]:
    for t in targets:
        p = pathlib.Path(t)
        if p.is_file() and p.suffix == ".swift":
            yield p
        elif p.is_dir() and recursive:
            yield from p.rglob("*.swift")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("targets", nargs="+", help="파일 또는 디렉토리")
    parser.add_argument("--recursive", action="store_true", help="디렉토리 재귀 탐색")
    parser.add_argument("--quiet", action="store_true", help="위반 내역 stdout 출력 억제 (요약만)")
    parser.add_argument(
        "--strict-missing",
        action="store_true",
        help="인터랙티브 요소 누락도 exit code 에 반영 (기본은 warning)",
    )
    args = parser.parse_args()

    files = list(gather_files(args.targets, args.recursive))
    if not files:
        print("검사 대상 .swift 파일 없음", file=sys.stderr)
        return 2

    all_identifiers: dict[str, list[str]] = defaultdict(list)
    total_violations = 0
    total_warnings = 0
    for path in files:
        v, w = check_file(path, all_identifiers, args.quiet)
        total_violations += v
        total_warnings += w

    # 전역 중복 검사
    duplicates = {k: v for k, v in all_identifiers.items() if len(v) > 1}
    # 동일 파일 내 중복은 SwiftUI visibility toggle 같은 의도적 케이스가 있을 수 있으므로
    # **서로 다른 파일에 동일 identifier 가 등장할 때만** 전역 중복 위반으로 집계.
    cross_file_duplicates = {
        ident: locs for ident, locs in duplicates.items()
        if len({loc.rsplit(":", 1)[0] for loc in locs}) > 1
    }
    if cross_file_duplicates:
        for ident, locs in cross_file_duplicates.items():
            total_violations += 1
            if not args.quiet:
                print(
                    f"[DUPLICATE] \"{ident}\" — {len(locs)}개 위치: {', '.join(locs)}",
                    file=sys.stderr,
                )

    # 요약
    print("=" * 60)
    print(f"검사 파일: {len(files)}")
    print(f"위반 (스키마/중복): {total_violations}")
    print(f"경고 (인터랙티브 미부여 가능성): {total_warnings}")
    print("=" * 60)

    exit_code = 0
    if total_violations > 0:
        exit_code = 1
    if args.strict_missing and total_warnings > 0:
        exit_code = 1

    if exit_code == 0:
        print("✓ accessibility identifier 검증 통과")
    else:
        print("✗ 위반 사항이 있습니다. 자세한 내역은 stderr 참조. 가이드: /ACCESSIBILITY_IDENTIFIERS.md")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
