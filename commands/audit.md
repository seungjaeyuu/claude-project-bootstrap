---
description: Audit quality, context size, and baseline — 품질·컨텍스트·베이스라인 점검
argument-hint: (선택) --context | --baseline | --quality
allowed-tools: Read, Bash(grep:*), Bash(wc:*), Bash(find:*), Bash(cat:*), Bash(ls:*), Bash(git:*), Bash(python3:*)
---

# /audit — 품질·컨텍스트·베이스라인 점검

## 실행 옵션

| 호출 | 점검 범위 |
|---|---|
| `/audit` | 전체 (아래 3개 모두) |
| `/audit --context` | 컨텍스트 최적화만 |
| `/audit --baseline` | 베이스라인 리뷰만 (= 기존 `/baseline-review`) |
| `/audit --quality` | 코드 품질만 |

---

## 1. 컨텍스트 점검 (--context)

### 검사 항목

1. **CLAUDE.md 줄 수**: `wc -l CLAUDE.md` — 상한 120줄
2. **RULES 총합**: `wc -l docs/rules/RULES_*.md` — 각 파일 250줄 상한
3. **활성 플러그인 수**: `.claude/settings.json` 의 `enabledPlugins` 키 분석
4. **비활성화 권장**: 프로젝트에서 사용 흔적 없는 플러그인 식별

### 비활성화 판단 휴리스틱

| 플러그인 | 미사용 신호 |
|---|---|
| `figma` | Figma 관련 파일 미감지 |
| `vercel` | `vercel.json` 미감지 |
| `firebase` | `.firebaserc` 또는 `firebase.json` 미감지 |
| 언어별 LSP | 해당 언어 파일 미감지 |

### 출력 형식

```
📊 컨텍스트 소비 현황

  CLAUDE.md         88줄  (상한 120)     ✅
  RULES 총합        420줄 (6개 파일)     ✅
  활성 플러그인      14개               ⚠️ n개 비활성화 가능

  비활성화 권장:
    <plugin>         — <미사용 근거>

  적용하시겠습니까? (Y/n)
  → Y: .claude/settings.json enabledPlugins 업데이트
```

---

## 2. 베이스라인 점검 (--baseline)

기존 `/baseline-review` 와 동일 동작. E2E 설정이 없으면 건너뜀.

### 전제 조건

- `scripts/baseline_update_suggest.py` 존재
- `scripts/baseline.yml` 존재

### 실행

```bash
python3 scripts/baseline_update_suggest.py --app <name> --since 14days
```

앱이 여러 개면 각각 실행.

---

## 3. 품질 점검 (--quality)

### 검사 항목

1. **CLAUDE.md 줄 수** — 120줄 상한
2. **각 RULES 파일 줄 수** — 250줄 상한
3. **미사용 RULES 감지** — 최근 6개월간 해당 영역 파일 변경 없으면 경고
4. **.claudeignore 존재** 확인
5. **.claude/commands/ 존재** 확인

### 출력 형식

```
📋 품질 점검

  CLAUDE.md 줄 수        88줄 / 120 상한    ✅
  RULES_E2E.md           99줄 / 250 상한    ✅
  미사용 RULES 감지       (해당 파일 — 근거)  ⚠️
  .claudeignore 존재      ✅
  .claude/commands/ 존재  ✅
```

---

## 참조

- 설계 원칙: `${CLAUDE_PLUGIN_ROOT}/docs/design-principles.md`
- 프로젝트 라이프사이클: `docs/rules/RULES_PROJECT_LIFECYCLE.md` (④ 테스트 단계)
