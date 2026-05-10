---
description: 문서 크기 hook 도입 — check_doc_size.py 복사 + pre-commit 통합 (CLAUDE.md 120줄 / RULES 250줄)
argument-hint: (선택 없음 — 대화형)
allowed-tools: Read, Write, Edit, Bash(cp:*), Bash(mkdir:*), Bash(cat:*), Bash(diff:*), Bash(ls:*), Bash(rm:*), Bash(grep:*), Bash(chmod:*), Bash(ln:*)
---

> **v0.3.0**: 이 커맨드는 `/init --hook` 에 통합되었습니다. 동일 기능을 실행합니다.

# /doc-size-hook — 문서 크기 검증 hook 도입

`scripts/check_doc_size.py` 를 프로젝트에 복사하고 Git pre-commit 에 통합. CLAUDE.md / RULES 줄 수가 임계치 초과 시 stderr 경고 (차단 안 함).

## 4중 안전장치

- **자동 백업**: 기존 pre-commit hook 이 있으면 `_backup_v0.1/` 으로 복사
- **Diff preview**: 추가될 hook 라인 미리보기 → yes/no
- **영역 독립**: pre-commit 의 다른 검사 라인 보존
- **idempotent**: 이미 통합된 프로젝트에서 재실행 시 중복 추가 안 함

## 절차

### Step 1. check_doc_size.py 복사 (없으면)

```bash
mkdir -p scripts
if [ ! -f scripts/check_doc_size.py ]; then
  cp ${CLAUDE_PLUGIN_ROOT}/scripts/check_doc_size.py scripts/
  chmod +x scripts/check_doc_size.py
  echo "✅ scripts/check_doc_size.py 복사"
else
  echo "ℹ️  scripts/check_doc_size.py 이미 존재 — skip"
fi
```

### Step 2. 백업 (pre-commit 변경 시)

```bash
mkdir -p _backup_v0.1/.git/hooks
TS=$(date +%Y%m%d_%H%M%S)
HOOK="$(git rev-parse --git-common-dir)/hooks/pre-commit"
[ -f "$HOOK" ] && cp "$HOOK" "_backup_v0.1/pre-commit.${TS}" || true

# scripts/pre-commit-framework.sh 도 백업
[ -f scripts/pre-commit-framework.sh ] && \
  cp scripts/pre-commit-framework.sh "_backup_v0.1/pre-commit-framework.sh.${TS}" || true

if [ -f .gitignore ] && ! grep -q "^_backup_v0.1/" .gitignore; then
  echo "" >> .gitignore
  echo "# claude-project-bootstrap 마이그/재설정 자동 백업" >> .gitignore
  echo "_backup_v0.1/" >> .gitignore
fi
```

### Step 3. pre-commit 통합

#### Case A. `scripts/pre-commit-framework.sh` 가 있는 경우 (claude-project-bootstrap 사용 프로젝트)

이미 (4) 블록이 있으면 skip. 없으면 추가:

```bash
if ! grep -q "check_doc_size.py" scripts/pre-commit-framework.sh; then
  cat >> scripts/pre-commit-framework.sh <<'EOF'

# ─────────────────────────────────────────────────────────────
# (4) 문서 크기 경고 (차단 아님) — claude-project-bootstrap v0.2.0+
# ─────────────────────────────────────────────────────────────
DOC_SIZE_SCRIPT="$ROOT/scripts/check_doc_size.py"
if [ -f "$DOC_SIZE_SCRIPT" ]; then
  python3 "$DOC_SIZE_SCRIPT" "$ROOT" || true
fi
EOF
  echo "✅ scripts/pre-commit-framework.sh 에 (4) 문서 크기 블록 추가"
else
  echo "ℹ️  pre-commit-framework.sh 에 이미 통합됨 — skip"
fi
```

#### Case B. `scripts/pre-commit-framework.sh` 가 없는 경우 (이 hook 시스템 미사용)

사용자에게 1개 옵션 제시:

```
이 프로젝트는 claude-project-bootstrap pre-commit-framework.sh 를 사용하지 않습니다.
다음 중 1개 선택:

(a) 새로 도입 — install-hooks.sh 실행 (전체 hook 시스템 + 검증 스크립트들)
(b) 단독 hook — .git/hooks/pre-commit 에 직접 추가 (다른 hook 과 충돌 가능)
(c) skip — 수동으로 CI 등에 추가
```

(a) 추천. (b) 시:

```bash
HOOK="$(git rev-parse --git-common-dir)/hooks/pre-commit"
if [ ! -f "$HOOK" ]; then
  cat > "$HOOK" <<'EOF'
#!/bin/bash
python3 "$(git rev-parse --show-toplevel)/scripts/check_doc_size.py" || true
EOF
  chmod +x "$HOOK"
elif ! grep -q "check_doc_size.py" "$HOOK"; then
  echo "" >> "$HOOK"
  echo 'python3 "$(git rev-parse --show-toplevel)/scripts/check_doc_size.py" || true' >> "$HOOK"
fi
```

### Step 4. 즉시 1회 실행 (현재 상태 점검)

```bash
python3 scripts/check_doc_size.py
```

임계치 초과 발견 시 `slim-claude-md` 커맨드 안내.

### Step 5. 완료 리포트

```
✅ 문서 크기 hook 도입 완료

   복사: scripts/check_doc_size.py
   통합: scripts/pre-commit-framework.sh (4) 블록

   현재 상태:
   - CLAUDE.md: <줄수>줄 (임계치 120) — OK 또는 분리 권장
   - 분리 RULES: <개수>개 (모두 ≤250줄)

   임계치 변경: scripts/check_doc_size.py 상단 THRESHOLDS 상수 수정
   백업: _backup_v0.1/<원본>.<TS>
```

## 참조

- 검증 스크립트: `${CLAUDE_PLUGIN_ROOT}/scripts/check_doc_size.py`
- 슬림화 도구: `/claude-project-bootstrap:slim-claude-md`
- spec: `${CLAUDE_PLUGIN_ROOT}/docs/specs/2026-05-05-v0.2.0-permissions-and-doc-slimming-design.md` §5.6, §9
