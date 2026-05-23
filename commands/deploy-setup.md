---
description: Scaffold deployment doc chain — CLAUDE.md → INDEX.md → DEPLOYMENT_INDEX.md → per-release record — 배포 문서 레이지 참조 체인 구축
argument-hint: (선택 없음 — 대화형)
allowed-tools: Read, Write, Edit, Bash(mkdir:*), Bash(cp:*), Bash(cat:*), Bash(ls:*), Bash(grep:*), Bash(date:*), Bash(diff:*)
---

# /deploy-setup — 배포 문서 레이지 참조 체인 구축

배포 절차·이력을 **4계층 레이지 참조**로 구조화한다.
각 층위는 다음 층위를 **1줄 링크**로만 참조 — Claude 세션이 필요할 때만 하위를 Read.

```
CLAUDE.md (항상 로드, ~1줄)
  → INDEX.md §배포 (한 줄 링크)
    → docs/deployment/DEPLOYMENT_INDEX.md (절차 + 이력 표)
      → docs/deployment/YYYYMMDD_vX.Y.Z.md (개별 릴리스 기록)
```

**설계 원칙**:
- CLAUDE.md 에 배포 상세를 쓰지 않는다 — 컨텍스트 비용 절감.
- DEPLOYMENT_INDEX.md 만 읽으면 전 배포 절차를 재현 가능.
- 개별 기록은 릴리스별 1파일, YYYYMMDD_ 접두어.

---

## 전제 조건

1. `CLAUDE.md` 가 존재해야 한다 (미존재 시 `/init` 먼저 실행 안내).
2. `INDEX.md` 가 존재해야 한다 (미존재 시 이 스킬에서 생성).

---

## 대화형 질의

### Q1. 배포 대상 — 복수 선택 가능

| 번호 | 대상 | 예시 |
|---|---|---|
| 1 | **App Store (iOS)** | Xcode Archive + fastlane deliver |
| 2 | **Google Play (Android)** | AAB + fastlane supply |
| 3 | **Firebase Hosting (Web)** | `firebase deploy --only hosting` |
| 4 | **Firebase Functions (Backend)** | `firebase deploy --only functions` |
| 5 | **Docker / Cloud Run** | Dockerfile + Cloud Build |
| 6 | **npm / PyPI (패키지)** | `npm publish` / `twine upload` |
| 7 | **기타** | 자유 입력 |

### Q2. (App Store 선택 시) App Store Connect 정보

아래 정보를 **아는 만큼만** 입력 (나중에 채울 수 있음):

- Apple ID (숫자, 예: `6767673933`) — 모르면 `[APPLE_ID]`
- Bundle ID (예: `com.example.myapp`) — 모르면 `[BUNDLE_ID]`
- Primary Category — 모르면 `[CATEGORY]`
- 로케일 (예: `ko, en-US`) — 모르면 `ko, en-US`
- CI 도구 (예: `fastlane`, `Xcode Cloud`, `GitHub Actions`) — 모르면 `fastlane`

### Q3. (Google Play 선택 시) Google Play 정보

- Package Name (예: `com.example.myapp`) — 모르면 `[PACKAGE_NAME]`
- Track (예: `production`, `beta`) — 모르면 `production`

### Q4. 현재 앱 버전

- Marketing version (예: `0.1.1`) — 모르면 `0.1.0`
- 첫 배포 여부 (Y/N) — Y 면 이력 표에 첫 항목으로 등록

---

## 실행 절차

### Step 0: 백업

기존 CLAUDE.md, INDEX.md 가 있으면 백업:

```bash
mkdir -p _backup_v0.1
TS=$(date +%Y%m%d_%H%M%S)
[ -f CLAUDE.md ] && cp CLAUDE.md "_backup_v0.1/CLAUDE.md.${TS}"
[ -f INDEX.md ] && cp INDEX.md "_backup_v0.1/INDEX.md.${TS}"

# .gitignore 등록
if [ -f .gitignore ] && ! grep -q "^_backup_v0.1/" .gitignore 2>/dev/null; then
  echo "" >> .gitignore
  echo "_backup_v0.1/" >> .gitignore
fi
```

### Step 1: CLAUDE.md — INDEX.md 참조 확인·추가

CLAUDE.md 를 Read 하여 `INDEX.md` 참조가 **이미 있는지** 확인.

**있으면** — skip.
**없으면** — CLAUDE.md 의 `## 변경 이력` 직전 (없으면 파일 끝) 에 아래 블록 삽입:

```markdown
## 문서 참조

> 프로젝트 전체 지도·문서 인덱스는 **[INDEX.md](INDEX.md)** 참조.
> 배포·설계·비용·핸드오프 등 상세 문서는 INDEX.md 에서 경로 확인.
```

**주의**: 기존 CLAUDE.md 의 다른 섹션은 절대 수정하지 않는다.

### Step 2: INDEX.md — 배포 섹션 확인·추가

INDEX.md 를 Read.

**파일 자체가 없으면** — 최소 구조로 생성:

```markdown
# {프로젝트 이름} INDEX

> **용도**: 프로젝트 전체 구조 지도. 신규 세션·협업자가 이 파일 한 개만 읽어도 어디에 무엇이 있는지 파악 가능.
> **규칙 파일은 [CLAUDE.md](CLAUDE.md)**, **지도는 본 INDEX.md** — 역할 분리.

---

## 배포

| 문서 | 설명 |
|---|---|
| [DEPLOYMENT_INDEX](docs/deployment/DEPLOYMENT_INDEX.md) | 배포 절차·이력. 배포 작업 시 이 파일부터 참조. |

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| {오늘 날짜} | 초판 — deploy-setup 으로 생성. |
```

**파일이 있으면** — `## 배포` 또는 `DEPLOYMENT_INDEX` 문자열 존재 여부 확인.
- 이미 있으면 skip.
- 없으면 `## 변경 이력` 직전에 아래 블록 삽입:

```markdown
### 배포

| 문서 | 설명 |
|---|---|
| [DEPLOYMENT_INDEX](docs/deployment/DEPLOYMENT_INDEX.md) | 배포 절차·이력. 배포 작업 시 이 파일부터 참조. |
```

변경 이력에 한 줄 추가: `| {오늘 날짜} | 배포 섹션 추가 — deploy-setup. |`

### Step 3: docs/deployment/ 디렉토리 + DEPLOYMENT_INDEX.md 생성

```bash
mkdir -p docs/deployment
```

`docs/deployment/DEPLOYMENT_INDEX.md` 가 **이미 있으면** — 사용자에게 알리고 덮어쓰기 여부 질의 (기본 N = skip).

**없으면** — Q1 답변에 따라 템플릿 생성:

#### App Store (iOS) 템플릿

```markdown
# App Store 배포 기록 INDEX

> {프로젝트 이름} iOS 앱의 App Store 배포 이력과 재현 절차를 관리한다.

## 배포 이력

| 버전 | 날짜 | 파일 | 상태 |
|------|------|------|------|
| {version} | {오늘 날짜} | [{YYYYMMDD}_v{version}.md]({YYYYMMDD}_v{version}.md) | 🟡 준비중 |

---

## App Store Connect 기본 정보

| 항목 | 값 |
|------|-----|
| Apple ID | {Q2 답변 또는 [APPLE_ID]} |
| Bundle ID | {Q2 답변 또는 [BUNDLE_ID]} |
| Primary Category | {Q2 답변 또는 [CATEGORY]} |
| 로케일 | {Q2 답변 또는 ko, en-US} |

---

## 배포 절차

> 프로젝트 CI 도구({CI 도구})에 맞춰 구체 명령을 여기에 기록한다.
> 첫 배포 후 실제 사용한 명령·옵션·주의사항으로 갱신할 것.

### 1. 빌드

```
# TODO: 실제 빌드 명령 기록
```

### 2. 메타데이터 업로드

```
# TODO: 실제 업로드 명령 기록
```

### 3. 심사 제출

```
# TODO: 실제 제출 절차 기록
```

---

## 메타데이터 파일 구조

> 첫 배포 후 실제 디렉토리 구조를 여기에 기록한다.

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| {오늘 날짜} | 초판 — deploy-setup 으로 스캐폴드 생성. |
```

#### Firebase Hosting 템플릿

```markdown
# Firebase Hosting 배포 기록 INDEX

> {프로젝트 이름} 웹 앱의 Firebase Hosting 배포 이력을 관리한다.

## 배포 이력

| 버전 | 날짜 | 파일 | 상태 |
|------|------|------|------|
| {version} | {오늘 날짜} | [{YYYYMMDD}_v{version}.md]({YYYYMMDD}_v{version}.md) | 🟡 준비중 |

---

## 배포 절차

### 1. 빌드 + 배포

```bash
firebase deploy --only hosting
```

### 2. 롤백

```bash
firebase hosting:channel:deploy rollback --expires 1h
```

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| {오늘 날짜} | 초판 — deploy-setup 으로 스캐폴드 생성. |
```

#### 복수 대상 선택 시

DEPLOYMENT_INDEX.md 에 **대상별 섹션**을 순서대로 나열:

```markdown
# 배포 기록 INDEX

## App Store (iOS)
(위 App Store 템플릿 내용)

---

## Firebase Hosting (Web)
(위 Firebase Hosting 템플릿 내용)
```

#### 기타·Docker·npm 등

최소 구조로 생성 (배포 이력 표 + 절차 TODO + 변경 이력). 사용자가 첫 배포 후 채우도록 안내.

### Step 4: 첫 릴리스 기록 파일 생성

`docs/deployment/{YYYYMMDD}_v{version}.md` 생성:

```markdown
# v{version} 배포 기록

> **날짜**: {오늘 날짜}
> **상태**: 🟡 준비중

---

## 변경 사항

> 이 릴리스에 포함된 주요 변경 사항을 여기에 기록한다.

- TODO

---

## 배포 단계

- [ ] 빌드 성공 확인
- [ ] 메타데이터 확인
- [ ] 배포 실행
- [ ] 배포 후 검증

---

## 이슈·메모

> 배포 중 발견한 이슈, 우회 방법, 후속 조치를 기록한다.

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| {오늘 날짜} | 초판 — 릴리스 기록 스캐폴드. |
```

### Step 5: 결과 요약 출력

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 배포 문서 레이지 참조 체인 구축 완료

체인 구조:
  CLAUDE.md
    → INDEX.md §배포
      → docs/deployment/DEPLOYMENT_INDEX.md
        → docs/deployment/{YYYYMMDD}_v{version}.md

생성/수정 파일:
  ✅ CLAUDE.md — INDEX.md 참조 {추가됨|이미 존재}
  ✅ INDEX.md — 배포 섹션 {추가됨|이미 존재}
  ✅ docs/deployment/DEPLOYMENT_INDEX.md — {생성됨|이미 존재}
  ✅ docs/deployment/{YYYYMMDD}_v{version}.md — 생성됨

다음 단계:
  1. DEPLOYMENT_INDEX.md 의 TODO 를 실제 명령으로 채우기
  2. 첫 배포 후 릴리스 기록 파일 상태를 ✅ 로 갱신
  3. 다음 릴리스 시 새 기록 파일 추가 + 이력 표 갱신
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## idempotent 보장

- CLAUDE.md 에 INDEX.md 참조가 이미 있으면 skip
- INDEX.md 에 배포 섹션이 이미 있으면 skip
- DEPLOYMENT_INDEX.md 가 이미 있으면 덮어쓰기 질의 (기본 N)
- 릴리스 기록 파일이 이미 있으면 skip + 안내

---

## 참조

- 설계 원칙: `${CLAUDE_PLUGIN_ROOT}/docs/design-principles.md`
- 레이지 참조 패턴: CLAUDE.md 에 상세를 넣지 않고 INDEX.md → 하위 INDEX → 개별 파일로 위임
- AIDEA 프로젝트 실 적용 예시: `CLAUDE.md §7` → `INDEX.md §배포` → `docs/deployment/DEPLOYMENT_INDEX.md`
