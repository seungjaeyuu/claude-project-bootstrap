# macOS Support + /kickoff Command Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** macOS 네이티브(Swift, SwiftUI/AppKit) 앱을 `claude-project-bootstrap` 플러그인의 1급 대상으로 추가하고, `/init`+`/init-project` 두 명령을 빌트인과 충돌하지 않는 단일 `/kickoff` 명령으로 통합한다 (v0.4.0).

**Architecture:** 플러그인은 Markdown 템플릿/명령 + JSON 매니페스트 + Python 스크립트로 구성된다. "테스트"는 grep(텍스트 존재/부재), `python3 -c json.load`(JSON 유효성·버전), 파일 존재/부재 검증으로 수행한다. 플러그인 이름은 변경하지 않는다.

**Tech Stack:** Claude Code plugin manifest, Markdown command/template files, Python 3, git, gh CLI.

**Spec:** `docs/superpowers/specs/2026-05-31-macos-support-and-command-cleanup-design.md`

---

## File Structure

**Create:**
- `templates/rules/RULES_MACOS_RELEASE.md.tmpl` — macOS 서명·공증·배포 규칙
- `commands/kickoff.md` — 통합 단일 진입점 (init.md에서 rename)

**Modify:**
- `templates/commands/build.md.tmpl`, `templates/commands/check.md.tmpl` — macOS 빌드/체크 예시
- `templates/baseline.yml.tmpl` — macOS 베이스라인 예시
- `templates/rules/RULES_ACCESSIBILITY.md.tmpl` — macOS 행
- `templates/CLAUDE.md.tmpl` — Discovery 트리거에 RULES_MACOS_RELEASE
- `commands/*.md`, `README.md` — `/init`·`init-project` 참조 → `/kickoff`
- `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` — 0.4.0
- `CHANGELOG.md`, `README.md`, `TASK.md`, `tasks/DEV-001.md`, `tasks/DEV-002.md`

**Delete:**
- `commands/init-project.md` (내용은 kickoff.md로 흡수)

---

## Task 1: macOS 표면 템플릿 (build/check/baseline/accessibility)

**Files:**
- Modify: `templates/commands/build.md.tmpl`, `templates/commands/check.md.tmpl`, `templates/baseline.yml.tmpl`, `templates/rules/RULES_ACCESSIBILITY.md.tmpl`

- [ ] **Step 1: build.md.tmpl에 macOS 예시 추가** — `- **Flutter**: ...` 줄 다음에 삽입:
```
- **macOS (SwiftUI/AppKit)**: `xcodebuild -scheme <scheme> -destination 'platform=macOS' build`
```

- [ ] **Step 2: check.md.tmpl에 macOS 예시 추가** — `- **Flutter**: ...` 줄 다음에 삽입:
```
- **macOS (SwiftUI/AppKit)**: `swiftlint lint && xcodebuild test -scheme <scheme> -destination 'platform=macOS'`
```

- [ ] **Step 3: baseline.yml.tmpl 주석 예시 보강** — 타입별 주석 블록(`#   Web 단일 ...` 다음)에 추가:
```
#   macOS 단일     → apps.macos 만 활성
```
그리고 하단 예시 주석을 `runner_field: <runner_field>   # 예: udid / device_id / browser / bundle_id` 와 `platform: <platform>           # 예: ios_simulator / android_emulator / web / macos` 로 갱신.

- [ ] **Step 4: RULES_ACCESSIBILITY.md.tmpl 표에 macOS 행 추가** — `| Flutter | ... |` 줄 다음:
```
| macOS SwiftUI / AppKit | `.accessibilityIdentifier("...")` (SwiftUI) · `setAccessibilityIdentifier(_:)` (AppKit) |
```

- [ ] **Step 5: 검증**
Run: `grep -l "platform=macOS" templates/commands/build.md.tmpl templates/commands/check.md.tmpl && grep "macos" templates/baseline.yml.tmpl && grep "macOS SwiftUI" templates/rules/RULES_ACCESSIBILITY.md.tmpl`
Expected: 4개 파일 모두 매치 출력

- [ ] **Step 6: Commit**
```bash
git add templates/commands/build.md.tmpl templates/commands/check.md.tmpl templates/baseline.yml.tmpl templates/rules/RULES_ACCESSIBILITY.md.tmpl
git commit -m "feat(macos): add macOS examples to build/check/baseline/accessibility templates"
```

---

## Task 2: RULES_MACOS_RELEASE 신규 + Discovery 등록

**Files:**
- Create: `templates/rules/RULES_MACOS_RELEASE.md.tmpl`
- Modify: `templates/CLAUDE.md.tmpl`

- [ ] **Step 1: RULES_MACOS_RELEASE.md.tmpl 작성** — 네거티브 우선 4층(🚫/📐/📎/💡). 내용:
  - 헤더: 발견 트리거(`CLAUDE.md` §Discovery에서 *서명·배포·notarization 작업* 시 read), 상위 정책 링크
  - **🚫 절대**: (1) 공증(notarization) 없는 외부 배포 금지 (2) hardened runtime(`--options runtime`) 필수 (3) ad-hoc/미서명 배포 금지 (4) 비밀키·인증서 커밋 금지
  - **📐 직배포(1급)** 순서: `codesign --deep --force --options runtime --sign "Developer ID Application: ..."` → `xcrun notarytool submit <zip/dmg> --keychain-profile <p> --wait` → `xcrun stapler staple <app/dmg>` → `.dmg`/`.pkg` 패키징
  - **📐 Mac App Store(보조·향후)**: App Sandbox entitlements, App Store Connect 업로드, provisioning profile, MAS 전용 서명
  - **📎 참조**: Apple notarization 문서, build/check 명령
  - **💡 팁**: `notarytool ... --wait` 사용, `spctl -a -vvv <app>` 으로 Gatekeeper 검증

- [ ] **Step 2: CLAUDE.md.tmpl Discovery 트리거에 행 추가** — 먼저 형식 확인:
Run: `grep -n "RULES_GEO\|RULES_ACCESSIBILITY\|Discovery\|트리거" templates/CLAUDE.md.tmpl`
그 결과의 트리거 표 형식을 그대로 따라, "서명·공증·배포(codesign/notarytool/dmg) 작업 편집 시 → `RULES_MACOS_RELEASE.md`" 행을 추가.

- [ ] **Step 3: 검증**
Run: `test -f templates/rules/RULES_MACOS_RELEASE.md.tmpl && grep -c "🚫\|📐" templates/rules/RULES_MACOS_RELEASE.md.tmpl && grep "RULES_MACOS_RELEASE" templates/CLAUDE.md.tmpl`
Expected: 파일 존재, 4층 마커 다수, CLAUDE.md.tmpl에 참조 1건

- [ ] **Step 4: Commit**
```bash
git add templates/rules/RULES_MACOS_RELEASE.md.tmpl templates/CLAUDE.md.tmpl
git commit -m "feat(macos): add RULES_MACOS_RELEASE (codesign/notarization/dmg) + Discovery trigger"
```

---

## Task 3: /kickoff 통합 (init.md → kickoff.md, init-project 흡수+제거)

**Files:**
- Rename: `commands/init.md` → `commands/kickoff.md`
- Delete: `commands/init-project.md`

- [ ] **Step 1: init-project.md에서 kickoff에 없는 고유 내용 확인**
Run: `diff <(sed -n '1,60p' commands/init.md) <(sed -n '1,60p' commands/init-project.md)` (참고용; 두 파일의 중복/고유 부분 파악)

- [ ] **Step 2: git mv 로 rename**
```bash
git mv commands/init.md commands/kickoff.md
```

- [ ] **Step 3: kickoff.md frontmatter·제목 갱신** — `description`을 "프로젝트 초기화 + 설정 변경 (네거티브 우선 + 컨텍스트 최적화 스캐폴드)"로, 본문 `# /init — ...` 제목을 `# /kickoff — 프로젝트 초기화 + 설정 변경` 으로 변경.

- [ ] **Step 4: kickoff.md에 macOS 반영** (스펙 B 매트릭스):
  - 프로젝트 유형 (b): `(b) 단일 모바일 (SwiftUI / Flutter / Kotlin Compose)` → `(b) 단일 네이티브 앱 (모바일·데스크톱: SwiftUI / AppKit / Flutter / Kotlin Compose)`
  - Q1a 앱타입에 `6. macOS (SwiftUI/AppKit)` 추가
  - baseline 매핑표(L279-285 영역)에 행 추가: `| macOS | docs/test/baseline/MACOS_BASELINE.md | docs/test/result/macos |` (그리고 상세 필드: ui_file_patterns `'apps/macos/.*\.swift$'`, runner_field `bundle_id`, platform `macos`)
  - 디렉토리 생성 블록에 `mkdir -p apps/macos` 추가 (주석 `# (b) 단일 네이티브 macOS`)
  - Q1c 표시 조건: `iOS 또는 Android 선택 시만` → `iOS·Android·macOS 선택 시만`
  - .claudeignore 안내 문자열에 macOS 추가

- [ ] **Step 5: init-project.md 고유 내용 흡수 후 삭제** — Step 1에서 확인한 init-project 고유 설명이 있으면 kickoff.md에 병합. 그 후:
```bash
git rm commands/init-project.md
```

- [ ] **Step 6: 검증**
Run: `test -f commands/kickoff.md && ! test -f commands/init-project.md && ! test -f commands/init.md && grep -c "macOS" commands/kickoff.md`
Expected: kickoff.md 존재, init.md·init-project.md 부재, macOS 매치 다수

- [ ] **Step 7: Commit**
```bash
git add -A commands/
git commit -m "feat(macos)!: merge init + init-project into single /kickoff command, add macOS

BREAKING CHANGE: /init and /init-project replaced by /kickoff (avoids builtin /init collision; resolves DEV-001/DEV-002)"
```

---

## Task 4: /init·init-project 참조 일괄 갱신

**Files:**
- Modify: `commands/*.md` (kickoff.md 외), `templates/**/*.tmpl`, `README.md`

- [ ] **Step 1: 잔존 참조 전수 조사**
Run: `grep -rn -- '/init\b\|init-project\|init\.md\|init\.md\.tmpl' commands templates README.md | grep -v kickoff`
(빌트인 `/init` 언급이 아니라 이 플러그인 명령을 가리키는 참조만 대상)

- [ ] **Step 2: 각 매치를 `/kickoff` 로 갱신** — Step 1 출력의 각 위치에서 플러그인 명령을 가리키는 `/init` → `/kickoff`, `init-project` → `kickoff`, `/claude-project-bootstrap:init` → `/claude-project-bootstrap:kickoff`. (빌트인 `/init`을 의도적으로 언급하는 곳은 제외)

- [ ] **Step 3: 검증**
Run: `grep -rn -- 'init-project\|:init\b' commands templates README.md | grep -v kickoff`
Expected: 출력 없음 (잔존 0). 빌트인 `/init` 언급만 남아 있으면 OK

- [ ] **Step 4: Commit**
```bash
git add commands templates README.md
git commit -m "refactor: update all /init and init-project references to /kickoff"
```

---

## Task 5: 메타·문서·TASK 갱신 (0.4.0)

**Files:**
- Modify: `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `CHANGELOG.md`, `README.md`, `TASK.md`, `tasks/DEV-001.md`, `tasks/DEV-002.md`

- [ ] **Step 1: 버전 0.3.6 → 0.4.0** — plugin.json `"version"` 과 marketplace.json plugins[0] `"version"` 모두 `0.4.0`.

- [ ] **Step 2: CHANGELOG `[0.4.0]` 항목 추가** — oldest-first 순서이므로 `[Unreleased]` 섹션 **직전**에 삽입:
```
## [0.4.0] - 2026-05-31

### Added — macOS 네이티브 1급 지원
- 프로젝트 유형/Q1a에 macOS (SwiftUI/AppKit) · `apps/macos`
- build/check 템플릿 macOS 분기 (`-destination 'platform=macOS'`)
- E2E baseline `platform: macos` (runner_field: bundle_id)
- `RULES_MACOS_RELEASE.md.tmpl` 신규 (Developer ID 서명·notarization·dmg; MAS 보조)
- RULES_ACCESSIBILITY 표에 macOS 행

### Changed (BREAKING) — 명령 통합
- `/init` + `/init-project` → 단일 `/kickoff` (빌트인 `/init` 충돌 회피, DEV-001/002 해소)
```

- [ ] **Step 3: README 갱신** — 지원 플랫폼 목록에 macOS 추가, 명령 사용 예시 `/init`→`/kickoff`.

- [ ] **Step 4: TASK.md·DEV-001·DEV-002 상태 갱신** — DEV-001, DEV-002를 `✅ 완료 (v0.4.0)` 로 표기.

- [ ] **Step 5: 검증**
Run: `python3 -c "import json; a=json.load(open('.claude-plugin/plugin.json'))['version']; b=json.load(open('.claude-plugin/marketplace.json'))['plugins'][0]['version']; assert a==b=='0.4.0', (a,b); print('OK', a)" && grep -q "0.4.0" CHANGELOG.md && echo CHANGELOG_OK`
Expected: `OK 0.4.0` 및 `CHANGELOG_OK`

- [ ] **Step 6: Commit**
```bash
git add .claude-plugin/plugin.json .claude-plugin/marketplace.json CHANGELOG.md README.md TASK.md tasks/DEV-001.md tasks/DEV-002.md
git commit -m "chore(release): v0.4.0 — version bump, CHANGELOG, README, TASK status"
```

---

## Task 6: 릴리스 (tag v0.4.0 + GitHub Release)

**Files:** none (git/gh only)

- [ ] **Step 1: 최종 점검** — 작업 트리 클린 확인
Run: `git status --short` → Expected: 출력 없음 (모두 커밋됨)

- [ ] **Step 2: push**
Run: `git push origin main`

- [ ] **Step 3: tag + push**
```bash
git tag -a v0.4.0 -m "v0.4.0 — macOS 1급 지원 + /kickoff 명령 통합"
git push origin v0.4.0
```

- [ ] **Step 4: GitHub Release**
```bash
gh release create v0.4.0 --title "v0.4.0 — macOS 1급 지원 + /kickoff 명령 통합" --notes-file - <<'NOTES'
### Added — macOS 네이티브 1급 지원
프로젝트 유형/Q1a에 macOS, build/check macOS 분기, E2E baseline macos, RULES_MACOS_RELEASE(서명·공증·dmg), Accessibility macOS 행.

### Changed (BREAKING)
`/init` + `/init-project` → 단일 `/kickoff` (빌트인 /init 충돌 회피, DEV-001/002 해소).

**업데이트**: `/plugin marketplace update seungjaeyuu-plugins` → `/plugin update claude-project-bootstrap` → 재시작
NOTES
```

- [ ] **Step 5: 검증**
Run: `gh release view v0.4.0 --json tagName,isDraft -q '"\(.tagName) draft=\(.isDraft)"'`
Expected: `v0.4.0 draft=false`

---

## Notes for executor

- 각 태스크는 독립 커밋. Task 3·4는 같은 파일군을 건드리니 순서 준수(통합 먼저, 참조 갱신 다음).
- `apps/macos` 디렉토리 패턴·`bundle_id` runner는 스펙 기술 결정을 따른다.
- AppKit accessibility 자동검증 스크립트는 **이번 범위 아님**(후속). `check_accessibility_identifiers.py`는 건드리지 않는다.
- 모든 변경은 macOS *템플릿/명령* 차원이며, 플러그인 자체 동작 코드(Python 스크립트 로직)는 변경하지 않는다.
