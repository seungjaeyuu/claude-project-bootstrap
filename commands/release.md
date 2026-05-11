---
description: Pre-release readiness check — security, legal, version, i18n, tests — 출시 준비 점검
argument-hint: (선택 없음 — 자동 점검)
allowed-tools: Read, Bash(grep:*), Bash(find:*), Bash(cat:*), Bash(ls:*), Bash(git:*), Bash(wc:*), Bash(python3:*)
---

# /release — 출시 준비 체크

프로젝트 라이프사이클 ⑤ 출시 준비 (Pre-release) 단계의 체크리스트를 자동 점검.

## 전제 조건

1. `docs/rules/RULES_PROJECT_LIFECYCLE.md` Read — 체크리스트 확인.
2. `docs/rules/RULES_VERSIONING.md` Read — 빌드번호 규칙 확인.

---

## 점검 항목 (5개 카테고리)

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

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 참조

- 프로젝트 라이프사이클: `docs/rules/RULES_PROJECT_LIFECYCLE.md`
- 버전·빌드번호: `docs/rules/RULES_VERSIONING.md`
