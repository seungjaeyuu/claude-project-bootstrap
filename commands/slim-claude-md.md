---
description: CLAUDE.md 슬림화 + 영역별 RULES 분리 (진단 → 사용자 후보별 yes/no → yes 한 후보만 분리)
argument-hint: (선택 없음 — 대화형)
allowed-tools: Read, Write, Edit, Bash(cp:*), Bash(mkdir:*), Bash(cat:*), Bash(diff:*), Bash(ls:*), Bash(rm:*), Bash(grep:*), Bash(python3:*), Bash(wc:*)
---

> **v0.3.0**: 이 커맨드는 `/init --slim` 에 통합되었습니다. 동일 기능을 실행합니다.

# /slim-claude-md — CLAUDE.md 슬림화 + RULES 분리

비대해진 `CLAUDE.md` 본체를 임계치(120줄) 이하로 슬림화. 영역별 상세는 `docs/rules/RULES_*.md` 로 분리. **자동 분리하지 않음** — 진단 리포트로 후보 제시 후 사용자가 후보별 yes/no.

## 4중 안전장치 (이 커맨드의 핵심)

1. **자동 백업**: 변경 전 `CLAUDE.md` 와 `INDEX.md` 를 `_backup_v0.1/` 으로 복사
2. **Diff preview**: 분리 후 본체와 새 RULES 파일 각각 diff 또는 미리보기 출력 → yes/no
3. **영역 독립**: 후보별로 독립 yes/no — 사용자가 일부만 분리 가능
4. **본체 자동 변경 회피**: 진단 도구(`migrate_diagnose.py`)가 후보 식별만, 사용자 confirm 후만 본체 수정

## 절차

### Step 1. 진단

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/migrate_diagnose.py CLAUDE.md
```

리포트 형식:

```
📊 분리 후보 진단

CLAUDE.md 현재 라인 수: 287줄 (임계치 120줄 초과 +167)

분리 후보 (큰 섹션 순):
  [1] §8 E2E 테스트 (현재 80줄)        → docs/rules/RULES_E2E.md 로 분리 권장
  [2] §6 데이터 정합성 (현재 22줄)      → docs/rules/RULES_DATA_INTEGRITY.md 로 분리 권장
  [3] §2 Accessibility (현재 18줄)     → docs/rules/RULES_ACCESSIBILITY.md 로 분리 권장
  ...
```

본체가 임계치 이하면 `분리 불요` 메시지 출력 후 종료.

### Step 2. 후보별 사용자 yes/no

진단 결과의 각 후보에 대해 **개별 yes/no** 받음:

```
[1] §8 E2E 테스트 (80줄) → RULES_E2E.md 로 분리하시겠습니까? (y/n)
[2] §6 데이터 정합성 (22줄) → RULES_DATA_INTEGRITY.md 로 분리하시겠습니까? (y/n)
...
```

모두 `n` 이면 본체 변경 없이 종료. 백업도 생성 안 함 (no-op).

### Step 3. 백업

후보 1개 이상 yes 받은 경우만:

```bash
mkdir -p _backup_v0.1
TS=$(date +%Y%m%d_%H%M%S)
cp CLAUDE.md "_backup_v0.1/CLAUDE.md.${TS}"
[ -f INDEX.md ] && cp INDEX.md "_backup_v0.1/INDEX.md.${TS}"

if [ -f .gitignore ] && ! grep -q "^_backup_v0.1/" .gitignore; then
  echo "" >> .gitignore
  echo "# claude-project-bootstrap 마이그/재설정 자동 백업" >> .gitignore
  echo "_backup_v0.1/" >> .gitignore
fi
```

### Step 4. 분리 실행 (각 yes 후보별)

각 후보마다:

1. **새 RULES 파일 작성**: `docs/rules/RULES_<영역>.md` 에 후보 섹션 본문 + 표준 헤더(`발견 트리거` / `상위 정책`) 추가. 플러그인의 `templates/rules/RULES_*.md.tmpl` 을 참고하되, 사용자의 customize 본문이 보존되어야 하므로 plugin 템플릿 *복사가 아닌* 사용자의 본체 섹션을 옮기는 것이 원칙.

2. **본체에서 해당 섹션 제거**: 헤딩(`## §N. ...`) 부터 다음 헤딩 직전까지 삭제.

3. **본체에 §Discovery 트리거 표 행 추가**: 기존 트리거 표가 없으면 §1 직후에 새로 추가, 있으면 행만 추가.

### Step 5. 본체 검증

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check_doc_size.py .
```

본체가 여전히 120줄 초과면 다음 후보 분리 권장 메시지 출력.

### Step 6. 완료 리포트

```
✅ CLAUDE.md 슬림화 완료

   변경 전: 287줄
   변경 후: 95줄  (목표 120줄 이내)

   분리된 RULES:
   - docs/rules/RULES_E2E.md (80줄)
   - docs/rules/RULES_DATA_INTEGRITY.md (22줄)

   백업: _backup_v0.1/CLAUDE.md.<TS>

복원 방법:
   cp _backup_v0.1/CLAUDE.md.<TS> CLAUDE.md
```

## 참조

- 진단 도구: `${CLAUDE_PLUGIN_ROOT}/scripts/migrate_diagnose.py`
- 임계치 검증: `${CLAUDE_PLUGIN_ROOT}/scripts/check_doc_size.py`
- 분리 RULES 템플릿(참고): `${CLAUDE_PLUGIN_ROOT}/templates/rules/RULES_*.md.tmpl`
- spec: `${CLAUDE_PLUGIN_ROOT}/docs/specs/2026-05-05-v0.2.0-permissions-and-doc-slimming-design.md` §5, §9
