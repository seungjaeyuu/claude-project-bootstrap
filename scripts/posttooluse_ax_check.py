#!/usr/bin/env python3
"""PostToolUse hook wrapper — Claude Code stdin JSON 파싱 + accessibility identifier 검증.

Claude Code PostToolUse hook 스펙:
- stdin 으로 JSON 수신 (tool_input.file_path 등)
- stdout 으로 JSON 응답 (systemMessage 필드 사용 시 Claude context 전달)
- exit 0 = 성공, exit 2 = 차단 경고

본 스크립트 동작:
1. stdin JSON 파싱 → file_path 추출
2. matcher regex (apps/.*\\.(swift|kt|tsx)$) 체크
3. check_accessibility_identifiers.py 호출 (target 프로젝트 로컬)
4. 위반·경고에 따라 systemMessage 구성 후 JSON 출력

절대 차단하지 않음 — 경고만 Claude 와 사용자에게 전달.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys


MATCHER_PATTERN = re.compile(r'apps/.*\.(swift|kt|tsx)$')
WARNING_LINE_PATTERN = re.compile(r'경고 \([^)]+\): [1-9]\d*')


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return

    tool_input = payload.get('tool_input', {}) or {}
    file_path = tool_input.get('file_path', '')

    if not isinstance(file_path, str) or not file_path:
        return

    if not MATCHER_PATTERN.search(file_path):
        return

    project_dir = os.environ.get('CLAUDE_PROJECT_DIR', '').strip()
    if not project_dir:
        return

    check_script = os.path.join(project_dir, 'scripts', 'check_accessibility_identifiers.py')
    if not os.path.isfile(check_script):
        return

    # 상대경로면 프로젝트 루트 기준으로 변환
    target_file = file_path if os.path.isabs(file_path) else os.path.join(project_dir, file_path)
    if not os.path.isfile(target_file):
        return

    try:
        result = subprocess.run(
            ['python3', check_script, target_file],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=project_dir,
        )
    except (OSError, subprocess.TimeoutExpired):
        return

    output = (result.stdout or '') + (result.stderr or '')

    if result.returncode != 0:
        # 위반 — 상세 포함 경고
        message = (
            f"⚠️ accessibility identifier 위반 감지\n"
            f"파일: {file_path}\n"
            f"---\n"
            f"{output.strip()}\n"
            f"---\n"
            f"→ 가이드: /ACCESSIBILITY_IDENTIFIERS.md\n"
            f"→ 수동 확인: python3 scripts/check_accessibility_identifiers.py {file_path}"
        )
        print(json.dumps({
            'systemMessage': message,
            'suppressOutput': False,
        }))
        return

    warning_match = WARNING_LINE_PATTERN.search(output)
    if warning_match:
        message = (
            f"💡 {file_path} — {warning_match.group(0)}\n"
            f"→ 상세: python3 scripts/check_accessibility_identifiers.py {file_path}"
        )
        print(json.dumps({
            'systemMessage': message,
            'suppressOutput': False,
        }))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        # hook 이 스스로 에러로 작업을 차단해선 안 됨
        pass
