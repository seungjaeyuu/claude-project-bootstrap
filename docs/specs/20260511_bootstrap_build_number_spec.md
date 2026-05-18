# claude-project-bootstrap 반영 — 빌드번호 자동 증가 규격

> AIDEA iOS 프로젝트에서 발생한 빌드번호 불일치 사고(Info.plist/project.pbxproj/project.yml 3곳 제각각)를 계기로 정리.
> bootstrap 에 반영할 변경 사항을 플랫폼별로 기술.

---

## 1. 핵심 원칙

### 단일 원천 (Single Source of Truth)

빌드번호는 **한 곳에만** 정수로 존재하고, 나머지 참조처는 변수 치환 또는 자동 생성으로 파생한다.
pre-commit hook 이 main 브랜치 커밋 시 **정수 +1** 을 수행하고 자동 staging.

| 플랫폼 | 정본 (hook 이 수정하는 유일한 곳) | 파생처 (직접 수정 금지) |
|---|---|---|
| **iOS (XcodeGen)** | `iOS/project.yml` → `CURRENT_PROJECT_VERSION` | `Info.plist` ← `$(CURRENT_PROJECT_VERSION)` 변수 치환 (빌드 시), `project.pbxproj` ← xcodegen 생성 |
| **Android** | `android/app/build.gradle(.kts)` → `versionCode` | AndroidManifest.xml ← Gradle 빌드 시 자동 주입 |
| **Web / Node** | `package.json` → `buildNumber` 필드 | 번들러 환경변수 또는 런타임 읽기 |

---

## 2. pre-commit hook 추가 섹션

`scripts/pre-commit-framework.sh` 에 **(6) 빌드번호 자동 증가** 섹션 추가.
플랫폼 자동 감지 — 해당 파일이 존재할 때만 실행.

```bash
# ─────────────────────────────────────────────────────────────
# (6) 빌드번호 자동 증가 (main 브랜치 전용, 플랫폼 자동 감지)
# ─────────────────────────────────────────────────────────────
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
if [ "$BRANCH" = "main" ]; then

  # ── iOS (XcodeGen) ──
  # 정본: project.yml settings.CURRENT_PROJECT_VERSION
  # Info.plist 는 $(CURRENT_PROJECT_VERSION) 변수 참조 — 빌드 시 자동 치환
  IOS_PROJYML="$ROOT/iOS/project.yml"
  if [ -f "$IOS_PROJYML" ]; then
    CUR=$(grep 'CURRENT_PROJECT_VERSION:' "$IOS_PROJYML" | head -1 | sed 's/.*: *"\([0-9]*\)".*/\1/')
    if [ -n "$CUR" ] && [ "$CUR" -eq "$CUR" ] 2>/dev/null; then
      NXT=$((CUR + 1))
      sed -i '' "s/CURRENT_PROJECT_VERSION: \"$CUR\"/CURRENT_PROJECT_VERSION: \"$NXT\"/" "$IOS_PROJYML"
      git add "$IOS_PROJYML"
      echo "📦 iOS 빌드번호: $CUR → $NXT"
    fi
  fi

  # ── Android (Gradle) ──
  # 정본: build.gradle(.kts) versionCode
  GRADLE_FILE=""
  [ -f "$ROOT/android/app/build.gradle.kts" ] && GRADLE_FILE="$ROOT/android/app/build.gradle.kts"
  [ -f "$ROOT/android/app/build.gradle" ] && GRADLE_FILE="$ROOT/android/app/build.gradle"
  [ -z "$GRADLE_FILE" ] && [ -f "$ROOT/app/build.gradle.kts" ] && GRADLE_FILE="$ROOT/app/build.gradle.kts"
  [ -z "$GRADLE_FILE" ] && [ -f "$ROOT/app/build.gradle" ] && GRADLE_FILE="$ROOT/app/build.gradle"
  if [ -n "$GRADLE_FILE" ]; then
    CUR=$(grep -m1 'versionCode' "$GRADLE_FILE" | sed 's/.*versionCode[= ]*\([0-9]*\).*/\1/')
    if [ -n "$CUR" ] && [ "$CUR" -eq "$CUR" ] 2>/dev/null; then
      NXT=$((CUR + 1))
      sed -i '' "s/versionCode[= ]*$CUR/versionCode $NXT/" "$GRADLE_FILE"
      git add "$GRADLE_FILE"
      echo "📦 Android 빌드번호: $CUR → $NXT"
    fi
  fi

  # ── Web / Node ──
  # 정본: package.json "buildNumber" 필드
  PKG_JSON="$ROOT/package.json"
  if [ -f "$PKG_JSON" ] && grep -q '"buildNumber"' "$PKG_JSON"; then
    CUR=$(grep '"buildNumber"' "$PKG_JSON" | head -1 | sed 's/.*: *\([0-9]*\).*/\1/')
    if [ -n "$CUR" ] && [ "$CUR" -eq "$CUR" ] 2>/dev/null; then
      NXT=$((CUR + 1))
      sed -i '' "s/\"buildNumber\": *$CUR/\"buildNumber\": $NXT/" "$PKG_JSON"
      git add "$PKG_JSON"
      echo "📦 Web 빌드번호: $CUR → $NXT"
    fi
  fi

fi
```

---

## 3. 플랫폼별 초기 설정 가이드

### 3-A. iOS (XcodeGen)

**문제**: XcodeGen 이 `project.yml` → `Info.plist` 를 생성할 때 `CFBundleVersion` 을 하드코딩 문자열로 쓰면, pre-commit hook 이 `project.yml` 만 수정해도 `Info.plist` 는 마지막 xcodegen 실행 시점에 고정됨.

**해결**: `project.yml` 의 `info.properties` 에서 변수 참조 사용.

```yaml
# project.yml
targets:
  MyApp:
    info:
      path: Info.plist
      properties:
        CFBundleShortVersionString: $(MARKETING_VERSION)     # ← 변수 참조
        CFBundleVersion: $(CURRENT_PROJECT_VERSION)          # ← 변수 참조
    settings:
      base:
        MARKETING_VERSION: "0.1"                             # ← 출시 버전 (사람이 관리)
        CURRENT_PROJECT_VERSION: "1"                         # ← 빌드번호 (hook 이 관리)
```

xcodegen generate 후 Info.plist:
```xml
<key>CFBundleVersion</key>
<string>$(CURRENT_PROJECT_VERSION)</string>        <!-- 빌드 시 Xcode 가 치환 -->
```

**앱에서 읽기** (기존 코드 변경 없음):
```swift
Bundle.main.object(forInfoDictionaryKey: "CFBundleVersion") // → "195"
```

### 3-B. Android (Gradle)

**정본**: `android/app/build.gradle(.kts)` 의 `versionCode`.

```kotlin
// build.gradle.kts
android {
    defaultConfig {
        versionCode = 1          // ← hook 이 +1
        versionName = "0.1"      // ← 사람이 관리
    }
}
```

`AndroidManifest.xml` 에는 `versionCode` 를 직접 쓰지 않음 — Gradle 이 빌드 시 주입.

**앱에서 읽기**:
```kotlin
val buildNumber = packageManager
    .getPackageInfo(packageName, 0).longVersionCode
```

### 3-C. Web / Node

**정본**: `package.json` 의 `buildNumber` 필드 (표준 `version` 과 별도 관리).

```json
{
  "name": "my-app",
  "version": "0.1.0",
  "buildNumber": 1
}
```

`version` (semver) 은 릴리스 시 사람이 관리. `buildNumber` (정수) 는 hook 이 관리.

**앱에서 읽기**:
```typescript
// build-time: 번들러가 환경변수로 주입
// vite.config.ts
import pkg from './package.json';
define: { __BUILD_NUMBER__: pkg.buildNumber }

// runtime
console.log(__BUILD_NUMBER__);
```

또는 API 응답 헤더, 빌드 info 엔드포인트 등에서 표시.

---

## 4. CLAUDE.md 템플릿 변경

### CLAUDE.md.tmpl §2 횡단 가드레일에 추가:

```markdown
### 📐 버전 · 빌드번호
- **빌드번호**: main 브랜치 커밋마다 정수 +1 자동 증가 (`pre-commit-framework.sh` §6)
- **단일 원천**: 정본 파일 하나만 수정. 파생 파일(Info.plist 등)은 변수 참조 또는 빌드 시 자동 생성 — 직접 수정 금지
- hook 미설치 환경에서는 커밋 전 수동 +1 후 staging
```

### CLAUDE.md.tmpl §3 발견 트리거에 추가:

```markdown
| 빌드번호·버전 관련 작업 | `docs/rules/RULES_BUILD_NUMBER.md` |
```

---

## 5. RULES_BUILD_NUMBER.md.tmpl (신규)

```markdown
# RULES_BUILD_NUMBER — 빌드번호 관리 규칙

## 원칙
빌드번호는 **한 곳에만 정수**로 존재. 파생처는 변수 치환 / 빌드 자동 생성.

## 정본 위치 (플랫폼별)
| 플랫폼 | 정본 파일 | 정본 필드 |
|---|---|---|
| iOS (XcodeGen) | `iOS/project.yml` | `settings.CURRENT_PROJECT_VERSION` |
| Android | `android/app/build.gradle(.kts)` | `versionCode` |
| Web / Node | `package.json` | `buildNumber` |

## 🚫 금지
- Info.plist 의 `CFBundleVersion` 에 하드코딩 숫자 기입 (반드시 `$(CURRENT_PROJECT_VERSION)`)
- 정본 이외의 파일에서 빌드번호 직접 수정
- main 커밋 시 빌드번호 미증가 (hook 미설치 환경이라도 수동 +1 필수)

## 자동 강제
- `scripts/pre-commit-framework.sh` §(6): main 브랜치 감지 → 정본 +1 → staging
- 플랫폼 자동 감지 — 해당 파일 존재 시에만 실행

## 검증
커밋 후 확인 명령:
- iOS: `grep 'CURRENT_PROJECT_VERSION:' iOS/project.yml`
- Android: `grep 'versionCode' android/app/build.gradle*`
- Web: `grep '"buildNumber"' package.json`
```

---

## 6. 변경 요약 (bootstrap 반영 체크리스트)

| 대상 파일 | 변경 |
|---|---|
| `scripts/pre-commit-framework.sh` | §(6) 빌드번호 자동 증가 섹션 추가 (iOS/Android/Web 자동 감지) |
| `templates/CLAUDE.md.tmpl` | §2 에 버전·빌드번호 가드레일, §3 에 트리거 행 추가 |
| `templates/rules/RULES_BUILD_NUMBER.md.tmpl` | 신규 생성 |
| `docs/design-principles.md` (해당 시) | 단일 원천 원칙 언급 |
