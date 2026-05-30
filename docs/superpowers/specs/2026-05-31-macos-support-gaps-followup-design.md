# macOS 지원 갭 후속 — 설계 (v0.4.1)

- 날짜: 2026-05-31
- 상태: 합의 완료 (구현 대기)
- 대상 버전: **0.4.1** (patch — v0.4.0 macOS 1급 지원의 미완 구멍 보강)
- 선행 설계: [`2026-05-31-macos-support-and-command-cleanup-design.md`](2026-05-31-macos-support-and-command-cleanup-design.md)

## 배경 / 목표

v0.4.0이 macOS 네이티브를 1급으로 올리고 `RULES_MACOS_RELEASE.md.tmpl`(서명·공증·배포)을 신설했으나, `/kickoff` 흐름에 **macOS를 일관 트리거하지 못하는 구멍**이 남았다. 검증 결과 갭 4건 확인:

| # | 갭 | 근거 | 출처 |
|---|---|---|---|
| 1 | Minimal tier(Q1~Q4 모두 N) macOS 앱이 `RULES_MACOS_RELEASE`를 못 받음 | `kickoff.md` Step 2a는 **Full tier 전용**. macOS 배포(서명·공증)는 tier와 무관하게 필요 | 사용자 보고 |
| 2 | macOS 타겟 탐지가 Claude 추론에 의존 | 명시적 플랫폼 질의는 Q1a(E2E 하위)뿐. "Swift/SwiftUI"는 iOS·macOS 공통 스택이라 자유 답변만으로는 모호 | 사용자 보고 |
| 3 | `templates/claudeignore.tmpl`에 **macOS 섹션 없음** | iOS/Android/Web/Flutter만 존재. 그런데 `kickoff.md` Step 3은 "macOS 섹션 주석 해제"를 지시 → 존재하지 않는 섹션을 가리킴 | 검증 발견 |
| 4 | `.gitignore` 기본 시크릿/서명 키 커버리지 부족 | `*.p12`만 존재. `RULES_MACOS_RELEASE` §🚫4가 명시한 `.p8`/`.mobileprovision`/`*.provisionprofile` 미포함 → "키 커밋 금지" 가드레일에 실효성 부족 | 검증 발견 + 사용자 보안 강화 지시 |

이 릴리스는 4건을 한 번에 닫아 macOS 지원을 완결한다.

## 핵심 결정 (합의)

| 항목 | 결정 |
|---|---|
| 방향 | **A(명시적 플랫폼 질의) + 자동 복사** — macOS면 tier 무관하게 `RULES_MACOS_RELEASE` 복사 |
| 플랫폼 질의 범위 | 유형 **(b) 단일 네이티브 + (c) 모노레포** 모두 (둘 다 `apps/<platform>` 생성 → 결정론적 식별 필요) |
| Minimal 처리 | macOS면 규칙 복사 + Minimal CLAUDE.md에 **발견 포인터 1줄 주입** (전체 트리거 표는 미도입) |
| 범위 | 갭 1·2·3·4 전부 |
| 버전 | 0.4.0 → **0.4.1** (patch, breaking 없음 — 신규 `/kickoff` 실행에만 영향) |

### 설계 근거: `RULES_MACOS_RELEASE`는 가드레일급

Minimal tier도 🚫 가드레일(Git 안전·시크릿 키)은 이미 인라인으로 싣는다. 빠지는 건 품질·도구류 RULES(E2E·접근성·리팩토링)뿐이다. `RULES_MACOS_RELEASE`는 🚫 지배적(공증 없는 배포 금지·hardened runtime 필수·ad-hoc 서명 금지·서명키 커밋 금지 = 전부 롤백 불가 피해)이므로 **"가드레일은 항상 / 도구는 tier-gated"** 원칙상 macOS면 tier 무관 제공이 옳다. 철학의 구멍이 아니라 올바른 적용이다.

## 변경 파일 매트릭스

### `commands/kickoff.md`
| 위치 | 변경 |
|---|---|
| 대화형 질의 (프로젝트 유형 직후) | **신규 후속 질의** — 유형 (b)/(c) 선택 시 "어떤 플랫폼?" 복수 선택. (b): iOS/macOS/Android/Flutter. (c): + Web/백엔드. (a)→Web 고정, (d)→Backend 고정, (e)→자유 답변(질의 생략) |
| Q1a (E2E 앱 타입) | (b)/(c)에서 답한 플랫폼 목록을 **기본값으로 재사용** — E2E 대상만 좁힘(재질문 생략). 중복 제거 |
| Q1c (접근성 조건) | "iOS·Android·macOS 선택 시 표시" 조건을 **통합 플랫폼 답변** 기준으로 정리(Q1a 단독 참조 → 플랫폼 답변 참조) |
| 질의 수 (현 L147) | 신규 플랫폼 질의(+1, 유형 b/c 조건부)를 반영해 갱신. 정확한 min/max는 구현 시 실제 질의 구조로 재계산 |
| Step 2a | macOS 복사 줄 **제거**(Step 2b로 이동). 조건 문구를 "플랫폼 답변" 기준으로 정리 |
| **Step 2b (신규)** | macOS ∈ 플랫폼 답변 시 **tier 무관** 실행: `mkdir -p docs/rules` + `cp RULES_MACOS_RELEASE`. Full=트리거 표 행 이미 존재(무변경). Minimal=CLAUDE.md `## 📎 참조`에 포인터 1줄 주입 |
| Step 3 | `apps/<platform>`·`.claudeignore` macOS 섹션이 플랫폼 답변으로 결정론적 |
| 원칙 (현 L477) | "Minimal tier 는 RULES 0개 복사" → "(단, macOS 플랫폼은 `RULES_MACOS_RELEASE` 1개를 가드레일급으로 복사 — §Step 2b)" |
| 원칙 (현 L482) | "apps/ 폴더는 프로젝트 유형에 따라" → "유형 + 플랫폼 답변에 따라" |

Minimal 주입 포인터 (정확한 문구):
```
- 🚫 macOS 서명·공증·배포(codesign/notarytool/dmg) 작업 시: `docs/rules/RULES_MACOS_RELEASE.md` 먼저 read (배포 가드레일).
```

### `templates/claudeignore.tmpl` (갭 3)
iOS 섹션 뒤에 macOS 섹션 추가:
```
# ── macOS (SwiftUI / AppKit) ──────────────────────
# DerivedData/
# *.xcuserstate
# *.app
# *.dmg
# *.pkg
```

### `templates/gitignore.tmpl` (갭 4) — ✅ 완료
Secrets 섹션에 8개 패턴 추가: `*.p8`, `*.pfx`, `*.keystore`, `*.jks`, `*.mobileprovision`, `*.provisionprofile`, `serviceAccountKey.json`, `*-service-account.json`. (인라인 주석 금지 — `.gitignore`는 줄 끝 `#`을 패턴으로 해석.) 제외: `*.cer`/`*.crt`/`*.der`/`*.pub`(공개 파트, 오탐 위험), SSH 개인키(앱 리포 밖 상주).

### `templates/rules/RULES_MACOS_RELEASE.md.tmpl` (갭 4 정합성)
§🚫4 열거 목록에 `.p8`(App Store Connect API/APNs 키) 추가 → 규칙 문서 ↔ `.gitignore` 동기화.

### `templates/CLAUDE.minimal.md.tmpl`
**파일 무변경**. Minimal 발견 포인터는 `kickoff.md` Step 2b가 생성 시 조건부 주입(macOS Minimal 프로젝트에만). 비-macOS Minimal에는 영향 없음.

### 메타/릴리스
| 파일 | 변경 |
|---|---|
| `.claude-plugin/plugin.json` + `marketplace.json` | version 0.4.1 |
| `CHANGELOG.md` | `[0.4.1]` 항목 (Fixed: macOS 갭 4건 / Security: .gitignore 키 파일 보강) |
| `TASK.md` + `tasks/DEV-003.md` | DEV-003 등록 → 완료(v0.4.1) |
| `README.md` / `README.en.md` | 구현 시 grep — macOS tier 서술·플랫폼 질의 반영 필요 여부 확인 |

## 비포함 (YAGNI / 후속)
- 전체 §Discovery 트리거 표를 Minimal에 도입(포인터 1줄로 충분)
- SSH 개인키·`*.cer`/`*.crt` 등 공개 파트 .gitignore 추가
- AppKit accessibility 자동검증 (v0.4.0 비포함 유지)
- 플랫폼 질의를 유형 (a)/(d)/(e)로 확장 (이들은 플랫폼이 자명)

## 릴리스
보호자 표준 4단계: commit + push + tag `v0.4.1` + GitHub Release. CHANGELOG `[0.4.1]` 작성. breaking 없음(신규 `/kickoff` 실행 출력만 변경).
