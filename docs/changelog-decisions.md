# 내부 결정 로그

> 공개 설계 원칙([`design-principles.md`](design-principles.md)) 에 포함하지 않은 보조 결정들. Claude Code 컨벤션 진화·논쟁 여지·세대별 모델 차이에 민감한 항목이라 README 에서는 링크하지 않습니다. 관심 있는 사용자가 직접 찾아 읽을 수 있도록 공개는 하되, core 원칙으로는 내세우지 않습니다.

---

## CL-02: 섹션 마커 철회

**결정**: baseline markdown 의 `<!-- baseline-section: active-tests -->` 메타 주석 계획 **철회**.

**근거**:
- ID 별 판정은 `status.json` 이 canonical
- 집계 제외는 `baseline.yml` 의 `exclude_prefixes` 로 달성 (BUG-* 등)
- 마커는 유지 부담만 증가

**향후**: 필요하다면 별도 메타 파일로 분리 (markdown 본문에 주석 삽입 대신).

---

## CL-06: `.claude/rules/` 철폐 + `.secret/` 프로젝트 루트

**결정**: `.claude/rules/`, `.claude/secrets/` 둘 다 사용하지 않음.

**근거**:
- `.claude/` 는 Claude Code **로컬·전역 설정** 디렉토리. 공식 구성은 `settings.json`, `commands/`, `agents/`.
- `.claude/rules/` 는 공식 아닌 관습. hidden 폴더라 사람 인지 어려움.

**대안**:
- 규칙 문서는 **루트** (`CLAUDE.md`, `TESTING_FRAMEWORK.md`)
- secrets 는 루트 `.secret/` (명확한 의미, `.secret/.gitkeep` 으로 디렉토리 존재 선언)

**주의**: Claude Code 컨벤션이 향후 변경되면 재검토 필요.

---

## CL-09: 위험 명령 차단 Hook 철회

**결정**: `rm -rf`, `git reset --hard` 등을 **PreToolUse hook 으로 기계 차단** 하려던 계획 **철회**. CLAUDE.md Guardrail 문서 규칙만 유지.

**근거**:
- Hook 차단은 **정당한 예외** (브랜치 정리, 임시 파일 clean 등) 도 막음
- CLAUDE.md 자동 로드로 Claude 에 인지됨 — LLM 판단에 맡기는 편이 유연
- 유연성 손실 > 안전성 이득

**논쟁 여지**: 팀 문화에 따라 강한 차단이 더 안전하다고 판단할 수 있음. Fork 후 PreToolUse hook 을 추가하는 변형 플러그인이 나올 수도 있음 — PR 로 재논의 가능.

---

## CL-10: MEMORY.md 프로젝트 단위 인식

**결정**: MEMORY.md 는 **프로젝트 단위 단일 계층**. 글로벌 계층 없음.

**근거 (2026-04 시점 실측)**:
- `~/.claude/MEMORY.md`, `~/.claude/memory/` 둘 다 존재하지 않음
- `~/.claude/projects/<인코딩된-경로>/memory/MEMORY.md` 가 프로젝트별 유일 경로
- 전역 기억은 `~/.claude/CLAUDE.md` 에 수동 기록

**반영**: 플러그인은 **프로젝트 간 공유 지식을 `templates/CLAUDE.md.tmpl` 에** 담음 (MEMORY.md 가 아님).

**주의**: Claude Code 의 memory 구조가 향후 변경될 수 있음 — 새 memory API 도입 시 재검토.

---

## CL-11: 100단어 답변 제한 예외

**결정**: Claude 의 "final response ≤100 단어" 규약이 **분석·회고·비교** 요청에는 적용되지 않음. 루트 CLAUDE.md 에 예외 명시.

**근거**:
- Opus 4.x+ 의 향상된 reasoning 을 분석에 활용하려면 분량 여유 필요
- 평상 대화는 간결 유지

**주의**: 모델 세대 바뀌면 재평가. 예를 들어 더 작은 모델의 경우 엄격한 분량 제한이 답변 품질에 도움이 될 수도 있음.

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-04-23 | 초판 — 5개 보조 결정 편입 |
