---
description: Set/change Bash permission tier (YOLO/Standard/Strict/None), merging existing .claude/settings.json permissions — Bash 권한 단계 도입·변경
argument-hint: (선택 없음 — 대화형)
allowed-tools: Read, Write, Edit, Bash(cp:*), Bash(mkdir:*), Bash(cat:*), Bash(diff:*), Bash(ls:*), Bash(rm:*), Bash(grep:*)
---

> **v0.3.0**: 이 커맨드는 `/init --bash` 에 통합되었습니다. 동일 기능을 실행합니다.

# /bash-permission — Bash 권한 단계 도입·변경

`.claude/settings.json` 의 `permissions` 키를 4단계 중 하나로 설정한다. 기존 `hooks` 키는 보존. 마이그레이션·재설정 양쪽 용도.

## 4중 안전장치

1. **자동 백업**: 변경 전 `.claude/settings.json` 을 `_backup_v0.1/.claude/settings.json` 으로 복사 (이미 있으면 timestamp suffix). `.gitignore` 에 `_backup_v0.1/` 등록.
2. **Diff preview**: 변경 적용 전 사용자에게 변경 내역 출력 → yes/no 확인.
3. **영역 독립**: 본 커맨드는 `permissions` 키만 변경. `hooks` 등 다른 키 보존.
4. **idempotent**: 재실행 시 직전 백업을 timestamp 로 보존하고 새 적용.

## 절차

### Step 1. 단계 선택 (사용자 입력)

| 단계 | 한 줄 요약 | 예시 |
|---|---|---|
| **(1) YOLO** | 거의 모두 자동, 파괴 명령만 deny | "프로토타입, 위험 명령 안 씀" |
| **(2) Standard** *(권장)* | 안전 명령 자동, 위험 명령 ask, 절대 파괴 deny | 일반 개발 |
| **(3) Strict** | 읽기 전용만 자동, 그 외 ask | 보안 민감 |
| **(4) None** | `permissions` 키 자체 미설정 (또는 제거) | 기본 동작 사용 |

ask vs deny 원칙: 롤백 가능 = ask, 롤백 불가 = deny.

### Step 2. 백업

```bash
mkdir -p _backup_v0.1/.claude
if [ -f .claude/settings.json ]; then
  TS=$(date +%Y%m%d_%H%M%S)
  cp .claude/settings.json "_backup_v0.1/.claude/settings.${TS}.json"
fi

# .gitignore 에 _backup_v0.1/ 등록 (없으면)
if [ -f .gitignore ] && ! grep -q "^_backup_v0.1/" .gitignore; then
  echo "" >> .gitignore
  echo "# claude-project-bootstrap 마이그/재설정 자동 백업" >> .gitignore
  echo "_backup_v0.1/" >> .gitignore
fi
```

### Step 3. permissions 머지

선택값에 따라:

```bash
mkdir -p .claude

# (1) YOLO
NEW_PERMS=$(cat ${CLAUDE_PLUGIN_ROOT}/templates/permissions/yolo.json)

# (2) Standard
NEW_PERMS=$(cat ${CLAUDE_PLUGIN_ROOT}/templates/permissions/standard.json)

# (3) Strict
NEW_PERMS=$(cat ${CLAUDE_PLUGIN_ROOT}/templates/permissions/strict.json)

# (4) None — settings.json 의 permissions 키 제거 (hooks 키 등 다른 내용 보존)
```

### Step 4. Diff preview

생성될 `.claude/settings.json` 와 기존 파일을 `diff` 출력 → 사용자에게 보여주고 `yes/no` 받기. `no` 시 백업도 삭제하고 종료 (no-op).

### Step 5. 적용

`yes` 시 새 파일 작성. 기존 `hooks` 키는 보존 머지 (Edit / Write 둘 중 안전한 방식).

머지 로직 (Claude 가 직접 수행):
1. 기존 settings.json 을 read 해 dict 로 파싱
2. `permissions` 키만 새 값으로 교체 (또는 (4) None 시 키 삭제)
3. 결과를 settings.json 에 Write

### Step 6. 완료 리포트

```
✅ Bash 권한 단계 적용 완료

   적용 단계: (1-4)
   백업: _backup_v0.1/.claude/settings.<TS>.json
   변경 키: permissions  (hooks 등 기존 키 보존)

복원 방법:
   cp _backup_v0.1/.claude/settings.<TS>.json .claude/settings.json
```

## 참조

- spec: `${CLAUDE_PLUGIN_ROOT}/docs/specs/2026-05-05-v0.2.0-permissions-and-doc-slimming-design.md` §3, §9
- JSON 조각: `${CLAUDE_PLUGIN_ROOT}/templates/permissions/{yolo,standard,strict}.json`
