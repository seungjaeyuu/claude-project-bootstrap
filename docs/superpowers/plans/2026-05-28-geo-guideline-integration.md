# GEO 가이드라인 통합 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** LLM 검색엔진 최적화(GEO) 가이드라인을 claude-project-bootstrap 템플릿에 반영하여, `/init` SEO 옵션 선택 시 GEO도 함께 세팅되도록 한다.

**Architecture:** 기존 RULES 분리 패턴을 따라 `RULES_GEO.md.tmpl`을 독립 파일로 생성하고, SEO 관련 기존 템플릿 4개 + 커맨드 2개에 GEO 참조를 추가한다. 모든 변경은 마크다운/JSON 템플릿 파일 수정이며 실행 코드 변경 없음.

**Tech Stack:** Markdown templates (.tmpl), JSON (firebase.json.tmpl)

**Spec:** `docs/superpowers/specs/2026-05-28-geo-guideline-integration-design.md`

---

### Task 1: RULES_GEO.md.tmpl 신규 생성

**Files:**
- Create: `templates/rules/RULES_GEO.md.tmpl`

- [ ] **Step 1: 파일 생성**

`templates/rules/RULES_GEO.md.tmpl` 을 아래 내용으로 생성한다. 기존 `RULES_SEO.md.tmpl`의 톤·구조(🚫/📐 이모지 층위, 수평선 구분, 참조 섹션)를 따른다.

```markdown
# RULES_GEO — LLM 검색엔진 최적화 (GEO) 규칙

> **트리거**: 랜딩 페이지 HTML 수정, llms.txt 편집, robots.txt 변경, 주요 기능 출시 시 참조.

---

## 🚫 절대 규칙

1. **llms.txt 필수 유지** — 사이트 루트에 plain text. 프로젝트 설명·기능·기술 스택·링크 포함.
2. **llms.txt ↔ 실제 기능 동기화** — 기능 추가/삭제 시 llms.txt 동시 업데이트. 미동기화 시 LLM이 오정보 생성.
3. **robots.txt LLM 크롤러 Allow 유지** — 명시적 `Allow: /llms.txt` + `Allow: /llms-full.txt`.
4. **llms 파일 Content-Type 필수** — `text/plain; charset=utf-8`. 호스팅 설정에서 명시.

---

## 📐 llms.txt 구조 규격

### llms.txt (간결 버전, 3~5KB)

| 섹션 | 필수 | 설명 |
|---|---|---|
| 제목 + 한줄 요약 | ✅ | `# 프로젝트명 — 한줄 설명` |
| llms-full.txt 링크 | ✅ | `> For the full version, see: [URL]` |
| 주요 기능 | ✅ | 핵심 기능 블릿 |
| 기술 상세 | ✅ | 플랫폼, 엔진, 데이터 소스 |
| 핵심 사실 (Key Facts) | 💡 | LLM이 인용할 수 있는 팩트 리스트 |
| 링크 | ✅ | 웹사이트, 앱스토어, 연락처 |

### llms-full.txt (상세 버전, 15~30KB)

llms.txt의 5~10배. 모든 기능 상세 설명, FAQ, use case, "무엇이 아닌가" 섹션 포함.

| 추가 섹션 | 설명 |
|---|---|
| 각 기능 상세 | 기능당 2~3 문단. 동작 원리, 왜 중요한지 |
| FAQ | 5~10개 Q&A (JSON-LD FAQPage와 동일 콘텐츠) |
| Use cases | 3~5개 구체적 시나리오 |
| "무엇이 아닌가" | 오해 방지. LLM 할루시네이션 예방에 핵심 |
| 타겟 사용자 | 1차/2차 타겟 |
| Key Facts | 15~20개 인용 가능한 사실 문장 |

---

## 📐 HTML 메타 태그 (GEO 전용)

`<head>` 에 추가:

```html
<!-- GEO: LLM crawler hints -->
<link rel="llms" href="/llms.txt" type="text/plain" title="[PROJECT] LLM info">
<link rel="llms-full" href="/llms-full.txt" type="text/plain" title="[PROJECT] LLM full info">
<meta name="robots" content="max-snippet:-1, max-image-preview:large">
```

- `link rel="llms"`: LLM 크롤러가 `<head>`에서 llms.txt 위치를 즉시 발견
- `max-snippet:-1`: 검색엔진이 콘텐츠 인용 길이를 제한하지 않도록 허용

---

## 📐 JSON-LD FAQPage

랜딩 페이지에 **FAQPage** 구조화 데이터 추가:

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "질문?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "답변."
      }
    }
  ]
}
```

- 최소 3~5개 Q&A
- llms-full.txt의 FAQ 섹션과 내용 동기화 필수

---

## 📐 robots.txt LLM 크롤러 목록

각 크롤러에 `/llms.txt` + `/llms-full.txt` Allow:

| 크롤러 | 운영 주체 |
|---|---|
| `GPTBot` | OpenAI (ChatGPT 검색) |
| `ChatGPT-User` | OpenAI (브라우징) |
| `OAI-SearchBot` | OpenAI (SearchGPT) |
| `Google-Extended` | Google (Gemini) |
| `ClaudeBot` | Anthropic |
| `Claude-Web` | Anthropic |
| `PerplexityBot` | Perplexity |
| `Applebot-Extended` | Apple (Siri/Spotlight) |
| `Meta-ExternalAgent` | Meta AI |
| `Bytespider` | ByteDance |
| `CCBot` | Common Crawl |

---

## 📐 호스팅 헤더 (firebase.json 등)

llms 파일 전용 헤더:

```json
{
  "source": "@(llms.txt|llms-full.txt)",
  "headers": [
    { "key": "Cache-Control", "value": "public, max-age=3600" },
    { "key": "Content-Type", "value": "text/plain; charset=utf-8" }
  ]
}
```

---

## 📐 sitemap.xml

llms.txt + llms-full.txt를 sitemap에 등록:

```xml
<url>
  <loc>https://[DOMAIN]/llms.txt</loc>
  <lastmod>[DATE]</lastmod>
  <changefreq>monthly</changefreq>
  <priority>0.5</priority>
</url>
<url>
  <loc>https://[DOMAIN]/llms-full.txt</loc>
  <lastmod>[DATE]</lastmod>
  <changefreq>monthly</changefreq>
  <priority>0.5</priority>
</url>
```

---

## 동기화 규칙

기능 추가/삭제/변경 시 다음 파일을 **동시에** 업데이트:

| 파일 | 업데이트 내용 |
|---|---|
| `llms.txt` | 기능 블릿 추가/수정 |
| `llms-full.txt` | 상세 설명 + FAQ + use case 반영 |
| FAQPage JSON-LD | 신규 Q&A 추가 |
| `sitemap.xml` | `<lastmod>` 갱신 |

---

## 검증 방법

### 배포 후

1. `curl -I https://[DOMAIN]/llms.txt` → `Content-Type: text/plain` + `200 OK` 확인
2. `curl -I https://[DOMAIN]/llms-full.txt` → 동일 확인
3. Google Rich Results Test → FAQPage JSON-LD 유효성
4. Google Search Console → 사이트맵 재제출
5. 네이버 Search Advisor → 수집 요청 + 사이트맵 재제출

---

## 참조

- SEO 가이드라인: `SEO_GUIDELINE.md`
- SEO 규칙: `docs/rules/RULES_SEO.md`
```

- [ ] **Step 2: 커밋**

```bash
git add templates/rules/RULES_GEO.md.tmpl
git commit -m "feat(templates): add RULES_GEO.md.tmpl for LLM search engine optimization"
```

---

### Task 2: SEO_GUIDELINE.md.tmpl에 §8 GEO 섹션 추가

**Files:**
- Modify: `templates/SEO_GUIDELINE.md.tmpl:119-127` (§7 뒤, 변경 이력 앞)

- [ ] **Step 1: §8 GEO 섹션 삽입**

`templates/SEO_GUIDELINE.md.tmpl`에서 `---` + `## 변경 이력` 블록 직전(119행 부근)에 다음을 삽입한다:

```markdown
---

## 8. GEO (Generative Engine Optimization)

LLM 검색엔진(ChatGPT, Perplexity, Claude 등)이 사이트 콘텐츠를 정확히 인용하도록 최적화.

### 필수 파일

| 파일 | 용도 | 크기 목표 |
|---|---|---|
| `/llms.txt` | LLM용 간결 사이트 소개 | 3~5KB |
| `/llms-full.txt` | LLM용 상세 참조 문서 | 15~30KB |

### HTML 메타 태그

`<head>`에 추가 필수:
- `<link rel="llms" href="/llms.txt" type="text/plain">`
- `<link rel="llms-full" href="/llms-full.txt" type="text/plain">`
- `<meta name="robots" content="max-snippet:-1, max-image-preview:large">`

### robots.txt

LLM 크롤러에 llms 파일 접근 허용 필수. 크롤러 목록은 §4 참조.

### 상세 규칙

`docs/rules/RULES_GEO.md` 참조.
```

- [ ] **Step 2: 변경 이력 업데이트**

변경 이력 표의 기존 행 아래에 추가:

```markdown
| 2026-05-28 | §8 GEO (Generative Engine Optimization) 섹션 추가 |
```

- [ ] **Step 3: 커밋**

```bash
git add templates/SEO_GUIDELINE.md.tmpl
git commit -m "feat(templates): add §8 GEO section to SEO_GUIDELINE.md.tmpl"
```

---

### Task 3: CLAUDE.md.tmpl 트리거 표 업데이트

**Files:**
- Modify: `templates/CLAUDE.md.tmpl:66` (SEO 행)

- [ ] **Step 1: SEO 행 변경**

`templates/CLAUDE.md.tmpl` 66행을 찾는다:

```
| 랜딩 페이지 HTML / 메타 태그 / SEO 관련 수정 | `docs/rules/RULES_SEO.md` + `SEO_GUIDELINE.md` |
```

이것을 다음으로 교체한다:

```
| 랜딩 페이지 HTML / 메타 태그 / SEO·GEO 관련 수정 | `docs/rules/RULES_SEO.md` + `docs/rules/RULES_GEO.md` + `SEO_GUIDELINE.md` |
```

- [ ] **Step 2: 커밋**

```bash
git add templates/CLAUDE.md.tmpl
git commit -m "feat(templates): add RULES_GEO.md to discovery trigger table in CLAUDE.md.tmpl"
```

---

### Task 4: RULES_SEO.md.tmpl 참조 섹션에 GEO 상호참조 추가

**Files:**
- Modify: `templates/rules/RULES_SEO.md.tmpl:53-57` (참조 섹션)

- [ ] **Step 1: GEO 참조 추가**

`templates/rules/RULES_SEO.md.tmpl`의 참조 섹션을 찾는다:

```markdown
## 참조

- 전체 가이드: `SEO_GUIDELINE.md`
- 검증 스크립트: `scripts/check_seo.py` (14개 항목)
```

이것을 다음으로 교체한다:

```markdown
## 참조

- 전체 가이드: `SEO_GUIDELINE.md`
- GEO 규칙: `docs/rules/RULES_GEO.md`
- 검증 스크립트: `scripts/check_seo.py` (14개 항목)
```

- [ ] **Step 2: 커밋**

```bash
git add templates/rules/RULES_SEO.md.tmpl
git commit -m "feat(templates): add GEO cross-reference to RULES_SEO.md.tmpl"
```

---

### Task 5: firebase.json.tmpl에 hosting.headers 추가

**Files:**
- Modify: `templates/firebase.json.tmpl:14-15` (hosting 객체)

- [ ] **Step 1: hosting.headers 배열 추가**

`templates/firebase.json.tmpl`의 `"hosting"` 객체를 찾는다:

```json
  "hosting": {
    "predeploy": [
      "python3 scripts/check_firebase_project.py"
    ]
  },
```

이것을 다음으로 교체한다:

```json
  "hosting": {
    "predeploy": [
      "python3 scripts/check_firebase_project.py"
    ],
    "headers": [
      {
        "source": "@(llms.txt|llms-full.txt)",
        "headers": [
          { "key": "Cache-Control", "value": "public, max-age=3600" },
          { "key": "Content-Type", "value": "text/plain; charset=utf-8" }
        ]
      }
    ]
  },
```

- [ ] **Step 2: JSON 유효성 검증**

```bash
python3 -m json.tool templates/firebase.json.tmpl > /dev/null
```

Expected: 정상 종료 (exit 0), 에러 메시지 없음.

- [ ] **Step 3: 커밋**

```bash
git add templates/firebase.json.tmpl
git commit -m "feat(templates): add llms.txt hosting headers to firebase.json.tmpl"
```

---

### Task 6: commands/init.md 명칭·흐름 업데이트

**Files:**
- Modify: `commands/init.md` (10곳 변경)

- [ ] **Step 1: argument-hint 행 (3행)**

`--seo` 플래그 자체는 유지. 변경 없음 (확인만).

- [ ] **Step 2: 직접 옵션 호출 표 — `/init --seo` 행 (21행)**

```
| `/init --seo` | SEO 가이드라인 도입 직행 | `/seo-setup` |
```
→
```
| `/init --seo` | SEO + GEO 가이드라인 도입 직행 | `/seo-setup` |
```

- [ ] **Step 3: 설정 변경 메뉴 2f (46행)**

```
   f) SEO 가이드라인 도입
```
→
```
   f) SEO + GEO 가이드라인 도입
```

- [ ] **Step 4: 메뉴 설명 (51행)**

```
2a~2f 선택 시: 해당 기능만 단독 실행 (2f SEO 는 `/seo-setup` 커맨드 실행).
```
→
```
2a~2f 선택 시: 해당 기능만 단독 실행 (2f SEO + GEO 는 `/seo-setup` 커맨드 실행).
```

- [ ] **Step 5: Q4 라벨 + 설명 (128~134행)**

```markdown
#### Q4. 웹 SEO 가이드라인 적용? (기본: N, **웹 프로젝트 권장**)

- **무엇**: 랜딩 페이지 HTML 의 메타 태그·구조·구조화 데이터를 14개 항목으로 자동 검증. pre-commit hook 으로 커밋 차단.
- **언제**: 검색 엔진 노출이 필요한 웹 사이트/랜딩 페이지.
- **생성**: `SEO_GUIDELINE.md` + `scripts/check_seo.py` + `docs/rules/RULES_SEO.md`
```
→
```markdown
#### Q4. 웹 SEO + GEO 가이드라인 적용? (기본: N, **웹 프로젝트 권장**)

- **무엇**: 랜딩 페이지 HTML 의 메타 태그·구조·구조화 데이터를 14개 항목으로 자동 검증 + LLM 검색엔진(ChatGPT, Perplexity 등) 최적화(GEO) 포함. pre-commit hook 으로 커밋 차단.
- **언제**: 검색 엔진 노출이 필요한 웹 사이트/랜딩 페이지.
- **생성**: `SEO_GUIDELINE.md` + `scripts/check_seo.py` + `docs/rules/RULES_SEO.md` + `docs/rules/RULES_GEO.md`
```

- [ ] **Step 6: Step 2a RULES 복사 블록 — Q4 주석 + GEO 복사 추가 (213~214행)**

```bash
# Q4 Yes 시 (SEO)
cp ${CLAUDE_PLUGIN_ROOT}/templates/rules/RULES_SEO.md.tmpl docs/rules/RULES_SEO.md
```
→
```bash
# Q4 Yes 시 (SEO + GEO)
cp ${CLAUDE_PLUGIN_ROOT}/templates/rules/RULES_SEO.md.tmpl docs/rules/RULES_SEO.md
cp ${CLAUDE_PLUGIN_ROOT}/templates/rules/RULES_GEO.md.tmpl docs/rules/RULES_GEO.md
```

- [ ] **Step 7: Step 4d 타이틀 + RULES_GEO 복사 + CLAUDE.md inline 변경 (350~373행)**

Step 4d 타이틀 변경:
```
### Step 4d: Q4 Yes 시 SEO 설정
```
→
```
### Step 4d: Q4 Yes 시 SEO + GEO 설정
```

SEO_GUIDELINE 복사 뒤에 RULES_GEO 안내 추가 (check_seo.py 복사 블록 뒤, CLAUDE.md 삽입 직전):
```markdown
# RULES_GEO.md 는 Step 2a 에서 이미 복사됨.
# llms.txt + llms-full.txt 는 프로젝트별로 내용이 다르므로 사용자가 직접 작성.
# 작성 규격: docs/rules/RULES_GEO.md §llms.txt 구조 규격 참조.
```

CLAUDE.md inline 섹션 변경:
```markdown
## NEW. 🚫 웹 SEO 가이드라인 (자동 검증)

- HTML 메타 태그 수정 시 `SEO_GUIDELINE.md` 참조 필수
- 수동 검증: `python3 scripts/check_seo.py <HTML_PATH>`
- pre-commit hook 에서 자동 검증 (커밋 차단)
```
→
```markdown
## NEW. 🚫 웹 SEO + GEO 가이드라인 (자동 검증)

- HTML 메타 태그 수정 시 `SEO_GUIDELINE.md` 참조 필수
- 수동 검증: `python3 scripts/check_seo.py <HTML_PATH>`
- pre-commit hook 에서 자동 검증 (커밋 차단)
- GEO: `llms.txt` + `llms-full.txt` 작성 필요 (규격: `docs/rules/RULES_GEO.md`)
```

- [ ] **Step 8: 완료 리포트 SEO 섹션 업데이트 (없으면 추가 — init.md 에는 별도 리포트 블록 없으므로 확인)**

init.md 에는 완료 리포트 블록이 있다 (405행~). `(Q6 == SEO 사용자만 해당)` 등의 표기는 없지만, init-project.md 와 통일하기 위해 추가하지 않아도 됨 — init.md 의 리포트는 init-project.md 보다 간결하고 조건부 블록을 열거하지 않는다.

완료 리포트에 GEO 관련 플러그인 추천은 해당 없음 (기존 구조 유지).

- [ ] **Step 9: 커밋**

```bash
git add commands/init.md
git commit -m "feat(commands): update /init SEO references to SEO + GEO"
```

---

### Task 7: commands/init-project.md 명칭·흐름 업데이트

**Files:**
- Modify: `commands/init-project.md` (10곳 변경)

- [ ] **Step 1: Q6 라벨 + 설명 (117~123행)**

```markdown
#### Q6. 웹 SEO 가이드라인 적용? (기본: N, **웹 프로젝트 권장**)

- **무엇인지**: 랜딩 페이지 HTML 의 메타 태그·구조·구조화 데이터를 14개 항목으로 자동 검증. pre-commit hook 으로 커밋 차단.
```
→
```markdown
#### Q6. 웹 SEO + GEO 가이드라인 적용? (기본: N, **웹 프로젝트 권장**)

- **무엇인지**: 랜딩 페이지 HTML 의 메타 태그·구조·구조화 데이터를 14개 항목으로 자동 검증 + LLM 검색엔진(ChatGPT, Perplexity 등) 최적화(GEO) 포함. pre-commit hook 으로 커밋 차단.
```

- [ ] **Step 2: Q6 생성 파일 (121행)**

```
- **생성**: `SEO_GUIDELINE.md` + `scripts/check_seo.py` + `docs/rules/RULES_SEO.md` + pre-commit hook 에 SEO 블록 활성화
```
→
```
- **생성**: `SEO_GUIDELINE.md` + `scripts/check_seo.py` + `docs/rules/RULES_SEO.md` + `docs/rules/RULES_GEO.md` + pre-commit hook 에 SEO 블록 활성화
```

- [ ] **Step 3: 스마트 제안 (123행)**

```
- **💡 스마트 제안**: Q6 Yes 선택 시 Q3 (Hook 자동 설치) 도 Yes 권장. Q3 N 이면 `check_seo.py` 수동 실행만 가능하고 커밋 시 자동 차단이 동작하지 않음.
```
→
```
- **💡 스마트 제안**: Q6 Yes 선택 시 Q3 (Hook 자동 설치) 도 Yes 권장. Q3 N 이면 `check_seo.py` 수동 실행만 가능하고 커밋 시 자동 차단이 동작하지 않음. GEO 의 llms.txt 검증은 수동 (`curl -I`).
```

- [ ] **Step 4: Step 2a RULES 복사 — Q6 주석 + GEO 복사 추가 (214행)**

```bash
# Q6 Yes 시
cp ${CLAUDE_PLUGIN_ROOT}/templates/rules/RULES_SEO.md.tmpl docs/rules/RULES_SEO.md
```
→
```bash
# Q6 Yes 시 (SEO + GEO)
cp ${CLAUDE_PLUGIN_ROOT}/templates/rules/RULES_SEO.md.tmpl docs/rules/RULES_SEO.md
cp ${CLAUDE_PLUGIN_ROOT}/templates/rules/RULES_GEO.md.tmpl docs/rules/RULES_GEO.md
```

- [ ] **Step 5: Step 4b 타이틀 (353행)**

```
### Step 4b: Q6 Yes 시 SEO 설정
```
→
```
### Step 4b: Q6 Yes 시 SEO + GEO 설정
```

- [ ] **Step 6: Step 4b-3 CLAUDE.md inline (374~383행)**

```markdown
**4b-3. CLAUDE.md 본체에 §NEW SEO inline (3줄)**:

Step 2 에서 복사한 `CLAUDE.md` 의 §변경이력 직전에 다음 삽입:

```markdown
## NEW. 🚫 웹 SEO 가이드라인 (자동 검증)

- HTML 메타 태그 수정 시 `SEO_GUIDELINE.md` 참조 필수
- 수동 검증: `python3 scripts/check_seo.py <HTML_PATH>`
- pre-commit hook 에서 자동 검증 (커밋 차단)
```
→
```markdown
**4b-3. CLAUDE.md 본체에 §NEW SEO + GEO inline**:

Step 2 에서 복사한 `CLAUDE.md` 의 §변경이력 직전에 다음 삽입:

```markdown
## NEW. 🚫 웹 SEO + GEO 가이드라인 (자동 검증)

- HTML 메타 태그 수정 시 `SEO_GUIDELINE.md` 참조 필수
- 수동 검증: `python3 scripts/check_seo.py <HTML_PATH>`
- pre-commit hook 에서 자동 검증 (커밋 차단)
- GEO: `llms.txt` + `llms-full.txt` 작성 필요 (규격: `docs/rules/RULES_GEO.md`)
```

- [ ] **Step 7: 완료 리포트 (464~468행)**

```
   (Q6 == SEO 사용자만 해당)
   SEO 검증 확인:
   • 대상 HTML: <HTML_PATH>
   • 수동 검증: python3 scripts/check_seo.py <HTML_PATH>
   • Q6b 미입력 시: SEO_GUIDELINE.md 의 [SITE_URL] 을 실제 URL 로 교체 필요
```
→
```
   (Q6 == SEO + GEO 사용자만 해당)
   SEO + GEO 검증 확인:
   • 대상 HTML: <HTML_PATH>
   • 수동 검증: python3 scripts/check_seo.py <HTML_PATH>
   • Q6b 미입력 시: SEO_GUIDELINE.md 의 [SITE_URL] 을 실제 URL 로 교체 필요
   • GEO: llms.txt + llms-full.txt 작성 필요 (상세: docs/rules/RULES_GEO.md §llms.txt 구조 규격)
```

- [ ] **Step 8: 커밋**

```bash
git add commands/init-project.md
git commit -m "feat(commands): update /init-project SEO references to SEO + GEO"
```

---

### Task 8: 최종 검증

- [ ] **Step 1: 모든 tmpl 파일에서 GEO 참조 일관성 확인**

```bash
grep -rn "RULES_GEO\|GEO" templates/ commands/ --include="*.tmpl" --include="*.md"
```

Expected: Task 1~7 에서 변경한 파일들에서만 GEO 언급이 나타나야 한다.

- [ ] **Step 2: firebase.json.tmpl JSON 유효성 재확인**

```bash
python3 -m json.tool templates/firebase.json.tmpl > /dev/null && echo "OK"
```

Expected: `OK`

- [ ] **Step 3: 상호참조 무결성 확인**

확인 항목:
1. RULES_GEO.md.tmpl 의 참조 섹션이 `SEO_GUIDELINE.md` + `RULES_SEO.md` 를 가리키는가
2. RULES_SEO.md.tmpl 의 참조 섹션이 `RULES_GEO.md` 를 가리키는가
3. SEO_GUIDELINE.md.tmpl §8 이 `RULES_GEO.md` 를 가리키는가
4. CLAUDE.md.tmpl 트리거 표의 SEO 행이 `RULES_GEO.md` 를 포함하는가
5. init.md Step 2a 에서 Q4 Yes 시 RULES_GEO.md 를 복사하는가
6. init-project.md Step 2a 에서 Q6 Yes 시 RULES_GEO.md 를 복사하는가
