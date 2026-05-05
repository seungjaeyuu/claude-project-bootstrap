#!/usr/bin/env python3
"""
Firebase 프로젝트 격리 검증 스크립트.

사용 1 — predeploy hook (firebase.json 의 predeploy 에서 호출):
    python3 scripts/check_firebase_project.py

사용 2 — init-project 의 글로벌 캐시 검증 (init 시 1회):
    python3 scripts/check_firebase_project.py --init-check <expected-project-id>

검증 우선순위 (Firebase CLI 동작 일치):
    1. CLI flag --project <ID>  (predeploy 시점에는 이미 적용된 상태)
    2. 환경변수 GCLOUD_PROJECT / GOOGLE_CLOUD_PROJECT
    3. 현재 디렉토리의 .firebaserc 의 projects.default
    4. firebase use 활성 프로젝트 (~/.config/configstore/firebase-tools.json activeProjects)

기대 ID 와 활성 ID 가 일치하지 않으면 비-0 종료 + stderr 에러 메시지.
일치하면 stdout 한 줄 + 종료 코드 0.

작성: claude-project-bootstrap v0.2.0
참조 spec: docs/specs/2026-05-05-v0.2.0-permissions-and-doc-slimming-design.md §4
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def read_firebaserc(cwd: Path) -> str | None:
    """현재 디렉토리의 .firebaserc 의 projects.default 를 반환. 없으면 None."""
    rc = cwd / ".firebaserc"
    if not rc.is_file():
        return None
    try:
        data = json.loads(rc.read_text())
    except json.JSONDecodeError as e:
        print(f"⚠️  .firebaserc JSON 파싱 실패: {e}", file=sys.stderr)
        return None
    return data.get("projects", {}).get("default")


def get_env_project() -> str | None:
    """환경변수 GCLOUD_PROJECT / GOOGLE_CLOUD_PROJECT 를 반환. 없으면 None."""
    return os.environ.get("GCLOUD_PROJECT") or os.environ.get("GOOGLE_CLOUD_PROJECT")


def get_active_from_configstore(cwd: Path) -> str | None:
    """
    ~/.config/configstore/firebase-tools.json 의 activeProjects 에서
    현재 디렉토리(절대경로) 매핑된 프로젝트 ID 를 반환. 매핑 없으면 None.
    """
    configstore = Path.home() / ".config" / "configstore" / "firebase-tools.json"
    if not configstore.is_file():
        return None
    try:
        data = json.loads(configstore.read_text())
    except json.JSONDecodeError:
        return None
    active = data.get("activeProjects", {})
    # firebase-tools 는 절대경로 키 기준
    return active.get(str(cwd.resolve()))


def get_firebase_use_output() -> str | None:
    """
    `firebase use` 명령 출력에서 active 프로젝트 추출.
    명령 미설치 또는 실패 시 None. (configstore 가 fallback)
    """
    try:
        result = subprocess.run(
            ["firebase", "use"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    # 출력 형태: "Active Project: <alias> (<project-id>)" 또는 "(<id>)"
    for line in result.stdout.splitlines():
        line = line.strip()
        if "Active Project" in line or "Now using project" in line:
            # 괄호 안의 id 우선
            if "(" in line and ")" in line:
                start = line.rindex("(") + 1
                end = line.rindex(")")
                return line[start:end].strip()
            # alias 만 있는 경우 마지막 토큰
            tokens = line.split()
            return tokens[-1].strip()
    return None


def resolve_active_project(cwd: Path) -> tuple[str | None, str]:
    """
    활성 프로젝트 ID 와 결정 경로(우선순위)를 반환.
    """
    env = get_env_project()
    if env:
        return env, "environment variable"

    rc = read_firebaserc(cwd)
    if rc:
        return rc, ".firebaserc"

    fb = get_firebase_use_output()
    if fb:
        return fb, "firebase use"

    cs = get_active_from_configstore(cwd)
    if cs:
        return cs, "configstore (글로벌 캐시)"

    return None, "결정 실패"


def predeploy_check(cwd: Path) -> int:
    """firebase.json predeploy 호출 시 검증 — 기대 ID = .firebaserc default."""
    expected = read_firebaserc(cwd)
    if not expected:
        print(
            "🚫 .firebaserc 가 없거나 projects.default 미정의 — predeploy 차단",
            file=sys.stderr,
        )
        print(
            "   해결: claude-project-bootstrap 의 firebase-isolation 커맨드 실행"
            " 또는 수동으로 .firebaserc 작성",
            file=sys.stderr,
        )
        return 1

    active, source = resolve_active_project(cwd)
    if active is None:
        print(
            f"⚠️  활성 프로젝트 결정 실패 — predeploy 보수적 차단 (기대: {expected})",
            file=sys.stderr,
        )
        return 1

    if active != expected:
        print(
            "🚫 Firebase 프로젝트 mismatch",
            file=sys.stderr,
        )
        print(f"   .firebaserc default: {expected}", file=sys.stderr)
        print(f"   현재 활성: {active}  (출처: {source})", file=sys.stderr)
        print("   해결:", file=sys.stderr)
        print(f"     firebase use {expected}", file=sys.stderr)
        print(f"   또는 deploy 명령에 --project {expected} 명시", file=sys.stderr)
        return 1

    print(f"✅ Firebase project = {expected}  (출처: {source})")
    return 0


def init_check(cwd: Path, expected: str) -> int:
    """
    init-project 시 1회 호출 — 글로벌 캐시 의심 여부 검증.
    .firebaserc 가 방금 생성되었으므로 configstore 의 다른 매핑이 의심 신호.
    """
    cs = get_active_from_configstore(cwd)
    if cs is None:
        print(f"✅ 글로벌 캐시 매핑 없음 — Firebase 격리 OK (project: {expected})")
        return 0
    if cs == expected:
        print(f"✅ 글로벌 캐시 매핑 일치 — {cs}")
        return 0
    print(
        "⚠️  글로벌 캐시에 다른 프로젝트 매핑 발견",
        file=sys.stderr,
    )
    print(f"   현재 디렉토리: {cwd.resolve()}", file=sys.stderr)
    print(f"   캐시 매핑: {cs}", file=sys.stderr)
    print(f"   기대값 (.firebaserc): {expected}", file=sys.stderr)
    print(
        f"   해결: firebase use {expected}  (캐시를 .firebaserc 와 동기화)",
        file=sys.stderr,
    )
    # init 단계는 차단 안 함 — 경고만
    return 0


def main(argv: list[str]) -> int:
    cwd = Path.cwd()
    if len(argv) >= 3 and argv[1] == "--init-check":
        return init_check(cwd, argv[2])
    return predeploy_check(cwd)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
