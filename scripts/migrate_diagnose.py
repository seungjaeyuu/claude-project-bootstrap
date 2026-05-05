#!/usr/bin/env python3
"""
CLAUDE.md 분리 후보 진단 도구.

claude-project-bootstrap 의 slim-claude-md 커맨드가 호출. 사용자에게
현재 본체에서 어떤 섹션이 분리 후보인지 리포트 제공 — 자동 분리하지 않음.

사용:
    python3 scripts/migrate_diagnose.py [path/to/CLAUDE.md]

기본값: ./CLAUDE.md

리포트 형식:
    📊 분리 후보 진단

    CLAUDE.md 현재 라인 수: 287줄 (임계치 120줄 초과)

    분리 후보 (큰 섹션 순):
      [1] §8 E2E 테스트 (현재 80줄)        → RULES_E2E.md 로 분리 권장
      [2] §6 데이터 정합성 (현재 22줄)      → RULES_DATA_INTEGRITY.md 로 분리 권장
      ...

리포트는 stdout. 사용자가 후보별 yes/no 결정은 slim-claude-md 커맨드의
대화형 흐름이 책임.

작성: claude-project-bootstrap v0.2.0
참조 spec: docs/specs/2026-05-05-v0.2.0-permissions-and-doc-slimming-design.md §9.3
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# 키워드 → (분리 대상 RULES 파일, 영역 설명)
SECTION_PATTERNS: list[tuple[re.Pattern[str], str, str]] = [
    (re.compile(r"E2E|시뮬레이터|Codex|orchestrator|Cross-Lane|UDID", re.I),
     "RULES_E2E.md",
     "E2E 테스트 / Codex orchestrator"),
    (re.compile(r"Firestore|catch.*silent|composite index|offline queue|시드 무결성", re.I),
     "RULES_DATA_INTEGRITY.md",
     "백엔드 데이터 정합성"),
    (re.compile(r"accessibilityIdentifier|testTag|data-testid|ValueKey|NavigationLink", re.I),
     "RULES_ACCESSIBILITY.md",
     "Accessibility identifier"),
    (re.compile(r"보호자|배송 건|도메인 용어|스키마명 병기", re.I),
     "RULES_TERMINOLOGY.md",
     "도메인 용어 / 스키마명 병기"),
    (re.compile(r"Dictionary literal|중복 키|duplicate keys|check_dict_duplicates", re.I),
     "RULES_DICT_DUPLICATES.md",
     "Dictionary 중복 키"),
    (re.compile(r"리팩토링|grep -c|필드 누락|기능 누락", re.I),
     "RULES_REFACTORING.md",
     "대규모 변경 / 리팩토링"),
]

THRESHOLD = 120  # CLAUDE.md 본체 임계치


def parse_sections(content: str) -> list[tuple[str, int, list[str]]]:
    """
    `## ` 시작 헤딩 기준으로 섹션 분리.
    반환: [(헤딩 텍스트, 시작 라인, 섹션 내용 줄 리스트), ...]
    """
    lines = content.splitlines()
    sections: list[tuple[str, int, list[str]]] = []
    current_title = "(머리말)"
    current_start = 0
    current_body: list[str] = []
    for idx, line in enumerate(lines):
        if line.startswith("## "):
            if current_body:
                sections.append((current_title, current_start, current_body))
            current_title = line.lstrip("# ").strip()
            current_start = idx
            current_body = []
        else:
            current_body.append(line)
    if current_body:
        sections.append((current_title, current_start, current_body))
    return sections


MIN_CONFIDENCE = 2  # 매치 횟수 임계치 — 1회만 등장은 우연 일치 가능성


def classify_section(title: str, body: list[str]) -> tuple[str | None, str | None]:
    """
    섹션 내용 기반으로 RULES 파일 분류 추론.

    가중치 방식 — 패턴별 매치 횟수를 세고 가장 점수 높은 카테고리 선택.
    제목의 매치는 본문 1매치보다 가중 (× 3) — 제목이 영역을 강하게 시사.
    최고 점수가 MIN_CONFIDENCE 미만이면 분류 안 함 (None) — 머리말 / 사용 방법
    같은 일반 섹션이 우연히 1회 매치된 키워드로 잘못 분류되는 것을 차단.

    반환: (RULES 파일명, 영역 설명) 또는 (None, None) — 분리 불요.
    """
    body_text = "\n".join(body)
    scores: list[tuple[int, str, str]] = []
    for pattern, rules_file, label in SECTION_PATTERNS:
        title_matches = len(pattern.findall(title))
        body_matches = len(pattern.findall(body_text))
        score = title_matches * 3 + body_matches
        if score > 0:
            scores.append((score, rules_file, label))
    if not scores:
        return None, None
    scores.sort(key=lambda s: -s[0])
    best_score, rules_file, label = scores[0]
    if best_score < MIN_CONFIDENCE:
        return None, None
    return rules_file, label


def diagnose(path: Path) -> int:
    if not path.is_file():
        print(f"❌ 파일 없음: {path}", file=sys.stderr)
        return 1

    content = path.read_text(encoding="utf-8")
    total_lines = len(content.splitlines())

    print("📊 분리 후보 진단")
    print()
    if total_lines <= THRESHOLD:
        print(f"CLAUDE.md 현재 라인 수: {total_lines}줄 (임계치 {THRESHOLD}줄 이내 — 분리 불요)")
        return 0

    print(
        f"CLAUDE.md 현재 라인 수: {total_lines}줄 "
        f"(임계치 {THRESHOLD}줄 초과 +{total_lines - THRESHOLD})"
    )
    print()

    sections = parse_sections(content)
    candidates: list[tuple[int, str, str, str]] = []  # (line_count, title, rules, label)
    for title, _start, body in sections:
        if len(body) < 5:
            continue  # 너무 작은 섹션은 분리 후보 아님
        rules, label = classify_section(title, body)
        if rules and label:
            candidates.append((len(body), title, rules, label))

    if not candidates:
        print("분리 후보 자동 추론 실패 — 본체를 직접 검토해 영역별로 수동 분리 필요.")
        print(
            "추천 절차: 본체에서 가장 큰 섹션을 영역명에 맞춰 docs/rules/RULES_*.md 로 이동."
        )
        return 0

    # 큰 섹션 순 정렬
    candidates.sort(key=lambda c: -c[0])

    print("분리 후보 (큰 섹션 순):")
    for idx, (line_count, title, rules, label) in enumerate(candidates, start=1):
        print(f"  [{idx}] {title} (현재 {line_count}줄)")
        print(f"      → docs/rules/{rules} 로 분리 권장 ({label})")
    print()
    print("각 후보를 분리할지 여부는 slim-claude-md 커맨드의 대화형 흐름에서 결정.")
    print("(이 스크립트는 진단만 — 자동 분리하지 않음)")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) >= 2 and argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0
    target = Path(argv[1]) if len(argv) >= 2 else Path("CLAUDE.md")
    return diagnose(target)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
