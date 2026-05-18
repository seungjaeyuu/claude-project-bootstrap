# 인계 프롬프트: claude-project-bootstrap 컨텍스트 최적화 기능 추가

> **목적**: AIDEA 프로젝트에서 수행한 컨텍스트 윈도우 최적화 경험을 claude-project-bootstrap 플러그인에 반영
> **대상 레포**: `/Users/yuseungjae/Documents/GitHub/claude-project-bootstrap/`
> **현재 버전**: v0.2.1
> **작업 성격**: 검토 → 설계 확정 → 구현 (이 프롬프트는 검토 시작점)

---

## 1. 배경: AIDEA 세션에서 발견한 문제

Claude Code 신규 세션 시작 시 MCP 도구·플러그인·커넥터·시스템 프롬프트가 컨텍스트의 약 19%(~38,800토큰/200K)를 차지.

### 컨텍스트 소비 해부 (6개 카테고리)

| 카테고리 | 토큰 추정 | 프로젝트 제어 가능 여부 |
|---|---|---|
| A. 시스템 프롬프트 + 안전 규칙 | ~8,000 | 불가 |
| B. CLAUDE.md (프로젝트 규칙) | ~6,000 | **가능** — 슬림화 |
| C. 플러그인 (스킬·에이전트·MCP) | ~8,000 | **가능** — enabledPlugins |
| D. claude.ai 커넥터 | ~3,000 | **가능** — 웹 UI / 환경변수 |
| E. Chrome 확장 MCP | ~6,000 | **가능** — 확장 비활성화 |
| F. Computer Use MCP | ~8,000 | 불가 (빌트인) |

**핵심 발견**:
1. `enabledPlugins`에서 `false`로 설정된 플러그인은 **0 토큰** (스킬·에이전트·MCP 서버 모두 미로드)
2. 필요할 때 `true`로 변경하면 다음 세션부터 즉시 활성화
3. 프로젝트별 `.claude/settings.json`으로 글로벌 설정을 오버라이드 가능
4. CLAUDE.md §8 E2E 섹션을 60줄 → 5줄로 슬림화하여 ~1,000토큰 절감 (상세는 TESTING_FRAMEWORK.md 참조로 분리)

### AIDEA에서 실행한 최적화

```json
// .claude/settings.json — enabledPlugins 추가
{
  "enabledPlugins": {
    "figma@claude-plugins-official": false,
    "notion@claude-plugins-official": false,
    "vercel@claude-plugins-official": false,
    "gitlab@claude-plugins-official": false,
    "kotlin-lsp@claude-plugins-official": false,
    "plugin-dev@claude-plugins-official": false,
    "github@claude-plugins-official": false,
    "code-simplifier@claude-plugins-official": false,
    "claude-code-setup@claude-plugins-official": false,
    "frontend-design@claude-plugins-official": false,
    "security-guidance@claude-plugins-official": false
  }
}
```

- 11개 비활성화, 7개 유지 (firebase, superpowers 등 매 세션 필요한 것)
- `github@claude-plugins-official` 비활성화해도 `git` CLI / `gh` CLI 정상 작동 확인
- 출시 로드맵에 단계별 플러그인 활성화 마커(`🔌 플러그인:`) 추가

---

## 2. 제안 기능 목록

### 제안 1: `/init-project` 플러그인 최적화 스텝 추가

**현재**: Q0~Q5 질문으로 프로젝트 타입·기능 선택 → 파일 생성. 플러그인 최적화 없음.

**제안**: Q0 직후 또는 Q5 직후에 플러그인 최적화 스텝 추가.

```
Q0a. 컨텍스트 최적화 — 불필요한 플러그인을 비활성화할까요? (Y/n)
  → Y: 사용자의 글로벌 설정(~/.claude/settings.json)에서 활성 플러그인 목록 읽기
       → 프로젝트 타입(Q1 답변)에 따라 불필요한 플러그인 식별
       → .claude/settings.json의 enabledPlugins에 false 추가
  → n: 스킵
```

**검토 사항**:
- 프로젝트 타입별 "필요/불필요" 매핑 테이블 설계 필요
  - 예: iOS 프로젝트 → `kotlin-lsp` 불필요, `vercel` 불필요
  - 예: Next.js 프로젝트 → `kotlin-lsp` 불필요, `vercel` 유용
- 글로벌 설정 읽기 권한 및 경로: `~/.claude/settings.json`
- 기존 `settings.json.tmpl`에 enabledPlugins 섹션 추가 방법
- Q0a vs Q5 이후 배치: Q0a가 나은 이유는 프로젝트 타입(Q1)만 알면 판단 가능하기 때문. 하지만 Q1 이후여야 타입을 알 수 있으므로 실제 위치는 Q1 직후가 적절할 수 있음

### 제안 2: `/context-audit` 신규 커맨드

**목적**: 기존 프로젝트의 컨텍스트 소비 현황 진단 + 최적화 제안.

```
/context-audit
  1. .claude/settings.json의 enabledPlugins 현황 읽기
  2. ~/.claude/settings.json의 글로벌 플러그인 목록 읽기
  3. CLAUDE.md 라인 수 + 예상 토큰 계산
  4. RULES_*.md 존재 여부 + 라인 수
  5. claude.ai 커넥터 존재 여부 (claudeAiMcpEverConnected)
  6. Chrome 확장 상태 (cachedChromeExtensionInstalled)
  7. 결과 리포트 + 절감 제안 출력
```

**검토 사항**:
- `~/.claude.json` 읽기 (커넥터·Chrome 확장 상태) — 개인 설정 파일 접근 범위
- 토큰 추정 로직: 정확한 카운팅 vs 라인 수 기반 근사치
- 커맨드 vs 스킬: `/context-audit`는 일회성 진단이므로 커맨드가 적절
- 출력 포맷: 표 형태의 현황 + 항목별 절감 가능 토큰 + 권장 액션

### 제안 3: CLAUDE.md 템플릿 E2E 섹션 축소

**현재**: `templates/CLAUDE.md.tmpl` (Full tier) 120줄. E2E 섹션이 포함될 경우 라인 수 증가.

**제안**: AIDEA에서 검증된 패턴 적용 — E2E 핵심 3원칙만 CLAUDE.md에, 상세는 TESTING_FRAMEWORK.md 참조.

**검토 사항**:
- 현재 CLAUDE.md.tmpl의 E2E 관련 라인 수 확인
- 이미 RULES_E2E.md.tmpl이 99줄로 분리되어 있음 → CLAUDE.md.tmpl 내 E2E 언급이 최소인지 확인
- 추가 슬림화 여지가 있는지 검토

### 제안 4: `design-principles.md` §7 컨텍스트 예산 원칙 추가

**현재**: 6개 원칙 (228줄).

**제안**: 7번째 원칙 추가 — "컨텍스트 윈도우는 유한 자원이다".

```markdown
## 7. Context budget: 컨텍스트 윈도우는 유한 자원이다

프로젝트 규칙(CLAUDE.md)·플러그인·MCP 서버·커넥터가 세션 시작 시 컨텍스트를 선점한다.
불필요한 플러그인 비활성화, CLAUDE.md 슬림화, 규칙 분리(RULES_*.md)는 모두
"사용 가능한 작업 공간"을 확보하는 행위다.

- CLAUDE.md 120줄 / RULES 250줄 상한은 품질이 아닌 **컨텍스트 예산** 근거
- enabledPlugins로 프로젝트별 플러그인 제어 가능
- 매 세션 필요하지 않은 규칙은 on-demand 로드(RULES 분리)
```

**검토 사항**:
- 기존 §1 (네거티브 우선 + 라인 수 상한)과 중복 범위 조정
- §7 신규 vs §1 확장 — 어느 쪽이 원칙 체계에 적합한지
- 라인 수 상한의 근거가 "가독성"에서 "컨텍스트 예산"으로 재정립되는 것이 기존 설명과 충돌하지 않는지

### 제안 5: INDEX.md 인덱싱 권고 강화

**현재**: `templates/INDEX.md.tmpl` (73줄)이 존재하나, "핵심 md 파일 생성 시 INDEX.md에 등록" 규칙은 명시되지 않음.

**제안**: 논의·협의·개발 완료 시 생성되는 핵심 MD 파일을 INDEX.md에 인덱싱하여, 사용자 또는 AI가 최신 버전을 바로 찾을 수 있게 하는 권고사항 추가.

```markdown
<!-- INDEX.md.tmpl에 추가할 섹션 -->
## 주요 문서 인덱스

> 신규 문서 작성 시 이 섹션에 등록한다. 카테고리별 최신·핵심 문서만 유지.
> 과거 이력·핸드오프 문서는 해당 디렉토리에서 직접 탐색.

| 문서 | 설명 |
|---|---|
| (프로젝트 진행에 따라 추가) | |
```

**추가로 검토할 사항**:
- CLAUDE.md 문서 규칙(§5)에 "핵심 문서 생성 시 INDEX.md 등록" 항목을 💡 권장으로 추가할지
- INDEX.md 자체의 라인 수 관리 — 문서가 많아지면 INDEX.md도 비대해짐. 카테고리별 최신·핵심만 유지하는 정리 기준 필요
- AI 세션에서 자동 등록할지 vs 사용자가 수동 등록할지 — 자동이면 CLAUDE.md에 규칙화, 수동이면 INDEX.md 자체에 안내문만
- AIDEA의 INDEX.md 실제 운용 사례 참조: 비용·요금제 4건, 설계·아키텍처 7건, 현재 핸드오프 5건, 운영·절차 3건으로 카테고리 분류

### 제안 6: 플러그인/스킬 추천 기능

**현재**: claude-project-bootstrap에 플러그인/스킬 추천 로직 없음. 커맨드는 독립적이며 보완 플러그인을 제안하지 않음.

**제안**: 작업 수행 시 최상의 퀄리티를 위해 관련 플러그인/스킬을 추천하는 메커니즘 도입.

**구현 방향 후보**:

#### 방향 A: `/init-project` 시점 정적 추천
프로젝트 타입(Q1)에 따라 "이 프로젝트에 유용한 플러그인/스킬" 목록을 출력.

```
프로젝트 타입: iOS (SwiftUI + Firebase)
추천 플러그인:
  ✅ firebase — Firebase 프로젝트 관리 (이미 활성)
  💡 frontend-design — UI 폴리싱 단계에서 활성화 권장
  💡 security-guidance — 출시 전 보안 감사에서 활성화 권장
  ℹ️ figma — Figma 디자인 연동 시 활성화
```

#### 방향 B: 작업 컨텍스트 기반 동적 추천 (스킬)
특정 작업을 시작할 때 관련 스킬/플러그인을 추천하는 스킬 또는 CLAUDE.md 규칙.

```
<!-- CLAUDE.md 또는 INDEX.md에 추가 -->
## 플러그인 활성화 가이드

| 작업 | 추천 플러그인 | 활성화 시점 |
|---|---|---|
| UI 디자인 폴리싱 | frontend-design | 개발 후반 |
| 보안 감사 | security-guidance | 출시 전 |
| Figma→코드 변환 | figma | 디자인 시스템 구축 시 |
| Vercel 배포 | vercel | 웹 프로젝트 배포 시 |
| 코드 리뷰·정리 | code-simplifier | 리팩토링 시 |
```

#### 방향 C: 추천 엔진 스킬 (superpowers 연동)
`superpowers` 플러그인의 스킬 시스템과 연동하여, 작업 시작 시 자동으로 관련 스킬을 트리거하는 메커니즘.

**검토 사항**:
- 방향 A(정적)는 구현 간단하지만 프로젝트 초기에만 유용
- 방향 B(가이드 테이블)는 CLAUDE.md/INDEX.md에 정적 테이블로 유지 — 구현 비용 최소, 하지만 수동 관리
- 방향 C(동적)는 구현 복잡도 높음 — 별도 스킬 개발 + superpowers 의존성
- 실용성 우선: A + B 조합이 가장 현실적 (init-project에서 초기 추천 + INDEX.md에 가이드 테이블)
- 플러그인 목록이 사용자마다 다름 — 글로벌 설정 읽기로 "설치된 플러그인" 파악 필요

---

## 3. 참조 파일

### claude-project-bootstrap 핵심 파일

| 파일 | 용도 | 이번 작업 관련도 |
|---|---|---|
| `.claude-plugin/plugin.json` | 플러그인 메타 (v0.2.1) | 버전 업 필요 시 |
| `commands/init-project.md` (423줄) | 메인 스캐폴딩 — Q0~Q5 | 제안 1 (Q0a 추가) |
| `templates/settings.json.tmpl` | .claude/settings.json 템플릿 | 제안 1 (enabledPlugins 추가) |
| `templates/INDEX.md.tmpl` (73줄) | INDEX.md 템플릿 | 제안 5 (인덱싱 섹션) |
| `templates/CLAUDE.md.tmpl` (120줄) | Full tier CLAUDE.md | 제안 3 (E2E 축소) |
| `docs/design-principles.md` (228줄) | 설계 원칙 6개 | 제안 4 (§7 추가) |
| `commands/slim-claude-md.md` (112줄) | CLAUDE.md 슬림화 | 제안 2 연관 |
| `scripts/check_doc_size.py` | 라인 수 경고 | 제안 4 근거 |

### AIDEA 실제 적용 사례 (참조용)

| 파일 | 내용 |
|---|---|
| `AIDEA/.claude/settings.json` | enabledPlugins 11개 비활성화 실례 |
| `AIDEA/CLAUDE.md` §8 | E2E 섹션 슬림화 실례 (60줄→5줄) |
| `AIDEA/INDEX.md` | 카테고리별 문서 인덱싱 실례 |
| `AIDEA/개발예정사항.md` | 로드맵 단계별 플러그인 마커(🔌) 실례 |

---

## 4. 작업 순서 제안

1. **현재 코드 확인** — 위 핵심 파일들의 최신 상태 읽기
2. **제안 1~6 각각에 대해 구현 여부·범위 확정** — 사용자와 논의
3. **설계 확정 후 구현** — 변경 파일 목록 + 영향 범위 정리 → 구현
4. **design-principles.md 업데이트** — 새 원칙 추가 시
5. **CHANGELOG.md 업데이트** — 버전 범프 (v0.3.0?)
6. **테스트** — 신규/변경 커맨드를 실제 프로젝트에서 실행하여 검증

---

## 5. 성공 기준

- [ ] 제안 1~6 각각에 대해 구현/보류/변형 결정 완료
- [ ] 구현 결정된 항목의 코드 변경 완료
- [ ] design-principles.md 일관성 유지 (중복·충돌 없음)
- [ ] 기존 커맨드(init-project, slim-claude-md 등) 기능 회귀 없음
- [ ] CHANGELOG.md + plugin.json 버전 업데이트
