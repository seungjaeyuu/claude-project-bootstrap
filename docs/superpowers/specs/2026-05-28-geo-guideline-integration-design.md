# GEO 가이드라인 통합 설계

> **날짜**: 2026-05-28
> **상태**: 승인됨
> **근거**: AIDEA v0.2.0 GEO 적용 경험 기반. 계획서 `docs/plans/20260528_geo_guideline.md` 참조.

---

## 목적

LLM 검색엔진(ChatGPT, Perplexity, Claude, Gemini 등)에서 프로젝트 웹페이지가 정확하게 인용·요약되도록 하는 GEO 체계를 claude-project-bootstrap 템플릿에 추가한다.

## 핵심 결정

| 결정 | 내용 | 근거 |
|---|---|---|
| SEO 번들 포함 | Q4(SEO) Yes 시 GEO 자동 세팅, 별도 질의 없음 | 2026년 시점에 SEO를 하면서 GEO를 안 하는 것은 비합리적 |
| 명칭 통일 | "SEO + GEO"로 표기 | 사용자가 GEO 포함을 인지하도록 |
| `--seo` 플래그 유지 | CLI 플래그 변경 없음 | `--seo-geo`는 장황. 질문 텍스트와 리포트에서 충분히 전달 |
| RULES 독립 파일 | `RULES_GEO.md.tmpl` 별도 생성 | llms.txt, FAQPage JSON-LD 등 고유 개념이 충분 |

## 변경 대상 (6개 파일)

### 1. `templates/rules/RULES_GEO.md.tmpl` (신규)

GEO 전용 규칙 문서. 기존 RULES 톤·구조 준수.

**포함 섹션:**
- 🚫 절대 규칙 4개 (llms.txt 필수, 동기화, robots.txt Allow, Content-Type)
- 📐 llms.txt 구조 규격 (간결 버전 3~5KB + 상세 버전 15~30KB)
- 📐 HTML 메타 태그 (link rel="llms", max-snippet:-1)
- 📐 JSON-LD FAQPage
- 📐 robots.txt LLM 크롤러 목록 (11종)
- 📐 호스팅 헤더 (firebase.json 등)
- 📐 sitemap.xml 등록
- 동기화 규칙 (기능 변경 시 llms.txt + llms-full.txt + FAQPage + sitemap 동시 갱신)
- 검증 방법 (배포 후 curl + Rich Results Test + Search Console)
- 참조 (SEO_GUIDELINE.md, RULES_SEO.md)

### 2. `templates/SEO_GUIDELINE.md.tmpl` — §8 추가

§7 (검증 방법) 뒤, §변경 이력 앞에 삽입:

```markdown
## 8. GEO (Generative Engine Optimization)

LLM 검색엔진이 사이트 콘텐츠를 정확히 인용하도록 최적화.

### 필수 파일
- `/llms.txt` — LLM용 간결 사이트 소개 (3~5KB)
- `/llms-full.txt` — LLM용 상세 참조 문서 (15~30KB)

### HTML 메타 태그
- `<link rel="llms" href="/llms.txt">`
- `<link rel="llms-full" href="/llms-full.txt">`
- `<meta name="robots" content="max-snippet:-1, max-image-preview:large">`

### 상세 규칙
`docs/rules/RULES_GEO.md` 참조.
```

**중복 방지**: §4 LLM 크롤러 목록과 중복하지 않음. §8에서 크롤러는 "§4 참조"로 처리.

변경 이력에 `| 2026-05-28 | §8 GEO 섹션 추가 |` 추가.

### 3. `templates/CLAUDE.md.tmpl` — 트리거 표 업데이트

§3 발견 트리거 표의 SEO 행 변경:

**Before:**
```
| 랜딩 페이지 HTML / 메타 태그 / SEO 관련 수정 | `docs/rules/RULES_SEO.md` + `SEO_GUIDELINE.md` |
```

**After:**
```
| 랜딩 페이지 HTML / 메타 태그 / SEO·GEO 관련 수정 | `docs/rules/RULES_SEO.md` + `docs/rules/RULES_GEO.md` + `SEO_GUIDELINE.md` |
```

### 4. `templates/rules/RULES_SEO.md.tmpl` — 참조 섹션 확장

기존 참조에 한 줄 추가:

```markdown
## 참조

- 전체 가이드: `SEO_GUIDELINE.md`
- GEO 규칙: `docs/rules/RULES_GEO.md`
- 검증 스크립트: `scripts/check_seo.py` (14개 항목)
```

### 5. `templates/firebase.json.tmpl` — hosting.headers 추가

`hosting` 객체에 `headers` 배열 추가:

```json
"hosting": {
  "predeploy": [...],
  "headers": [
    {
      "source": "@(llms.txt|llms-full.txt)",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=3600" },
        { "key": "Content-Type", "value": "text/plain; charset=utf-8" }
      ]
    }
  ]
}
```

기존 `predeploy` 키는 변경하지 않음.

### 6. `commands/init.md` + `commands/init-project.md` — 명칭·흐름 업데이트

**명칭 변경 지점:**

| 위치 | Before | After |
|---|---|---|
| Q4 질문 라벨 | 웹 SEO 가이드라인 적용? | 웹 SEO + GEO 가이드라인 적용? |
| Q4 설명 "무엇" | 메타 태그·구조·구조화 데이터 14개 항목 자동 검증 | + LLM 검색엔진(ChatGPT, Perplexity 등) 최적화(GEO) 포함 |
| Q4 생성 파일 | SEO_GUIDELINE.md + check_seo.py + RULES_SEO.md | + `docs/rules/RULES_GEO.md` 추가 |
| Step 4d 타이틀 | Q4 Yes 시 SEO 설정 | Q4 Yes 시 SEO + GEO 설정 |
| Step 4d 실행 | RULES_SEO.md 복사 | + RULES_GEO.md 복사 추가 |
| CLAUDE.md inline | 🚫 웹 SEO 가이드라인 | 🚫 웹 SEO + GEO 가이드라인 |
| 완료 리포트 | SEO 검증 확인 | SEO + GEO 검증 확인 + llms.txt 작성 안내 |
| 설정 변경 메뉴 2f | SEO 가이드라인 도입 | SEO + GEO 가이드라인 도입 |

**Step 4d 추가 작업 (init.md):**

```bash
# 기존 SEO 복사 뒤에 추가
cp ${CLAUDE_PLUGIN_ROOT}/templates/rules/RULES_GEO.md.tmpl docs/rules/RULES_GEO.md
```

**Step 2a (init.md/init-project.md) RULES 복사 조건에 추가:**

```bash
# Q4 Yes 시 (SEO + GEO)
cp ${CLAUDE_PLUGIN_ROOT}/templates/rules/RULES_SEO.md.tmpl docs/rules/RULES_SEO.md
cp ${CLAUDE_PLUGIN_ROOT}/templates/rules/RULES_GEO.md.tmpl docs/rules/RULES_GEO.md
```

**완료 리포트 SEO + GEO 섹션:**

```
(Q4 == SEO + GEO 사용자만 해당)
SEO + GEO 검증 확인:
• 대상 HTML: <HTML_PATH>
• 수동 검증: python3 scripts/check_seo.py <HTML_PATH>
• Q4b 미입력 시: SEO_GUIDELINE.md 의 [SITE_URL] 을 실제 URL 로 교체 필요
• GEO: llms.txt + llms-full.txt 작성 필요 (상세: docs/rules/RULES_GEO.md §llms.txt 구조 규격)
```

## 범위 외

| 항목 | 사유 |
|---|---|
| robots.txt 템플릿 신규 생성 | 현재 존재하지 않음. 별도 작업으로 분리 |
| check_seo.py에 llms.txt 검증 추가 | 기존 14개 항목 변경은 별도 작업 |
| llms.txt / llms-full.txt 샘플 템플릿 | 프로젝트마다 내용이 달라 안내만 제공 |

## 검증 방법

1. 각 tmpl 파일이 기존 스타일·톤·플레이스홀더 패턴과 일관되는지 확인
2. `commands/init.md`의 Step 4d 흐름이 Q4 Yes 시 RULES_GEO.md를 복사하는지 확인
3. CLAUDE.md.tmpl 트리거 표에서 SEO 행이 RULES_GEO.md를 포함하는지 확인
4. firebase.json.tmpl이 유효한 JSON인지 확인
