---
description: Detect the current project stage and suggest available commands — 현재 프로젝트 단계 감지 + 커맨드 안내
argument-hint: (선택 없음 — 자동 감지)
allowed-tools: Read, Bash(grep:*), Bash(find:*), Bash(cat:*), Bash(ls:*), Bash(git:*), Bash(wc:*)
---

# /guide — 단계 감지 + 커맨드 안내

프로젝트의 현재 단계를 휴리스틱으로 추정하고, 해당 단계에 유용한 커맨드와 플러그인을 안내.

## 전제 조건

`docs/rules/RULES_PROJECT_LIFECYCLE.md` Read (존재 시).

---

## 단계 감지 휴리스틱

아래 신호를 순서대로 확인하여 가장 높은 매칭 단계를 추정:

| 우선순위 | 신호 | 확인 방법 | 추정 단계 |
|---|---|---|---|
| 1 | `CLAUDE.md` 없음 또는 소스 파일 0개 | `test -f CLAUDE.md`, `find apps/ src/ -name '*.swift' -o -name '*.ts' -o -name '*.kt' -o -name '*.dart' \| head -1` | ① 기획 / ② 설계 |
| 2 | git tag 가 최근 커밋에 존재 | `git tag --points-at HEAD` | ⑥ 운영 |
| 3 | CHANGELOG 변경 또는 버전 파일 변경 | `git log --oneline -10 -- CHANGELOG.md package.json iOS/project.yml` | ⑤ 출시 |
| 4 | 최근 커밋에 test 파일 변경 다수 | `git log --oneline -10 --name-only \| grep -c -E 'test\|spec\|baseline'` | ④ 테스트 |
| 5 | 최근 커밋에 src/app 코드 변경 다수 | `git log --oneline -10 --name-only \| grep -c -E 'apps/\|src/'` | ③ 개발 |

**"추정"이므로 강제하지 않음**. 참고 수준 안내.

---

## 출력 형식

```
📍 현재 단계 추정: ③ 개발
   근거: 최근 7일간 apps/ 변경 <n>건, test 변경 <m>건

🔧 지금 유용한 명령어:
   /audit              — 코드 품질·컨텍스트 점검
   /check              — lint + typecheck + test
   RULES 자동 트리거    — CLAUDE.md §3 활성 중

📋 다음 단계 준비:
   ④ 테스트 →  /audit --baseline
   ⑤ 출시   →  /release

📖 전체 라이프사이클: docs/rules/RULES_PROJECT_LIFECYCLE.md

💡 단계별 플러그인 추천:
   ③ 개발    superpowers (활성), code-simplifier (비활성 — 리팩토링 시 활성화)
   ⑤ 출시    security-guidance (비활성 — 출시 전 활성화 권장)
```

---

## 단계별 커맨드 매핑

| 단계 | 추천 커맨드 | 설명 |
|---|---|---|
| ① 기획 | — | 도메인 종속적, 플러그인 범위 밖 |
| ② 설계 | `/init` | 프로젝트 스캐폴드 |
| ③ 개발 | `/audit --quality`, `/check` | 품질 점검, 빌드·테스트 |
| ④ 테스트 | `/audit --baseline` | 베이스라인 리뷰 |
| ⑤ 출시 | `/release` | 보안·법적·버전·i18n 체크 |
| ⑥ 운영 | `/status` | 현황 확인 |

---

## 참조

- 프로젝트 라이프사이클: `docs/rules/RULES_PROJECT_LIFECYCLE.md`
- 플러그인 설계 원칙: `${CLAUDE_PLUGIN_ROOT}/docs/design-principles.md`
