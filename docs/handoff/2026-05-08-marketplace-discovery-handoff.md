# 인계 스크립트 — claudemarketplaces.com 게시 디스커버리

> **대상 독자**: 다음 세션의 Claude (또는 사용자 본인)
> **작성일**: 2026-05-08
> **현재 상태**: P0 4건 처리 완료 + v0.2.1 hotfix 머지·푸시 완료. P1·P2 잔여.

## 0. 한 줄 컨텍스트

`claudemarketplaces.com/marketplaces` 에 `claude-project-bootstrap` 이 게시되지 않은 원인 분석 결과, 사이트는 자동 인덱서이지만 (a) GitHub Code Search 인덱스 미포함 (b) 디스커버리 시그널(stars·topics·homepage) 부족 (c) `marketplace.json` 메타 결손 — 세 가지가 겹쳤다. P0 메타 보강 완료. 이제 인지도·release 메타·외부 직접 제출이 남았다.

## 1. 이전 세션에서 처리된 것 (P0)

| # | 항목 | 처리 결과 |
|---|---|---|
| 1 | `marketplace.json` 의 `plugins[0].version` 0.2.0 → 0.2.1 sync | ✅ |
| 2 | `marketplace.json` 에 `repository`, `license` 필드 추가 (최상위 + plugin 레벨) | ✅ |
| 3 | GitHub repo topics 8개 설정: `claude-code, claude-plugin, claude-marketplace, bootstrap, korean, e2e-testing, baseline-harness, scaffold` | ✅ |
| 4 | GitHub `homepageUrl` 설정 | ✅ |

커밋 / tag: 본 인계 스크립트와 함께 별도 hotfix 커밋으로 처리 (v0.2.1 tag 는 유지, marketplace.json sync 만 추가 커밋).

## 2. 다음 세션 P1 — 디스커버리 보강 (사이트 자동 인덱서가 발견할 확률 높이기)

### P1-1. README 에 install 명령 + 한 줄 소개 추가

**왜**: 사이트들이 README 의 첫 100줄을 미리보기로 사용. install 명령이 명시되어야 사용자가 try 하고 그 결과가 popularity signal 로 잡힘.

**무엇**: README.md 상단 (배지 위 또는 "Quick Start" 섹션) 에 다음 추가:

```markdown
## 설치

\`\`\`
/plugin marketplace add seungjaeyuu/claude-project-bootstrap
/plugin install claude-project-bootstrap@seungjaeyuu-plugins
\`\`\`
```

**검증**: `cat README.md | head -30` 으로 확인. install 명령이 렌더링되는지.

### P1-2. GitHub Release 페이지 생성 (v0.2.0, v0.2.1)

**왜**: 일부 인덱서는 GitHub Releases API 를 본다. 또한 사용자가 release notes 를 보고 신뢰도 판단.

**무엇**: 이미 tag 는 존재 (`v0.1.0`, `v0.1.1`, `v0.2.0`, `v0.2.1`). release 만 없는 상태. `gh release create` 로 각 tag 에 대한 release 페이지 생성:

```bash
# v0.2.1
gh release create v0.2.1 \
  --title "v0.2.1 — YOLO firebase deploy 과잉 차단 수정" \
  --notes-file - <<'EOF'
[CHANGELOG.md 의 ## [0.2.1] 섹션 본문 그대로]
EOF

# v0.2.0
gh release create v0.2.0 \
  --title "v0.2.0 — Bash 권한 4단계 + Firebase 격리 + CLAUDE.md 슬림화" \
  --notes-file - <<'EOF'
[CHANGELOG.md 의 ## [0.2.0] 섹션 본문 그대로]
EOF
```

**검증**: `gh release list` 에 4개 release 노출.

### P1-3. version SSOT 의사결정 + 자동 sync 메커니즘

**문제 (이전 세션에서 발견된 누락)**: v0.2.1 hotfix 시 `plugin.json` 만 0.2.1 로 올리고 `.claude-plugin/marketplace.json` 의 `plugins[0].version` 을 빠뜨림. 양쪽이 같은 정보를 중복 저장하는 한 매 릴리스마다 누락 위험.

**옵션**:

(a) **plugin.json 을 SSOT 로**: `marketplace.json` 의 `plugins[].version` 을 빈 값 또는 placeholder 로 두고, 빌드 시점에 `plugin.json` 에서 읽어 머지. 단점: Claude Code 가 marketplace.json 의 version 을 신뢰하면 placeholder 가 노출될 수 있음.

(b) **pre-commit hook 으로 sync 검증**: 두 파일의 version 이 다르면 commit 차단. 가장 단순. 권장.

(c) **release 스크립트로 양쪽 동시 갱신**: `scripts/release.sh <new_version>` 작성, sed 로 양쪽 갱신.

**다음 세션 액션**: (b) + (c) 둘 다 채택 권장.
- `scripts/check_version_sync.py` 작성 → pre-commit framework 통합
- `scripts/release.sh` 작성 → CHANGELOG entry, plugin.json, marketplace.json, git tag 한 번에

## 3. 다음 세션 P2 — 외부 디렉터리 직접 제출

### P2-1. claudemarketplaces.com 운영자 직접 컨택

**근거**: 자동 인덱서가 GitHub Code Search 에 의존한다면, stars 0 신규 레포는 인덱싱 자체가 늦다. 운영자에게 "auto-discovery 로 안 잡혀서 manual add 부탁" 직접 요청이 빠를 수 있다.

**경로**:
1. `claudemarketplaces.com` 의 Feedback 페이지 (URL 미확인 — 다음 세션에서 사이트 footer 재확인)
2. 운영자 X(Twitter) 계정 [@mertduzgun](https://x.com/mertduzgun) 직접 DM
3. 첨부 정보: 레포 URL, marketplace.json 경로, 한국어 권 사용자 타깃임을 명시

### P2-2. Anthropic 공식 디렉터리 PR

**근거**: [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) 가 가장 권위 있는 큐레이션. PR 절차 존재할 가능성.

**액션**: 해당 레포의 README, CONTRIBUTING.md 확인 후 PR 절차 따름. 한국어 권 사용자 타깃이라는 점이 채택률에 영향 줄 수 있음 — 영문 설명 보강 필요할 가능성.

### P2-3. 다른 디렉터리 병행 등록

후보:
- [buildwithclaude.com/marketplaces](https://www.buildwithclaude.com/marketplaces)
- [claudecodemarketplace.net/marketplace](https://claudecodemarketplace.net/marketplace)

각 사이트의 등록 정책 확인 (자동 인덱서 vs 수동 제출).

## 4. 다음 세션 P3 — 오픈소스 운영 모델 (사용자가 별도 의사결정 필요)

이전 세션에서 사용자가 "깃허브 공개 / 오픈소스 할까" 라고 질문. 현 상태:
- visibility = **PUBLIC** (이미 공개)
- 라이선스 = **MIT** (이미 적용)
- README, CHANGELOG 존재

즉 "공개" 액션은 이미 끝났고, 남은 건 "오픈소스 프로젝트로 운영" 의 후속 인프라:

| 항목 | 상태 | 다음 세션 검토 사항 |
|---|---|---|
| `CONTRIBUTING.md` | 없음 | 한국어 / 영문 병기 권장. 기여 가이드, 커밋 컨벤션, PR 양식 |
| `CODE_OF_CONDUCT.md` | 없음 | Contributor Covenant 표준 |
| `.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE.md` | 없음 | bug / feature / question 3종 |
| 영문 README (`README.en.md`) 또는 ko/en 분리 | 없음 | 글로벌 기여 진입장벽 — 한국어 100% 라 비한국어권 기여자 차단 |
| GitHub Actions CI | 없음 | `scripts/` 의 Python 스크립트 lint/test, JSON 스키마 검증 |
| 민감 정보 점검 | **✅ 2026-05-08 처리** | 외부 프로젝트명 8개 실명을 generic 가명으로 일괄 치환 (41건, 7개 파일). 매핑 표는 git history 비노출 — 사용자만 보유. 추가 노출 시 사용자 컨택. |

**P3-우선 액션 (다음 세션)**: 실명 → 가명 치환은 2026-05-08 세션에서 처리 완료. 다음 세션은 이 항목 skip 가능. 단 신규 추가 콘텐츠에 외부 프로젝트명 재유입이 없는지 PR 단위 점검은 계속 필요.

## 5. 다음 세션 시작 시 권장 첫 명령

```bash
# 1) 컨텍스트 빠르게 흡수
cat docs/handoff/2026-05-08-marketplace-discovery-handoff.md

# 2) 현재 디스커버리 상태 재확인 (시간 흐른 뒤 GitHub Code Search 인덱스 변동 가능)
gh api search/code -X GET -f q='filename:marketplace.json path:.claude-plugin "claude-project-bootstrap"' --jq '.total_count'

# 3) claudemarketplaces.com 현재 상태
# (Claude 가 WebFetch 로 https://claudemarketplaces.com/plugins/seungjaeyuu-plugins 확인)

# 4) 위 결과에 따라 P1 또는 P2 진입
```

## 6. 의사결정 보류 사항 요약

다음 세션 시작 시 사용자에게 확인 받을 항목:

1. ~~**P3 민감정보 점검**~~ — 2026-05-08 처리 완료
2. **version SSOT 결정** — pre-commit sync 검증 vs release 스크립트 vs 둘 다
3. **영문 README 추가 여부** — 글로벌 기여 받을지 / 한국어권 한정 운영할지
4. **Anthropic 공식 PR 시도 여부** — 기각 시 영향 평가 (없음, 그냥 retry 가능)
