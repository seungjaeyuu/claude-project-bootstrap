---
description: Add SEO guideline + validation to an existing web project — SEO 가이드라인·검증 스크립트 도입
argument-hint: (선택 없음 — 대화형)
allowed-tools: Read, Write, Edit, Bash(cp:*), Bash(mkdir:*), Bash(cat:*), Bash(diff:*), Bash(ls:*), Bash(grep:*), Bash(chmod:*), Bash(ln:*), Bash(python3:*)
---

# /seo-setup — 기존 웹 프로젝트에 SEO 도입

검색 엔진 최적화(SEO) 가이드라인·자동 검증 스크립트·pre-commit hook 을 기존 프로젝트에 추가.
`/init` 시 Q6=Yes 와 동일한 결과를 이미 초기화된 프로젝트에 적용.

## 전제 조건

1. 프로젝트 루트에 `CLAUDE.md` 가 이미 존재해야 함 (초기화된 프로젝트).
2. 웹 프로젝트여야 함 (HTML 파일이 존재하거나 생성 예정).

---

## 대화형 질의

### 1. 랜딩 페이지 HTML 경로

```
예: public/index.html, src/index.html, _design/_web/index.html

프레임워크별 기본값:
- Vite / React CRA: index.html
- Next.js (static export): out/index.html
- 정적 사이트: public/index.html
- Firebase Hosting: public/index.html
```

### 2. 사이트 URL (선택, 생략 가능)

예: `https://example.com/`. canonical / og:url 에 사용.
생략 시 `[SITE_URL]` 플레이스홀더 유지 — 나중에 수동 교체.

### 3. pre-commit hook 설치 여부 (Y/N, 기본 Y)

- Y: Git pre-commit hook 에 SEO 검증 블록 활성화 (커밋 시 자동 차단)
- N: 수동 실행만 가능 (`python3 scripts/check_seo.py <html-file>`)

---

## 실행 절차

사용자 답변을 받은 후:

### Step 1. SEO_GUIDELINE.md 생성

```bash
cp ${CLAUDE_PLUGIN_ROOT}/templates/SEO_GUIDELINE.md.tmpl ./SEO_GUIDELINE.md
```

- `[HTML_PATH]` → 질의 1 답변으로 치환
- `[SITE_URL]` → 질의 2 답변으로 치환 (생략 시 유지)
- `YYYY-MM-DD` → 오늘 날짜로 치환

이미 `SEO_GUIDELINE.md` 가 존재하면 사용자에게 덮어쓰기 확인.

### Step 2. check_seo.py 복사

```bash
mkdir -p scripts
cp ${CLAUDE_PLUGIN_ROOT}/scripts/check_seo.py ./scripts/check_seo.py
chmod +x ./scripts/check_seo.py
```

이미 존재하면 건너뜀 (버전 비교 후 업데이트 제안).

### Step 3. RULES_SEO.md 복사

```bash
mkdir -p docs/rules
cp ${CLAUDE_PLUGIN_ROOT}/templates/rules/RULES_SEO.md.tmpl ./docs/rules/RULES_SEO.md
```

### Step 4. CLAUDE.md 업데이트

**4a. 발견 트리거 표에 SEO 행 추가** (§3 표가 있을 때만):

```markdown
| 랜딩 페이지 HTML / 메타 태그 / SEO 관련 수정 | `docs/rules/RULES_SEO.md` + `SEO_GUIDELINE.md` |
```

이미 SEO 행이 있으면 건너뜀.

**4b. §NEW SEO 섹션 추가** (§변경이력 직전):

```markdown
## NEW. 🚫 웹 SEO 가이드라인 (자동 검증)

- HTML 메타 태그 수정 시 `SEO_GUIDELINE.md` 참조 필수
- 수동 검증: `python3 scripts/check_seo.py <HTML_PATH>`
- pre-commit hook 에서 자동 검증 (커밋 차단)
```

이미 "SEO 가이드라인" 섹션이 있으면 건너뜀.

### Step 5. (질의 3 == Y 시) pre-commit hook 설치/갱신

**Case A: pre-commit hook 미설치 상태**

```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/install-hooks.sh
```

전체 hook 프레임워크를 설치 (SEO 블록 §7 포함).

**Case B: pre-commit hook 이미 존재**

`scripts/pre-commit-framework.sh` 에 SEO 블록 §(7) 이 없으면:
- 최신 `pre-commit-framework.sh` 로 교체할지 사용자 확인
- 또는 기존 hook 끝(`exit $EXIT` 직전)에 SEO 블록만 수동 삽입 안내

### Step 6. 동작 확인

```bash
python3 scripts/check_seo.py <HTML_PATH>
```

파일이 존재하면 즉시 실행하여 현재 상태 보고. 미존재 시 안내만.

---

## 완료 리포트

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ SEO 설정 완료

📦 생성/갱신된 파일
   SEO_GUIDELINE.md
   scripts/check_seo.py
   docs/rules/RULES_SEO.md
   CLAUDE.md (발견 트리거 + §NEW SEO 섹션)
   .git/hooks/pre-commit (질의 3 == Y 시)

⚙  확인 필요
   • 대상 HTML: <HTML_PATH>
   • 수동 검증: python3 scripts/check_seo.py <HTML_PATH>
   • [SITE_URL] 미설정 시: SEO_GUIDELINE.md 에서 직접 교체

🛠  다음 단계
   • HTML 파일에 14개 필수 메타 태그 추가
   • robots.txt / sitemap.xml 생성
   • 배포 후 Google Search Console / 네이버 Search Advisor 등록
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 참조

- SEO 가이드라인: `SEO_GUIDELINE.md`
- 검증 스크립트: `scripts/check_seo.py` (14개 항목)
- 도메인 규칙: `docs/rules/RULES_SEO.md`
- 전체 초기화: `/init` (Q6 옵션)
