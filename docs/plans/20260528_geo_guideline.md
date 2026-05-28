# GEO (Generative Engine Optimization) 가이드라인 반영 계획

> **목적**: LLM 검색엔진(ChatGPT, Perplexity, Claude, Gemini 등)에서 프로젝트 랜딩페이지가 정확하게 인용·요약되도록 하는 GEO 체계를 claude-project-bootstrap 템플릿에 추가.
> **근거**: AIDEA v0.2.0 배포(2026-05-28)에서 실제 적용·검증된 패턴.
> **날짜**: 2026-05-28

---

## 배경

전통적 SEO(검색엔진 최적화)는 Google/네이버 크롤러가 HTML을 파싱하여 검색 결과에 노출하는 것을 목표로 한다. GEO는 여기에 **LLM 기반 검색엔진**을 추가 타겟으로 삼는다.

LLM 검색엔진은 다음을 우선 소비한다:
1. **llms.txt / llms-full.txt** — 사이트 루트에 위치한 plain text 파일. LLM이 파싱하기 최적화된 포맷.
2. **FAQPage JSON-LD** — 구조화된 Q&A. LLM이 정확한 답변을 생성하는 데 직접 활용.
3. **max-snippet:-1 메타** — 콘텐츠 인용 길이 제한 해제.
4. **robots.txt LLM 크롤러 허용** — GPTBot, ClaudeBot, PerplexityBot 등 명시적 Allow.

---

## 변경 대상 파일 (7개)

### 1. `templates/rules/RULES_GEO.md.tmpl` (신규)

GEO 전용 규칙 문서. 다음 섹션 포함:

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
LLM이 정확한 답변을 생성하기 위한 **참조 문서** 역할.

| 추가 섹션 | 설명 |
|---|---|
| 각 기능 상세 | 기능당 2~3 문단. 동작 원리, 왜 중요한지 |
| FAQ | 5~10개 Q&A (JSON-LD FAQPage와 동일 콘텐츠) |
| Use cases | 3~5개 구체적 시나리오 |
| "무엇이 아닌가" | 오해 방지. LLM의 할루시네이션 예방에 핵심 |
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

---

### 2. `templates/SEO_GUIDELINE.md.tmpl` — §8 GEO 섹션 추가

기존 §7 (검증 방법) 뒤에 새 섹션 삽입:

```markdown
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

### 상세 규칙

`docs/rules/RULES_GEO.md` 참조.
```

---

### 3. `templates/CLAUDE.md.tmpl` — 발견 트리거 표에 GEO 행 추가

| 작업 종류 | Read 대상 |
|---|---|
| 랜딩 페이지 HTML / 메타 태그 / SEO 관련 수정 | `docs/rules/RULES_SEO.md` + `docs/rules/RULES_GEO.md` + `SEO_GUIDELINE.md` |

(기존 SEO 행에 `RULES_GEO.md` 추가)

---

### 4. `templates/rules/RULES_SEO.md.tmpl` — GEO 상호 참조 추가

기존 "참조" 섹션에 추가:

```markdown
## 참조

- 전체 가이드: `SEO_GUIDELINE.md`
- GEO 규칙: `docs/rules/RULES_GEO.md`
- 검증 스크립트: `scripts/check_seo.py` (14개 항목)
```

---

### 5. `templates/firebase.json.tmpl` — llms 파일 헤더 추가

기존 호스팅 headers 배열에 추가:

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

### 6. Bootstrap 스크립트 — llms.txt 초기 생성 안내

프로젝트 초기화 시 llms.txt 스캐폴딩 메시지 또는 빈 템플릿 제공.
llms-full.txt는 기능이 충분히 정의된 후 작성하도록 안내.

---

### 7. robots.txt 템플릿 — `Allow: /llms-full.txt` 추가

기존 LLM 크롤러 블록에 `Allow: /llms-full.txt` 행 추가.

---

## 변경 이력

| 날짜 | 변경 |
|---|---|
| 2026-05-28 | 초판 — AIDEA v0.2.0 GEO 적용 경험 기반 |
