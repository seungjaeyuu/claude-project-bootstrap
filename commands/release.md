---
description: Pre-release readiness check — security, legal, version, i18n, tests, accessibility — 출시 준비 점검
argument-hint: (선택 없음 — 자동 점검)
allowed-tools: Read, Bash(grep:*), Bash(find:*), Bash(cat:*), Bash(ls:*), Bash(git:*), Bash(wc:*), Bash(python3:*)
---

# /release — 출시 준비 체크

프로젝트 라이프사이클 ⑤ 출시 준비 (Pre-release) 단계의 체크리스트를 자동 점검.

## 전제 조건

1. `docs/rules/RULES_PROJECT_LIFECYCLE.md` Read — 체크리스트 확인.
2. `docs/rules/RULES_VERSIONING.md` Read — 빌드번호 규칙 확인.
3. `SEO_GUIDELINE.md` Read — SEO 체크리스트 확인 (있을 경우).

---

## 점검 항목 (7개 카테고리)

### 1. 버전·빌드번호

- [ ] 빌드번호 정합성 — 정본 파일에서 현재 값 확인
- [ ] CHANGELOG.md — 현재 버전 항목 존재 여부
- [ ] package.json / project.yml 등 — semver 값 확인

**검증 방법**:
```bash
# 플랫폼별 자동 감지
grep 'CURRENT_PROJECT_VERSION:' iOS/project.yml 2>/dev/null
grep 'versionCode' android/app/build.gradle* 2>/dev/null
grep '"version"\|"buildNumber"' package.json 2>/dev/null
grep -m1 '## ' CHANGELOG.md 2>/dev/null
```

### 2. 보안

- [ ] `.secret/` → `.gitignore` 에 포함 확인
- [ ] `.env*` 파일 커밋 여부 — `git ls-files .env*`
- [ ] Firebase 사용 시 predeploy hook 활성 확인

### 3. 법적 문서

- [ ] 개인정보처리방침 존재 — `PRIVACY.md` 또는 `privacy-policy` 관련 파일 탐색
- [ ] 이용약관 존재 — `TERMS.md` 또는 `terms-of-service` 관련 파일 탐색

### 4. 국제화 (i18n)

사용자에게 질의: "다국어 지원이 필요합니까? (Y/N)"
- Y 시: 지원 언어 목록 요청 → 미번역 항목 점검 가이드 제공
- N 시: 건너뜀

### 5. 테스트 (E2E 설정 시)

- E2E 설정이 없으면 건너뜀
- 설정이 있으면: `/audit --baseline` 실행과 동일

### 6. 접근성 (Accessibility)

`docs/rules/RULES_ACCESSIBILITY.md` 존재 시만 실행 (init 시 Accessibility 검증 활성화한 프로젝트).
미존재 시 건너뜀.

- [ ] AX identifier 스키마 검증 — snake_case + type 접미사
- [ ] 인터랙티브 요소 `.accessibilityIdentifier()` 부여 여부
- [ ] 전역 identifier 중복 (cross-file)

**검증 방법**:
```bash
# Swift 소스 디렉토리 자동 감지 후 실행
# --features 는 프로젝트별 feature prefix (ACCESSIBILITY_IDENTIFIERS.md 참조)
find . -type d -name "*.xcodeproj" -o -name "Package.swift" 2>/dev/null | head -1
python3 scripts/check_accessibility_identifiers.py --recursive \
    --features auth,settings,common \
    <iOS 소스 경로>
```

**판정 기준**:
- exit 0 → PASS
- exit 1 → 위반 존재 (세부 내역은 stderr)
- `--strict-missing` 옵션으로 인터랙티브 요소 누락도 위반 처리 가능

### 7. SEO (웹 프로젝트, SEO 설정 시)

`SEO_GUIDELINE.md` 존재 시만 실행. 미존재 시 건너뜀.

- [ ] HTML 메타 태그 14항목 자동 검증 — `check_seo.py`
- [ ] `robots.txt` 존재 + 크롤러 등록 확인
- [ ] `sitemap.xml` 존재 + `<lastmod>` 최신 여부
- [ ] JSON-LD 구조화 데이터 유효성

**검증 방법**:
```bash
# SEO_GUIDELINE.md 에 명시된 HTML 경로로 실행
python3 scripts/check_seo.py <html-file>
```

---

## 출력 형식

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 출시 준비 점검

1. 버전·빌드번호
   ✅ 빌드번호: <n> (정본 파일 일치)
   ✅ CHANGELOG.md: <version> 항목 존재
   ⚠️ package.json version: <old> — 업데이트 필요?

2. 보안
   ✅ .secret/ → .gitignore 보호됨
   ✅ .env 파일 커밋 없음
   💡 security-guidance 플러그인 활성화 권장

3. 법적 문서
   ⚠️ 개인정보처리방침 미발견 — PRIVACY.md 생성 권장
   ⚠️ 이용약관 미발견 — TERMS.md 생성 권장

4. 국제화 (i18n)
   ❓ 다국어 지원 필요? (Y/N)

5. 테스트
   ✅ PASS: <n>건 / ⚠️ FAIL: <n>건

6. 접근성 (Accessibility)
   ✅ identifier 스키마: 위반 0건
   ⚠️ 인터랙티브 미부여: <n>건 (warning)
   — 또는 —
   ⏭️ RULES_ACCESSIBILITY.md 미존재 — 건너뜀

7. SEO
   ✅ 메타 태그 14항목 통과
   ✅ robots.txt 존재 (크롤러 15종)
   ⚠️ sitemap.xml lastmod 이 30일 이전 — 갱신 권장
   — 또는 —
   ⏭️ SEO_GUIDELINE.md 미존재 — 건너뜀

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 참조

- 프로젝트 라이프사이클: `docs/rules/RULES_PROJECT_LIFECYCLE.md`
- 버전·빌드번호: `docs/rules/RULES_VERSIONING.md`
- 접근성 규칙: `docs/rules/RULES_ACCESSIBILITY.md`
- 접근성 검증 스크립트: `scripts/check_accessibility_identifiers.py`
- SEO 가이드라인: `SEO_GUIDELINE.md`
- SEO 검증 스크립트: `scripts/check_seo.py`
