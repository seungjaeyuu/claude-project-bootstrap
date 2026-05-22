# 웹 프로젝트 SEO 자동화 통합 — 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `/init` 으로 웹 프로젝트를 초기화할 때 SEO 가이드라인·검증 스크립트·pre-commit hook 이 자동 적용되도록 claude-project-bootstrap 플러그인을 업데이트한다.

**Architecture:** AIDEA 프로젝트의 3계층 SEO 자동화(가이드라인 문서 → 검증 스크립트 → pre-commit hook)를 범용 템플릿으로 추출하여 플러그인에 통합. 기존 Q1~Q5 옵션 뒤에 Q6(SEO) 를 추가하고, Full tier 일 때 `RULES_SEO.md` 가 발견 트리거 표에 등록된다.

**Tech Stack:** Bash (hooks), Python 3 (check_seo.py), Markdown (templates)

**Reference:** AIDEA 프로젝트 (`/Users/yuseungjae/Documents/GitHub/AIDEA`)의 `SEO_GUIDELINE.md`, `scripts/check_seo.py`, `scripts/pre-commit-framework.sh` §(SEO)

---

## 파일 구조 총괄

| 변경 유형 | 파일 | 목적 |
|---|---|---|
| **Create** | `scripts/check_seo.py` | SEO 14항목 자동 검증 (HTML → PASS/FAIL) |
| **Create** | `templates/SEO_GUIDELINE.md.tmpl` | 프로젝트별 SEO 가이드라인 범용 템플릿 |
| **Create** | `templates/rules/RULES_SEO.md.tmpl` | 발견 트리거용 SEO 도메인 규칙 |
| **Modify** | `scripts/pre-commit-framework.sh` | SEO 검증 블록 추가 (§7) |
| **Modify** | `scripts/install-hooks.sh` | `check_seo.py` 복사 대상 추가 |
| **Modify** | `templates/CLAUDE.md.tmpl` | §3 발견 트리거 표에 SEO 행 추가 |
| **Modify** | `commands/init-project.md` | Q6 SEO 질문 + Step 4b 실행 절차 추가 |
| **Modify** | `commands/release.md` | 7번 SEO 점검 카테고리 추가 |

---

### Task 1: SEO 검증 스크립트 생성

AIDEA 의 `check_seo.py` 를 범용화하여 플러그인에 추가.

**Files:**
- Create: `scripts/check_seo.py`
- Reference: `/Users/yuseungjae/Documents/GitHub/AIDEA/scripts/check_seo.py`

- [ ] **Step 1: AIDEA check_seo.py 를 범용화하여 생성**

AIDEA 원본과 차이점:
- `aidea.life` 등 프로젝트 고유 문자열 제거
- docstring 을 범용 설명으로 변경
- 가이드 참조를 `SEO_GUIDELINE.md` (프로젝트 루트)로 통일
- 로직 14개 항목 동일 유지

```python
#!/usr/bin/env python3
"""
SEO 가이드라인 자동 검증 스크립트.

사용법:
    python3 scripts/check_seo.py <html-file>
    python3 scripts/check_seo.py --quiet <html-file>   # 실패 시만 출력

종료 코드:
    0 — 모든 검사 통과
    1 — 하나 이상의 검사 실패
    2 — 사용법 오류

검사 항목 (14개):
    1. <title> 너비 15~40 (네이버 기준)
    2. <meta description> 너비 45~80
    3. og:title 너비 ≤ 40
    4. og:description 너비 ≤ 80
    5. twitter:title 너비 ≤ 40
    6. twitter:description 너비 ≤ 80
    7. canonical URL 존재
    8. hreflang ko/en/x-default 존재
    9. viewport 존재
   10. h1 태그 정확히 1개
   11. JSON-LD 존재 및 유효
   12. html lang 속성 존재
   13. og:image 존재
   14. <title> 단일 태그

가이드라인 상세: SEO_GUIDELINE.md
"""

import re
import sys
import json
import unicodedata
from pathlib import Path


def naver_width(s: str) -> int:
    """네이버 너비 계산: 전각(W/F) = 2, 반각 = 1."""
    return sum(
        2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
        for ch in s
    )


def extract(page: str, pattern: str) -> str | None:
    m = re.search(pattern, page, re.DOTALL)
    return m.group(1).strip() if m else None


def run_checks(filepath: str, quiet: bool = False) -> list[str]:
    path = Path(filepath)
    if not path.exists():
        return [f"파일 없음: {filepath}"]

    page = path.read_text(encoding="utf-8")
    errors: list[str] = []

    def check(ok: bool, msg: str):
        if not ok:
            errors.append(msg)
        elif not quiet:
            print(f"  ✅ {msg}")

    if not quiet:
        print(f"🔍 SEO 검증: {filepath}")
        print()

    # 1. <title>
    title = extract(page, r"<title>(.*?)</title>")
    title_count = len(re.findall(r"<title>", page))
    if title:
        tw = naver_width(title)
        check(15 <= tw <= 40, f"title 너비: {tw} (한도 15~40)")
        check(title_count == 1, f"title 태그 수: {title_count}개 (1개 필요)")
    else:
        errors.append("<title> 태그 없음")

    # 2. <meta description>
    desc = extract(page, r'<meta\s+name="description"\s+content="(.*?)"')
    if desc:
        dw = naver_width(desc)
        check(45 <= dw <= 80, f"description 너비: {dw} (한도 45~80)")
    else:
        errors.append('<meta name="description"> 없음')

    # 3. og:title
    og_title = extract(page, r'property="og:title"\s+content="(.*?)"')
    if og_title:
        otw = naver_width(og_title)
        check(otw <= 40, f"og:title 너비: {otw} (한도 ≤40)")
    else:
        errors.append("og:title 없음")

    # 4. og:description
    og_desc = extract(page, r'property="og:description"\s+content="(.*?)"')
    if og_desc:
        odw = naver_width(og_desc)
        check(odw <= 80, f"og:description 너비: {odw} (한도 ≤80)")
    else:
        errors.append("og:description 없음")

    # 5. twitter:title
    tw_title = extract(page, r'name="twitter:title"\s+content="(.*?)"')
    if tw_title:
        ttw = naver_width(tw_title)
        check(ttw <= 40, f"twitter:title 너비: {ttw} (한도 ≤40)")
    else:
        errors.append("twitter:title 없음")

    # 6. twitter:description
    tw_desc = extract(page, r'name="twitter:description"\s+content="(.*?)"')
    if tw_desc:
        tdw = naver_width(tw_desc)
        check(tdw <= 80, f"twitter:description 너비: {tdw} (한도 ≤80)")
    else:
        errors.append("twitter:description 없음")

    # 7. canonical
    canonical = extract(page, r'<link\s+rel="canonical"\s+href="(.*?)"')
    check(canonical is not None, "canonical URL 존재")

    # 8. hreflang
    hreflangs = re.findall(r'hreflang="(.*?)"', page)
    for lang in ["ko", "en", "x-default"]:
        check(lang in hreflangs, f"hreflang {lang} 존재")

    # 9. viewport
    viewport = extract(page, r'<meta\s+name="viewport"\s+content="(.*?)"')
    check(viewport is not None, "viewport 메타 태그 존재")

    # 10. h1
    h1_count = len(re.findall(r"<h1[\s>]", page))
    check(h1_count == 1, f"h1 태그 수: {h1_count}개 (1개 필요)")

    # 11. JSON-LD
    ld_match = re.search(
        r'<script\s+type="application/ld\+json">(.*?)</script>', page, re.DOTALL
    )
    if ld_match:
        try:
            ld_data = json.loads(ld_match.group(1))
            check("@type" in ld_data, "JSON-LD @type 존재")
        except json.JSONDecodeError as e:
            errors.append(f"JSON-LD 파싱 에러: {e}")
    else:
        errors.append("JSON-LD 없음")

    # 12. html lang
    html_lang = extract(page, r'<html[^>]*\slang="(.*?)"')
    check(html_lang is not None, f"html lang 속성: {html_lang}")

    # 13. og:image
    og_image = extract(page, r'property="og:image"\s+content="(.*?)"')
    check(og_image is not None, "og:image 존재")

    return errors


def main():
    args = sys.argv[1:]
    quiet = "--quiet" in args
    files = [a for a in args if not a.startswith("--")]

    if not files:
        print("사용법: python3 scripts/check_seo.py [--quiet] <html-file>")
        sys.exit(2)

    all_errors: list[str] = []
    for f in files:
        errs = run_checks(f, quiet=quiet)
        all_errors.extend(errs)

    if all_errors:
        print()
        print(f"❌ SEO 검증 실패 ({len(all_errors)}건):")
        for e in all_errors:
            print(f"  • {e}")
        print()
        print("  가이드: SEO_GUIDELINE.md")
        sys.exit(1)
    else:
        if not quiet:
            print()
            print("✅ SEO 검증 통과 (14개 항목)")
        sys.exit(0)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 스크립트 실행 권한 부여 + 동작 확인**

```bash
chmod +x scripts/check_seo.py
python3 scripts/check_seo.py --help 2>&1 || true
# Expected: 사용법: python3 scripts/check_seo.py [--quiet] <html-file> → exit 2
```

- [ ] **Step 3: 커밋**

```bash
git add scripts/check_seo.py
git commit -m "feat: add check_seo.py — 14-point SEO validation script"
```

---

### Task 2: SEO 가이드라인 템플릿 생성

AIDEA 의 `SEO_GUIDELINE.md` 를 범용 템플릿으로 추출.

**Files:**
- Create: `templates/SEO_GUIDELINE.md.tmpl`
- Reference: `/Users/yuseungjae/Documents/GitHub/AIDEA/SEO_GUIDELINE.md`

- [ ] **Step 1: 범용 템플릿 생성**

플레이스홀더: `[HTML_PATH]` (HTML 파일 경로), `[SITE_URL]` (사이트 URL), `YYYY-MM-DD` (날짜).
AIDEA 고유 내용 제거 (`applyLang()` 참조, `aidea.life` 등).

```markdown
# 랜딩 페이지 SEO 가이드라인

> `[HTML_PATH]` 수정 시 준수해야 할 SEO 규칙.
> 자동 검증: `python3 scripts/check_seo.py [HTML_PATH]`
> pre-commit hook 에서 자동 실행됨 (커밋 차단).

---

## 1. 메타 태그 길이 한도

네이버 너비 기준: 한글/전각 = 2, ASCII/반각 = 1.

| 태그 | 네이버 한도 | Google 참고 | 비고 |
|---|---|---|---|
| `<title>` | **15~40** (너비) | ~60자 | 사이트명 + 핵심 키워드 포함 |
| `<meta description>` | **45~80** (너비) | ~160자 | 차별화된 설명, 행동 유도 |
| `og:title` | **≤40** (너비) | — | `<title>` 과 동일 권장 |
| `og:description` | **≤80** (너비) | — | `<meta description>` 과 동일 권장 |
| `twitter:title` | **≤40** (너비) | — | `<title>` 과 동일 권장 |
| `twitter:description` | **≤80** (너비) | — | `<meta description>` 과 동일 권장 |

### 너비 계산법

```python
import unicodedata
def naver_width(s):
    return sum(2 if unicodedata.east_asian_width(ch) in ('W','F') else 1 for ch in s)
```

---

## 2. 필수 메타 태그 체크리스트

| # | 태그 | 필수 | 검사 항목 |
|---|---|---|---|
| 1 | `<title>` | ✅ | 1개, 너비 15~40 |
| 2 | `<meta name="description">` | ✅ | 1개, 너비 45~80 |
| 3 | `<link rel="canonical">` | ✅ | `[SITE_URL]` |
| 4 | `<html lang="ko">` | ✅ | 기본 언어 명시 |
| 5 | `hreflang` | ✅ | ko, en, x-default 3개 |
| 6 | `viewport` | ✅ | `width=device-width` |
| 7 | `og:title` | ✅ | 너비 ≤40 |
| 8 | `og:description` | ✅ | 너비 ≤80 |
| 9 | `og:image` | ✅ | 1200x630, URL 접근 가능 |
| 10 | `og:url` | ✅ | canonical 과 동일 |
| 11 | `twitter:card` | ✅ | `summary_large_image` |
| 12 | `twitter:title` | ✅ | 너비 ≤40 |
| 13 | `twitter:description` | ✅ | 너비 ≤80 |
| 14 | JSON-LD | ✅ | 유효한 JSON, `@type` 존재 |

---

## 3. HTML 구조 규칙

- **h1 태그**: 페이지당 **정확히 1개**
- **헤딩 계층**: h1 → h2 → h3 순서 유지 (h1 없이 h2 시작 금지)
- **이미지 alt**: 모든 `<img>` 에 의미 있는 `alt` 속성 필수
- **서버 렌더링**: 핵심 콘텐츠는 HTML 마크업에 직접 포함 (JS 로딩 의존 금지)

---

## 4. robots.txt 크롤러 관리

### 권장 등록 크롤러 (15종)

**검색 엔진**: `*`, `Googlebot`, `Bingbot`
**네이버**: `Yeti`
**OpenAI**: `GPTBot`, `ChatGPT-User`, `OAI-SearchBot`
**Google AI**: `Google-Extended`
**Anthropic**: `ClaudeBot`, `Claude-Web`
**Apple**: `Applebot-Extended`
**기타 LLM**: `PerplexityBot`, `Meta-ExternalAgent`, `Bytespider`, `CCBot`

### 크롤러 추가 시

1. `User-agent:` 블록 추가
2. `Allow: /` + `Allow: /llms.txt` 명시
3. 본 문서의 크롤러 목록 업데이트

---

## 5. sitemap.xml 관리

- 페이지 추가/삭제 시 sitemap 동시 업데이트
- `<lastmod>` 를 실제 수정일로 갱신
- 배포 후 Google Search Console + 네이버 Search Advisor 에서 재제출

---

## 6. Cache-Control 정책 (호스팅 설정 참고)

| 파일 유형 | Cache-Control | 이유 |
|---|---|---|
| HTML (진입점) | `no-cache` | 항상 최신 콘텐츠 |
| JS / CSS | `max-age=604800` (7일) | 정적 에셋 |
| 이미지 / 폰트 / 동영상 | `max-age=31536000, immutable` | 변경 시 파일명 변경 |
| sitemap.xml / robots.txt | `max-age=3600` (1시간) | 적절한 갱신 빈도 |

---

## 7. 검증 방법

### 자동 (pre-commit hook)

HTML 파일이 staged 상태이면 `scripts/check_seo.py` 자동 실행.
실패 시 커밋 차단.

### 수동

```bash
python3 scripts/check_seo.py [HTML_PATH]
```

### 배포 후 외부 검증

- **Google**: Search Console → URL 검사
- **네이버**: Search Advisor → 검증 → 간단체크
- **구조화 데이터**: https://search.google.com/test/rich-results

---

## 변경 이력

| 날짜 | 변경 |
|---|---|
| YYYY-MM-DD | 초판 — claude-project-bootstrap SEO 가이드라인 적용 |
```

- [ ] **Step 2: 커밋**

```bash
git add templates/SEO_GUIDELINE.md.tmpl
git commit -m "feat: add SEO_GUIDELINE.md.tmpl — 14-point SEO checklist template"
```

---

### Task 3: SEO 도메인 규칙 파일 생성

발견 트리거 표에서 참조할 RULES 파일.

**Files:**
- Create: `templates/rules/RULES_SEO.md.tmpl`

- [ ] **Step 1: RULES_SEO.md.tmpl 생성**

기존 RULES 파일 패턴(트리거 설명 → 규칙 → 자동 검증 → 참조) 준수. 250줄 이하.

```markdown
# RULES_SEO — 웹 SEO 규칙

> **트리거**: 랜딩 페이지 HTML 수정, 메타 태그 편집, robots.txt / sitemap.xml 변경 시 참조.

---

## 🚫 절대 규칙

1. **`<title>` 너비 15~40** (네이버 기준, 전각=2 / ASCII=1). 초과·미달 시 커밋 차단.
2. **`<meta description>` 너비 45~80**. 초과·미달 시 커밋 차단.
3. **`<h1>` 페이지당 정확히 1개**. 0개 또는 2개 이상 금지.
4. **`og:image` 필수**. 1200×630 권장.
5. **canonical URL 필수**. `<link rel="canonical">` 누락 금지.
6. **JSON-LD 구조화 데이터** `@type` 필수.

---

## 📐 메타 태그 일관성

- `og:title` / `twitter:title` 은 `<title>` 과 동일 값 권장
- `og:description` / `twitter:description` 은 `<meta description>` 과 동일 값 권장
- `og:url` 은 canonical URL 과 일치해야 함
- `hreflang` 은 ko, en, x-default 3개 필수

---

## 📐 HTML 구조

- 헤딩 계층: h1 → h2 → h3 순서 유지 (건너뛰기 금지)
- 모든 `<img>` 에 의미 있는 `alt` 속성 필수 (장식 이미지: `alt=""`)
- 핵심 콘텐츠는 HTML 마크업에 직접 포함 (JS 동적 렌더링 의존 금지)

---

## 📐 robots.txt / sitemap.xml

- 페이지 추가·삭제 시 `sitemap.xml` 동시 업데이트 필수
- `<lastmod>` 를 실제 수정일로 갱신
- 크롤러 추가 시 `robots.txt` + SEO_GUIDELINE.md 크롤러 목록 동시 업데이트

---

## 자동 검증

| 시점 | 명령 | 차단 |
|---|---|---|
| 수동 | `python3 scripts/check_seo.py <html-file>` | — |
| pre-commit | 자동 (HTML 파일 staged 시) | ✅ 실패 시 차단 |
| `/release` | 7번 SEO 카테고리 | 경고 |

---

## 참조

- 전체 가이드: `SEO_GUIDELINE.md`
- 검증 스크립트: `scripts/check_seo.py` (14개 항목)
```

- [ ] **Step 2: 커밋**

```bash
git add templates/rules/RULES_SEO.md.tmpl
git commit -m "feat: add RULES_SEO.md.tmpl — SEO domain rules for discovery trigger"
```

---

### Task 4: pre-commit hook 에 SEO 검증 블록 추가

기존 §(1)~§(6) 뒤에 §(7) SEO 블록 추가.

**Files:**
- Modify: `scripts/pre-commit-framework.sh:153` (exit 문 직전)

- [ ] **Step 1: §(7) SEO 검증 블록 삽입**

`exit $EXIT` 직전에 삽입. 기존 블록과 동일한 패턴: 스크립트 존재 확인 → staged HTML 파일 필터 → 실행 → 실패 시 EXIT=1.

```bash
# ─────────────────────────────────────────────────────────────
# (7) SEO 가이드라인 검증 (HTML 파일, check_seo.py 존재 시)
# ─────────────────────────────────────────────────────────────
SEO_SCRIPT="$ROOT/scripts/check_seo.py"
if [ -f "$SEO_SCRIPT" ]; then
  HTML_FILES=$(git diff --cached --name-only --diff-filter=AM | grep -E '\.html$' || true)
  if [ -n "$HTML_FILES" ]; then
    echo "🔍 SEO 가이드라인 검증..."
    if ! echo "$HTML_FILES" | xargs python3 "$SEO_SCRIPT" --quiet; then
      echo ""
      echo "❌ 커밋 차단: SEO 가이드라인 위반"
      echo "   가이드: SEO_GUIDELINE.md"
      EXIT=1
    fi
  fi
fi
```

파일 상단 주석의 검사 항목 목록에도 추가:

```
#   (7) SEO 가이드라인 검증 (HTML 파일, check_seo.py 존재 시)
```

- [ ] **Step 2: 쉘 문법 확인**

```bash
bash -n scripts/pre-commit-framework.sh
# Expected: 출력 없음 (문법 정상)
```

- [ ] **Step 3: 커밋**

```bash
git add scripts/pre-commit-framework.sh
git commit -m "feat: add SEO validation block to pre-commit hook (§7)"
```

---

### Task 5: install-hooks.sh 에 check_seo.py 복사 대상 추가

**Files:**
- Modify: `scripts/install-hooks.sh:87` (for script in ... 루프)

- [ ] **Step 1: check_seo.py 를 복사 대상 목록에 추가**

기존 `for script in ... ; do` 루프의 목록에 `check_seo.py` 추가:

```bash
for script in check_dict_duplicates.py check_accessibility_identifiers.py check_baseline_sync.py baseline_status.py baseline_update_suggest.py posttooluse_ax_check.py check_doc_size.py check_firebase_project.py check_seo.py; do
```

(기존 목록 끝 `check_firebase_project.py` 뒤에 `check_seo.py` 추가)

- [ ] **Step 2: 커밋**

```bash
git add scripts/install-hooks.sh
git commit -m "feat: include check_seo.py in hook install script"
```

---

### Task 6: CLAUDE.md 템플릿에 SEO 발견 트리거 추가

**Files:**
- Modify: `templates/CLAUDE.md.tmpl:67` (§3 발견 트리거 표)

- [ ] **Step 1: 발견 트리거 표에 SEO 행 추가**

`| 버전 변경 / 릴리스 / main 커밋 |` 행과 `| 출시 준비 / 프로젝트 단계 점검 |` 행 사이에 삽입:

```markdown
| 랜딩 페이지 HTML / 메타 태그 / SEO 관련 수정 | `docs/rules/RULES_SEO.md` + `SEO_GUIDELINE.md` |
```

- [ ] **Step 2: 커밋**

```bash
git add templates/CLAUDE.md.tmpl
git commit -m "feat: add SEO row to CLAUDE.md discovery trigger table"
```

---

### Task 7: /init-project 커맨드에 Q6 SEO 옵션 추가

가장 큰 변경. Q6 질문 정의 + Step 실행 절차 + tier 로직 업데이트.

**Files:**
- Modify: `commands/init-project.md`

- [ ] **Step 1: Q6 SEO 질문 블록 추가**

Q5 블록과 Step 0 사이 (`---` 구분선 직전)에 삽입:

```markdown
---

#### Q6. 웹 SEO 가이드라인 적용? (기본: N, **웹 프로젝트 권장**)

- **무엇인지**: 랜딩 페이지 HTML 의 메타 태그·구조·구조화 데이터를 14개 항목으로 자동 검증. pre-commit hook 으로 커밋 차단.
- **언제**: 검색 엔진 노출이 필요한 웹 사이트/랜딩 페이지. **SPA 프레임워크(Next.js/Nuxt)** 는 빌드 결과물에 적용 가능.
- **생성**: `SEO_GUIDELINE.md` + `scripts/check_seo.py` + `docs/rules/RULES_SEO.md` + pre-commit hook 에 SEO 블록 활성화
- **기본 N 이유**: 백엔드·모바일·내부 도구에는 불필요.

##### Q6a. (Q6 == Yes 시) 랜딩 페이지 HTML 경로?

예: `public/index.html`, `src/index.html`, `_design/_web/index.html`.
프레임워크별 기본값 제안:
- Vite / React CRA: `index.html`
- Next.js (static export): `out/index.html`
- 정적 사이트: `public/index.html`
- Firebase Hosting: `public/index.html`

##### Q6b. (Q6 == Yes 시) 사이트 URL? (선택, 나중에 설정 가능)

예: `https://example.com/`. canonical / og:url 에 사용. 생략 시 `[SITE_URL]` 플레이스홀더 유지.
```

- [ ] **Step 2: Step 1 tier 결정 로직 업데이트**

기존: `Q1~Q5 **모두 N** | **Minimal**` → 변경: `Q1~Q6 **모두 N** | **Minimal**`
기존: `Q1/Q2/Q3/Q4/Q5 중 하나라도 Yes | **Full**` → 변경: `Q1~Q6 중 하나라도 Yes | **Full**`

- [ ] **Step 3: Step 2a 에 SEO RULES 복사 추가**

기존 `# Q4 Yes 시` 블록 뒤에 추가:

```bash
# Q6 Yes 시
cp ${CLAUDE_PLUGIN_ROOT}/templates/rules/RULES_SEO.md.tmpl docs/rules/RULES_SEO.md
```

- [ ] **Step 4: Step 4b (SEO 설정) 신규 섹션 추가**

Step 4a (Firebase) 와 Step 5 사이에 삽입:

```markdown
### Step 4b: Q6 Yes 시 SEO 설정

Q6 Yes 인 경우만 실행. Q6a 에서 받은 HTML 경로를 `<HTML_PATH>`, Q6b 의 사이트 URL 을 `<SITE_URL>` 라 한다.

**4b-1. SEO_GUIDELINE.md 복사·치환**:

\`\`\`bash
cp ${CLAUDE_PLUGIN_ROOT}/templates/SEO_GUIDELINE.md.tmpl ./SEO_GUIDELINE.md
\`\`\`

`[HTML_PATH]`, `[SITE_URL]`, `YYYY-MM-DD` 플레이스홀더를 실제 값으로 치환.
Q6b 생략 시 `[SITE_URL]` 은 그대로 유지 (사용자가 나중에 설정).

**4b-2. check_seo.py 복사**:

\`\`\`bash
mkdir -p scripts
cp ${CLAUDE_PLUGIN_ROOT}/scripts/check_seo.py ./scripts/check_seo.py
chmod +x ./scripts/check_seo.py
\`\`\`

**4b-3. CLAUDE.md 본체에 §NEW SEO inline (3줄)**:

Step 2 에서 복사한 `CLAUDE.md` 의 §변경이력 직전에 다음 삽입:

\`\`\`markdown
## NEW. 🚫 웹 SEO 가이드라인 (자동 검증)

- HTML 메타 태그 수정 시 `SEO_GUIDELINE.md` 참조 필수
- 수동 검증: `python3 scripts/check_seo.py <HTML_PATH>`
- pre-commit hook 에서 자동 검증 (커밋 차단)
\`\`\`
```

- [ ] **Step 5: 완료 리포트에 SEO 관련 항목 추가**

`⚙ 확인이 필요한 항목` 섹션에:

```markdown
   (Q6 == SEO 사용자만 해당)
   SEO 검증 확인:
   • 대상 HTML: <HTML_PATH>
   • 수동 검증: python3 scripts/check_seo.py <HTML_PATH>
   • Q6b 미입력 시: SEO_GUIDELINE.md 의 [SITE_URL] 을 실제 URL 로 교체 필요
```

- [ ] **Step 6: 원칙 섹션에 Q6 반영**

기존 원칙의 `Q1~Q5` 언급을 모두 `Q1~Q6` 으로 변경:
- "tier 결정 로직: Q1~Q5 모두 N 이면 Minimal" → "Q1~Q6 모두 N 이면 Minimal"
- "Q0 == None + Q4 == No" → 이 줄은 Q6 와 무관하므로 유지

- [ ] **Step 7: 커밋**

```bash
git add commands/init-project.md
git commit -m "feat: add Q6 SEO option to /init-project wizard"
```

---

### Task 8: /release 커맨드에 SEO 점검 카테고리 추가

**Files:**
- Modify: `commands/release.md`

- [ ] **Step 1: 7번 SEO 카테고리 추가**

`### 6. 접근성 (Accessibility)` 섹션 뒤에 추가:

```markdown
### 7. SEO (웹 프로젝트, SEO 설정 시)

`SEO_GUIDELINE.md` 존재 시만 실행. 미존재 시 건너뜀.

- [ ] HTML 메타 태그 14항목 자동 검증 — `check_seo.py`
- [ ] `robots.txt` 존재 + 크롤러 등록 확인
- [ ] `sitemap.xml` 존재 + `<lastmod>` 최신 여부
- [ ] JSON-LD 구조화 데이터 유효성

**검증 방법**:
\`\`\`bash
# SEO_GUIDELINE.md 에 명시된 HTML 경로로 실행
python3 scripts/check_seo.py <html-file>
\`\`\`
```

출력 형식 예시에도 7번 추가:

```
7. SEO
   ✅ 메타 태그 14항목 통과
   ✅ robots.txt 존재 (크롤러 15종)
   ⚠️ sitemap.xml lastmod 이 30일 이전 — 갱신 권장
   — 또는 —
   ⏭️ SEO_GUIDELINE.md 미존재 — 건너뜀
```

- [ ] **Step 2: 전제 조건에 SEO 참조 추가**

기존 전제 조건 목록에:

```markdown
3. `SEO_GUIDELINE.md` Read — SEO 체크리스트 확인 (있을 경우).
```

- [ ] **Step 3: 참조 섹션에 SEO 추가**

```markdown
- SEO 가이드라인: `SEO_GUIDELINE.md`
- SEO 검증 스크립트: `scripts/check_seo.py`
```

- [ ] **Step 4: 커밋**

```bash
git add commands/release.md
git commit -m "feat: add SEO check category to /release command"
```

---

### Task 9: 통합 검증

모든 변경이 일관성 있게 동작하는지 확인.

**Files:**
- All modified files (read-only verification)

- [ ] **Step 1: 템플릿 파일 존재 확인**

```bash
ls -la templates/SEO_GUIDELINE.md.tmpl templates/rules/RULES_SEO.md.tmpl scripts/check_seo.py
# Expected: 3 files exist
```

- [ ] **Step 2: pre-commit hook 문법 검증**

```bash
bash -n scripts/pre-commit-framework.sh
# Expected: 무출력 (정상)
```

- [ ] **Step 3: check_seo.py 독립 실행 검증**

```bash
python3 scripts/check_seo.py 2>&1; echo "exit: $?"
# Expected: 사용법 출력 + exit: 2
```

- [ ] **Step 4: init-project.md 일관성 확인**

```bash
# Q6 관련 키워드가 적절한 위치에 있는지 확인
grep -n "Q6" commands/init-project.md | head -20
# Expected: Q6 질문 정의, tier 로직, Step 4b 등에 등장
```

- [ ] **Step 5: install-hooks.sh 에 check_seo.py 포함 확인**

```bash
grep "check_seo.py" scripts/install-hooks.sh
# Expected: for loop 에 check_seo.py 포함
```

- [ ] **Step 6: CLAUDE.md.tmpl 발견 트리거 표에 SEO 행 확인**

```bash
grep -i "SEO" templates/CLAUDE.md.tmpl
# Expected: RULES_SEO.md 참조 행 존재
```

- [ ] **Step 7: release.md 에 SEO 카테고리 확인**

```bash
grep -n "SEO" commands/release.md
# Expected: 7번 카테고리 관련 행 존재
```

---

## 범위 외 (이 계획에 포함하지 않음)

- `/audit` 커맨드에 SEO 품질 점검 추가 (별도 계획 가능)
- Next.js metadata API / Nuxt useSeoMeta 등 프레임워크별 검증 확장
- robots.txt / sitemap.xml 자동 생성 템플릿
- README.md / CHANGELOG.md 업데이트 (별도 커밋 권장)
- `.claude-plugin/plugin.json` 버전 범프 (릴리스 시 일괄)
