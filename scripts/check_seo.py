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
