# macOS 1급 지원 + 명령 체계 정리 — 설계 (v0.4.0)

- 날짜: 2026-05-31
- 상태: 합의 완료 (구현 대기)
- 대상 버전: **0.4.0** (플러그인 이름 `claude-project-bootstrap` 유지)

## 배경 / 목표

`claude-project-bootstrap`은 iOS/Android/Web/Flutter/Backend를 1급으로 다루지만 **macOS 네이티브 데스크톱 앱(Swift, SwiftUI/AppKit)은 1급이 아니다**. 빌드 명령은 `iphonesimulator` SDK 고정, E2E baseline에 macos 플랫폼 없음, codesign/notarization 등 배포 요소 전무. 동시에 `/init`이 **Claude Code 빌트인 `/init`과 충돌**하고 `init` + `init-project` 두 명령이 중복(DEV-001)이다.

이 릴리스는 (1) macOS 네이티브를 1급으로 끌어올리고, (2) 명령 체계를 정리한다.

## 핵심 결정 (합의)

| 항목 | 결정 |
|---|---|
| 범위 | **표준** (개발~배포 전체 체인, "풀"의 E2E AX 상세 가이드는 후속) |
| 배포 | **Developer ID 직배포 1급** + Mac App Store 보조 섹션(향후) |
| 분류 | **데스크톱 신규 1급** — 프로젝트 유형 (b) 일반화 + Q1a에 macOS 추가 |
| 명령 | `init` + `init-project` → **단일 명령 `/kickoff`로 통합**, `init-project` deprecated 후 제거 |
| 플러그인 이름 | **변경 없음** (`claude-project-bootstrap` 유지 → 마이그레이션·카탈로그 리스크 회피) |
| 버전 | 0.3.6 → **0.4.0** (minor; 0.x 단계라 명령 rename 허용) |

## 변경 파일 매트릭스

### macOS 지원
| 파일 | 변경 |
|---|---|
| `templates/commands/build.md.tmpl` | macOS 예시 추가: `xcodebuild -scheme <S> -destination 'platform=macOS' build` |
| `templates/commands/check.md.tmpl` | macOS 예시: `swiftlint lint && xcodebuild test ... -destination 'platform=macOS'` |
| `templates/baseline.yml.tmpl` | 주석 예시에 macOS(`runner_field: bundle_id`, `platform: macos`) |
| `templates/rules/RULES_ACCESSIBILITY.md.tmpl` | 표(L18-23)에 macOS 행: SwiftUI `.accessibilityIdentifier` / AppKit `setAccessibilityIdentifier(_:)` |
| **`templates/rules/RULES_MACOS_RELEASE.md.tmpl`** (신규) | 서명·공증·패키징 규칙 (아래) |
| `templates/CLAUDE.md.tmpl` | Discovery 트리거 표에 `RULES_MACOS_RELEASE`(서명·배포 작업 시 read) |

### 명령 정리 (DEV-001 + DEV-002 해소)
| 파일 | 변경 |
|---|---|
| `commands/init.md` → `commands/kickoff.md` | rename + 통합 진입점으로 단일화. 유형(b) 일반화, Q1a에 macOS 추가, baseline 매핑표 macOS 행, `mkdir apps/macos`, Q1c 조건에 macOS 포함 |
| `commands/init-project.md` | deprecated 표기(DEV-002) 후 제거. 핵심 내용은 kickoff.md로 흡수 |
| 기타 명령/문서의 `/init`·`init-project` 참조 | `/kickoff`로 일괄 갱신 (release.md, audit.md, README 등 — 구현 시 grep으로 전수 확인) |

### 메타/릴리스
| 파일 | 변경 |
|---|---|
| `.claude-plugin/plugin.json` + `marketplace.json` | version 0.4.0 |
| `CHANGELOG.md` | `[0.4.0]` 항목 (oldest-first 순서, `[Unreleased]` 위) |
| `README.md` | 지원 플랫폼에 macOS, 명령명 `/kickoff` 반영 |
| `TASK.md` + `tasks/DEV-001.md`, `tasks/DEV-002.md` | 본 작업으로 해소 → 상태 갱신 |

## 기술 결정

- **빌드/체크**: `-destination 'platform=macOS'` (arch 미지정=기본; universal은 배포 시점)
- **E2E baseline macOS 행**: `baseline=docs/test/baseline/MACOS_BASELINE.md`, `status_dir=docs/test/result/macos`, `ui_file_patterns='apps/macos/.*\.swift$'`, `runner_field=bundle_id`, `platform=macos` (시뮬레이터/UDID 없음 → bundle_id로 앱 식별)
- **Accessibility**: macOS SwiftUI는 iOS와 동일 API라 `check_accessibility_identifiers.py` 거의 그대로 적용. AppKit(`setAccessibilityIdentifier`)은 표에 명기하되 자동검증은 후속(SwiftUI 우선) — 구현 시 스크립트가 .swift를 플랫폼 무관하게 파싱하는지 확인

## `RULES_MACOS_RELEASE.md.tmpl` 구조 (네거티브 우선 4층 🚫/📐/📎/💡)

- **🚫 절대**: 공증 없는 배포 금지 · hardened runtime 필수 · ad-hoc 서명 배포 금지
- **📐 직배포(1급)**: Developer ID Application 서명 → `notarytool submit --wait` → `stapler staple` → `.dmg`/`.pkg`
- **📐 Mac App Store(보조·향후)**: App Sandbox entitlements · App Store Connect · provisioning profile
- **📎 참조 / 💡 팁**

## 비포함 (YAGNI / 후속)

- macOS 전용 **E2E AX 드라이버 상세 가이드**(RULES_E2E 네이티브 섹션) — "풀" 범위, 후속 릴리스
- Windows/Linux 데스크톱 — 카테고리 확장 여지만 마련, 미구현
- AppKit accessibility 자동검증 스크립트 · Sparkle 자동업데이트 — 후속
- 플러그인 이름 변경 — 명시적으로 하지 않음

## 릴리스

보호자 표준 4단계: commit + push + tag `v0.4.0` + GitHub Release. CHANGELOG `[0.4.0]` 작성. `/kickoff` rename은 CHANGELOG에 **Breaking** 으로 명기.
