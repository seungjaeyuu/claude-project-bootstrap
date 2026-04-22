# PROJECT_FRAMEWORK 설계 결정 기록

> 본 프레임워크의 각 규약이 **왜 이렇게 결정되었는지** 의 근거 로그.
> 원 대화: 2026-04-21~22 SunnyWay 세션. 이후 새 프로젝트의 의사결정이 추가되면 본 문서 끝에 append.

---

## 배경

- **출발**: SunnyWay 프로젝트의 CLAUDE.md 규칙 최적화 요청 (Opus 4.7 업그레이드 대응)
- **범위 확장**: 다음 프로젝트 재사용 가능한 프레임워크로 추출
- **결과**: SunnyWay 실증 적용 (PR #8) + `_PROJECT_FRAMEWORK/` 저장소 분리

---

## 주요 결정

### D1. 네거티브 우선 + 4층 규칙 범례

**질문**: 규칙을 "금지만" 적는 극단이 좋은가?

**결정**: 극단은 안 좋지만 **"포지티브 중심" 에서 "네거티브 우선" 으로 기울이기**.

**근거**:
- Opus 4.7 은 일반 모범 사례를 자력 판단 가능. 프로젝트에 "특별히" 해당되는 것만 명시
- 하지만 프로젝트 고유 관습 (용어·스키마) 은 포지티브 계약 필요
- 따라서 4층:
  - 🚫 Guardrail (절대 금지, 사고 재발 방지 근거)
  - 📐 Schema (스키마·용어·명명 계약)
  - 📎 참조 (경로·환경 정보)
  - 💡 권장 (모범 사례, override 가능)

**반영**: CLAUDE_TEMPLATE.md 최상단에 범례 표.

---

### D2. 섹션 마커 (§20.3) 철회

**질문**: baseline markdown 의 각 섹션에 `<!-- baseline-section: active-tests -->` 같은 메타 주석 추가?

**결정**: **철회**. 섹션 마커 불필요.

**근거**:
- ID 별 판정은 `status.json` 이 canonical (§20.5)
- 집계 제외는 `baseline.yml` 의 `exclude_prefixes` 로 해결 (BUG-* 등)
- 섹션 마커의 원래 목적 (§2 BUG-* 전체 제외) 이 prefix 필터로 달성됨
- 마커는 단지 유지 부담만 증가시킴

**반영**: §20.3 자리는 "철회" 로 문서화.

---

### D3. 3 Template 규약 (§20.4)

**질문**: baseline markdown 의 테이블 헤더가 프로젝트마다 제각각이면?

**결정**: **3개 표준 Template 만 허용** (A/B/C).

**근거**:
- SunnyWay 의 `IOS_MASTER_TEST_BASELINE.md` 에서 **13개의 서로 다른 헤더 변형** 발견
- 의미론적으로 같은 것을 다른 이름으로 부름 (`항목` / `미실행 필수 항목` / `기준 항목`)
- 스크립트가 파싱하기 어렵고 사람도 혼란
- 3 Template 으로 통일:
  - A: 이미 실행된 ID
  - B: 미실행·소스 보강
  - C: 버그 추적용 (집계 제외)
- **기존 데이터는 즉시 변환 안 함** — 자연어 셀 재해석 시 정보 손실 위험. 편집 기회 시 점진 전환

**반영**: §20.4 + BASELINE_TEMPLATE.md.

---

### D4. 판정 Canonical = status.json (§20.5)

**질문**: baseline markdown 에 PASS/FAIL 표시 vs status.json 만 사용?

**결정**: **canonical 은 status.json 만**. baseline 의 텍스트 컬럼은 historical narrative.

**근거**:
- SunnyWay 의 기존 "최신 판정/메모" 칸이 판정·메모·후속 과제·참조 4가지가 섞임
- 이걸 한 셀에서 관리하면 자동화 불가
- 분리:
  - 판정 → `status.json`
  - 요약 → baseline "최신 요약" (판정 없이)
  - 후속 과제 → `/개발예정사항.md`
  - 참조 → baseline "이전 프롬프트 매핑" 링크

**반영**: §20.5 + `baseline_status.py` 가 status.json 만 집계.

---

### D5. 이중 배치 지양 + Trigger-based 발견

**질문**: 중요한 규칙을 여러 파일에 복붙 배치?

**결정**: **단일 SSOT + 발견 경로 최적화**.

**근거**:
- 이중 배치는 **동기화 실패 시 더 큰 혼란**
- 어디에 쓰느냐보다 **Claude 가 언제 Read 하는가**가 관건
- 3계층:
  - T1 hook (기계적 강제) — 가장 확실
  - T2 자동 로드 (루트 CLAUDE.md, MEMORY.md) — 매 세션 인지
  - T3 조건부 로드 (앱별 CLAUDE.md) — 해당 영역 작업 시
  - T4 on-demand (TESTING_FRAMEWORK, 기타 참조 문서) — Claude 가 Read 해야 발견
- T1 이 진짜 강제, T2/T3/T4 는 "발견 가능성"

**반영**:
- 루트 CLAUDE.md 는 간결 유지 (자동 로드이므로 부담 최소화)
- 상세는 TESTING_FRAMEWORK.md 등에 SSOT
- hook 로 기계 강제 추가

---

### D6. `.claude/rules/` 철폐 + `.secret/` 프로젝트 루트

**질문**: `.claude/` 아래에 프로젝트 규칙 / secrets 두는 게 적절한가?

**결정**: 둘 다 **철폐**.

**근거**:
- `.claude/` 는 Claude Code **로컬·전역 설정** 의미 (공식은 settings.json/commands/agents)
- `.claude/rules/` 는 공식 아닌 관습. hidden 폴더라 사람 인지 어려움
- `.claude/secrets/` 도 동일 문제
- 대안:
  - 규칙 문서는 **루트** 에 (TESTING_FRAMEWORK.md, CLAUDE.md 등)
  - secrets 는 루트 `.secret/` (명확한 의미, Git 에 `.secret/.gitkeep` 으로 디렉토리 존재 선언 가능)

**반영**:
- PROJECT_FRAMEWORK 의 .gitignore.template 에 `.secret/` + 관련 패턴
- CLAUDE_TEMPLATE.md 에 외부 API 키 섹션 — `.secret/` 경로 참조

---

### D7. 하네스 도입 = `baseline.yml` entry 활성화

**질문**: "하네스 도입" 이 구체적으로 언제 일어나는가?

**결정**: **`baseline.yml` 의 `apps.<name>` entry 가 활성화되는 순간**.

**근거**:
- SunnyWay DEV-066/067/068/069 같은 백로그는 **실행 시점이 모호**
- 명시적 신호 필요
- `baseline.yml` 한 파일만 수정하면 스크립트·hook 모두 자동 인식
- 단일 진실 원천(SSOT)

**반영**: `scripts/baseline.yml.template` 에 commented-out entry + 활성화 설명.

---

### D8. 베이스라인 동기화 — 트리거 기반 (§20.7)

**질문**: "매 기능 수정마다 baseline 갱신" 이 현실적인가?

**결정**: **아님. 트리거 시점 일괄 검토 + Git diff 자동 제안**.

**근거**:
- "매 기능 수정" 은 Claude 가 매 프롬프트마다 판단 필요 → 거짓양성·음성 많음
- 기능 개발은 연속적 (여러 PR)
- 대안 3가지 평가:
  - (A) 개별 커밋 — 비효율
  - (B) 기능 완료 시점 — 정의 모호
  - (C) **트리거 (E2E 세션 시작 / 릴리스 / 정기)** ← 채택
- `baseline_update_suggest.py` 가 Git diff 분석 → 제안
- 사용자 승인 후 일괄 반영

**반영**:
- §20.7 "트리거 기반 동기화"
- `/baseline-review` slash command
- L1 pre-commit hook 경고 (차단 아님) + L3 명시 호출 + L4 문서 규약

**L2 (SessionStart hook) 철회**:
- 세션마다 "최근 UI 수정 있으나 baseline 없음" 자동 알림은 과함
- L1 (커밋 시 경고) 로 충분

---

### D9. Hook 의 위험 명령 차단 (PreToolUse) 철회

**질문**: `rm -rf`, `git reset --hard` 등을 Hook 으로 기계 차단?

**결정**: **철회**. CLAUDE.md Guardrail 문서 규칙만 유지.

**근거**:
- CLAUDE.md 자동 로드로 Claude 에 인지됨
- Hook 차단은 **정당한 예외 상황** (브랜치 정리 등) 도 막음
- 유연성 손실 > 안전성 이득

**반영**: Hook 은 **검증 (dict 중복, accessibility) + 경고 (baseline 동기화)** 만.

---

### D10. MEMORY.md 프로젝트 단위 인식

**질문**: MEMORY.md 는 글로벌/로컬 중첩인가?

**결정**: **프로젝트 단위 단일 계층**. 글로벌 없음.

**근거 (실측)**:
- `~/.claude/MEMORY.md`, `~/.claude/memory/` 둘 다 **존재하지 않음**
- `~/.claude/projects/<인코딩된-경로>/memory/MEMORY.md` 가 프로젝트별 유일 경로
- 전역 기억은 `~/.claude/CLAUDE.md` 에 수동 기록

**반영**: 프레임워크는 **프로젝트 간 공유 지식은 CLAUDE_TEMPLATE.md 에** 담는다 (MEMORY.md 가 아님).

---

### D11. 100단어 답변 제한 예외

**질문**: Claude 의 "final response ≤100 단어" 규약이 분석 요청에도 적용?

**결정**: **분석·회고·비교는 예외**. 루트 CLAUDE.md 에 명시.

**근거**:
- Opus 4.7 의 향상된 reasoning 을 분석 요청에 충분히 발휘하려면 분량 여유 필요
- 단, 평상 대화는 간결 유지

**반영**: CLAUDE_TEMPLATE.md 에 규약 문장 (옵션).

---

### D12. Markdown 링크 사용 유지

**질문**: `[표시](링크)` 형태 유지?

**결정**: **유지**. GitHub 렌더링 시 편의.

**근거**:
- Claude 는 텍스트·링크 모두 context 에 수용
- 사람이 GitHub 에서 클릭 가능 링크로 문서 탐색

---

## 다음 프로젝트 적용 체크리스트

프레임워크 사용 시 순서:

1. **규약 결정** (CLAUDE_TEMPLATE.md 를 프로젝트 루트에 복사 + 플레이스홀더 치환)
2. **E2E 필요 시**: TESTING_FRAMEWORK_TEMPLATE + BASELINE_TEMPLATE + baseline.yml.template
3. **Hook 설치**: `install-hooks.sh` 실행
4. **Secrets 폴더**: `.secret/` 생성 + `.gitignore.template` 적용
5. **Git 초기 커밋**: "framework: initial scaffold"
6. **프로젝트 진행 중 규칙 갱신**: 새 사고·패턴 발견 시 CLAUDE.md + 본 DESIGN_DECISIONS.md 에 append

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-04-22 | 초판 — SunnyWay 2026-04-21~22 세션의 D1~D12 수록 |
