# claude-project-bootstrap 플러그인 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 기존 `_PROJECT_FRAMEWORK` 을 Claude Code 플러그인 `claude-project-bootstrap` 으로 재패키징 하고 GitHub 공개 배포.

**Architecture:** 단일 GitHub 저장소가 플러그인(`.claude-plugin/plugin.json`) + 마켓플레이스(`.claude-plugin/marketplace.json`) 역할 겸함. `_PROJECT_FRAMEWORK` 의 14개 파일(+3 신규 docs)을 `commands/`, `scripts/`, `templates/`, `docs/` 4 분류로 재배치. `/init-project` 실행 시 `${CLAUDE_PLUGIN_ROOT}` 경로의 템플릿·스크립트를 target 프로젝트로 복사. 플러그인 레벨 hook 은 두지 않음 (프로젝트 고유 matcher regex 차이 때문).

**Tech Stack:** Claude Code Plugin (JSON manifest), bash scripts (install/pre-commit), Python 3 (baseline/check 도구), Git.

**선행 조건:**
- `~/Documents/GitHub/claude-project-bootstrap/` 폴더 존재 (spec 파일이 `docs/specs/` 안에 있음)
- `~/Documents/GitHub/_PROJECT_FRAMEWORK/` 는 **read-only** (archive 대상, 파일 수정 금지)
- `~/.claude/commands/init-project.md.bak` 백업 파일 존재 (원본 `/init-project` 커맨드)
- 글로벌 `~/.claude/CLAUDE.md` 에서 `_PROJECT_FRAMEWORK` 자동 제안 규칙 이미 제거됨

**참조 Spec:** `docs/specs/2026-04-23-claude-project-bootstrap-plugin-design.md`

---

## Phase 개요

| Phase | 목표 | 예상 Task 수 |
|---|---|---|
| 0 | Claude Code 플러그인 규약 확인 (spec 의 불확실 항목 5건 해소) | 3 |
| 1 | 저장소 초기화 & 디렉토리 스켈레톤 | 4 |
| 2 | 원본 파일 이관 (generic 화 전) | 4 |
| 3 | Plugin · Marketplace manifest 작성 | 2 |
| 4 | Generic 화 (사적 맥락 31건 제거 + DESIGN_DECISIONS 분할 + 신규 docs) | 6 |
| 5 | 경로 참조 치환 + README 전면 재작성 | 3 |
| 6 | 정적 검증 (grep 기반) | 1 |
| 7 | 로컬 동작 검증 (10 항목 체크리스트) | 4 |
| 8 | 공개 배포 & 기존 저장소 archive | 3 |

각 Phase 끝에서 사용자 checkpoint 가능 — `execution handoff` 에서 선택한 방식(subagent-driven / inline)에 따라 다름.

---

## Phase 0: 플러그인 규약 확인

**목적:** Spec Section 6 의 불확실 항목 5건을 해소해서 Phase 1-7 의 세부 결정이 틀리지 않도록 함. 플러그인 개발 경험이 없으므로 이 단계 건너뛰면 Phase 3 의 manifest 가 깨짐.

### Task 0.1: plugin-dev:plugin-structure skill 로 규약 확인

**Files:** (문서 읽기만 — 파일 수정 없음)

- [ ] **Step 1: Skill 호출**

```
Skill tool 호출: plugin-dev:plugin-structure
args: "claude-project-bootstrap 플러그인 개발을 위해 plugin.json 스키마, 디렉토리 규약, ${CLAUDE_PLUGIN_ROOT} 동작, 필수 필드 확인 필요"
```

- [ ] **Step 2: 발견 사항 메모**

`docs/specs/2026-04-23-claude-project-bootstrap-plugin-design.md` Section 6 에 답변을 기록. Edit 도구로 각 불확실 항목 (1~5번) 뒤에 "✅ 확인 결과:" 한 줄씩 추가:

```markdown
| **1** | `plugin.json` 의 정확한 JSON 스키마 ... | ... |
| | ✅ 확인: [여기에 실제 스키마 요약] |
```

(각 항목 확인 후 작성)

### Task 0.2: plugin-dev:command-development 로 커맨드 규약 확인

- [ ] **Step 1: Skill 호출**

```
Skill tool 호출: plugin-dev:command-development
args: "슬래시 커맨드의 frontmatter 필드, description/argument-hint 규약, ${CLAUDE_PLUGIN_ROOT} 변수가 커맨드 본문에서 어떻게 resolve 되는지 확인"
```

- [ ] **Step 2: 발견 사항 메모**

Spec Section 6 의 4번 (`${CLAUDE_PLUGIN_ROOT}` 해석 맥락), 5번 (커맨드 네임스페이스) 에 확인 결과 기록.

### Task 0.3: plugin-dev:hook-development + marketplace 형식 확인

- [ ] **Step 1: plugin-dev:hook-development skill 호출**

```
Skill tool 호출: plugin-dev:hook-development
args: "플러그인 레벨 hook 과 settings.json hook 의 실행 컨텍스트 차이, 'hooks/hooks.json' 또는 '.claude-plugin/hooks.json' 의 정확한 위치 확인. 우리는 프로젝트 레벨 hook 만 사용 예정 — 그 선택이 올바른지 재확인"
```

- [ ] **Step 2: marketplace.json 스키마 확인**

WebFetch 또는 plugin-dev skill 을 추가 호출해 `marketplace.json` 의 `plugins` 배열 스키마·필수 필드 확인.

- [ ] **Step 3: Spec Section 6 최종 업데이트**

5건 모두 ✅ 확인 결과를 spec 에 반영 후 commit 은 Phase 1 에서 함께 (지금은 아직 git init 전).

---

## Phase 1: 저장소 초기화 & 디렉토리 스켈레톤

**목적:** 빈 폴더 상태에서 git 저장소로 변환, 플러그인 표준 디렉토리 구조 생성, 최소 루트 파일 (.gitignore, LICENSE, README 초안, CHANGELOG) 작성, 초기 커밋.

### Task 1.1: git init + 기본 설정

**Files:**
- Create: `.gitignore`

- [ ] **Step 1: git init 실행**

```bash
cd ~/Documents/GitHub/claude-project-bootstrap
git init -b main
```

Expected: `Initialized empty Git repository in .../claude-project-bootstrap/.git/`

- [ ] **Step 2: .gitignore 작성**

Create `.gitignore`:

```
# macOS
.DS_Store

# Editor
.vscode/
.idea/
*.swp
*~

# Python
__pycache__/
*.pyc
.venv/

# Local development
*.log
.secret/
```

- [ ] **Step 3: 확인**

```bash
git status
```

Expected: `docs/specs/...` (untracked), `.gitignore` (untracked).

### Task 1.2: LICENSE + CHANGELOG + README 초안

**Files:**
- Create: `LICENSE`
- Create: `CHANGELOG.md`
- Create: `README.md`

- [ ] **Step 1: LICENSE (MIT)**

Create `LICENSE`:

```
MIT License

Copyright (c) 2026 Yu Seungjae

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 2: CHANGELOG.md 초안**

Create `CHANGELOG.md`:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial plugin scaffold migrated from `_PROJECT_FRAMEWORK`

## [0.1.0] - TBD
```

- [ ] **Step 3: README.md 초안 (Phase 5 에서 전면 재작성)**

Create `README.md`:

```markdown
# claude-project-bootstrap

> 🚧 **Work in Progress** — 초기 스캐폴드. 전면 재작성은 Phase 5 에서 진행.

Claude Code 플러그인: 새 프로젝트를 네거티브 우선 원칙 + 베이스라인 하네스로 부트스트랩.

## 상태

Alpha — 로컬 검증 진행 중. 공개 배포는 v0.1.0 릴리즈 이후.
```

### Task 1.3: 디렉토리 스켈레톤 생성

- [ ] **Step 1: 4개 디렉토리 + .claude-plugin 생성**

```bash
mkdir -p .claude-plugin commands scripts templates docs
```

- [ ] **Step 2: .gitkeep 배치 (빈 디렉토리 추적용 — Phase 2 에서 채워짐)**

```bash
touch commands/.gitkeep scripts/.gitkeep templates/.gitkeep
```

- [ ] **Step 3: 확인**

```bash
ls -la
```

Expected: `.claude-plugin/`, `commands/`, `docs/`, `scripts/`, `templates/` 모두 존재.

### Task 1.4: Initial commit

- [ ] **Step 1: 전체 staging**

```bash
git add .gitignore LICENSE CHANGELOG.md README.md docs/ commands/.gitkeep scripts/.gitkeep templates/.gitkeep
```

- [ ] **Step 2: 커밋**

```bash
git commit -m "initial: 플러그인 저장소 스캐폴드 + spec 이관"
```

- [ ] **Step 3: 확인**

```bash
git log --oneline
```

Expected: 1 커밋, hash + "initial: 플러그인 저장소 스캐폴드 + spec 이관".

---

## Phase 2: 원본 파일 이관 (generic 화 전)

**목적:** `_PROJECT_FRAMEWORK` 의 모든 파일을 플러그인 저장소로 **복사** (generic 화는 Phase 4 에서 별도). 복사 후 즉시 commit 해서 "이관만 한 상태" 를 이력에 남김 → 나중에 generic 화 diff 가 명확히 보임.

**환경 변수:** 명령 단순화를 위해 `$ORIGINAL=/Users/yuseungjae/Documents/GitHub/_PROJECT_FRAMEWORK` 라고 가정.

### Task 2.1: 템플릿 7개 이관

**Files:**
- Create: `templates/CLAUDE.md.tmpl`
- Create: `templates/INDEX.md.tmpl`
- Create: `templates/TESTING_FRAMEWORK.md.tmpl`
- Create: `templates/BASELINE.md.tmpl`
- Create: `templates/gitignore.tmpl`
- Create: `templates/settings.json.tmpl`
- Create: `templates/baseline.yml.tmpl`

- [ ] **Step 1: 6개 템플릿 cp**

```bash
ORIGINAL=/Users/yuseungjae/Documents/GitHub/_PROJECT_FRAMEWORK
cp "$ORIGINAL/CLAUDE_TEMPLATE.md"              templates/CLAUDE.md.tmpl
cp "$ORIGINAL/INDEX_TEMPLATE.md"               templates/INDEX.md.tmpl
cp "$ORIGINAL/TESTING_FRAMEWORK_TEMPLATE.md"   templates/TESTING_FRAMEWORK.md.tmpl
cp "$ORIGINAL/BASELINE_TEMPLATE.md"            templates/BASELINE.md.tmpl
cp "$ORIGINAL/.gitignore.template"             templates/gitignore.tmpl
cp "$ORIGINAL/hooks/settings.json.template"    templates/settings.json.tmpl
cp "$ORIGINAL/scripts/baseline.yml.template"   templates/baseline.yml.tmpl
```

- [ ] **Step 2: 이관 확인**

```bash
ls -la templates/
```

Expected: 7개 `.tmpl` 파일 + `.gitkeep`.

- [ ] **Step 3: .gitkeep 제거**

```bash
rm templates/.gitkeep
```

### Task 2.2: Scripts 5개 + bash 2개 이관

**Files:**
- Create: `scripts/baseline_status.py`
- Create: `scripts/baseline_update_suggest.py`
- Create: `scripts/check_baseline_sync.py`
- Create: `scripts/check_accessibility_identifiers.py`
- Create: `scripts/check_dict_duplicates.py`
- Create: `scripts/install-hooks.sh`
- Create: `scripts/pre-commit-framework.sh`

- [ ] **Step 1: Python scripts 5개 cp**

```bash
cp "$ORIGINAL/scripts/baseline_status.py"                scripts/
cp "$ORIGINAL/scripts/baseline_update_suggest.py"        scripts/
cp "$ORIGINAL/scripts/check_baseline_sync.py"            scripts/
cp "$ORIGINAL/scripts/check_accessibility_identifiers.py" scripts/
cp "$ORIGINAL/scripts/check_dict_duplicates.py"          scripts/
```

- [ ] **Step 2: Bash hook 스크립트 2개 cp**

```bash
cp "$ORIGINAL/hooks/install-hooks.sh"          scripts/
cp "$ORIGINAL/hooks/pre-commit-framework.sh"   scripts/
```

- [ ] **Step 3: 실행 권한 확인·부여**

```bash
chmod +x scripts/*.py scripts/*.sh
ls -la scripts/
```

Expected: 7개 파일 모두 `-rwxr-xr-x`.

- [ ] **Step 4: .gitkeep 제거**

```bash
rm scripts/.gitkeep
```

### Task 2.3: Commands 2개 이관

**Files:**
- Create: `commands/init-project.md` (⚠ 원본이 글로벌 백업)
- Create: `commands/baseline-review.md`

- [ ] **Step 1: init-project 는 글로벌 백업에서 이관**

```bash
cp ~/.claude/commands/init-project.md.bak commands/init-project.md
```

- [ ] **Step 2: baseline-review 는 `_PROJECT_FRAMEWORK/commands/` 에서**

```bash
cp "$ORIGINAL/commands/baseline-review.md" commands/baseline-review.md
```

- [ ] **Step 3: 확인**

```bash
ls -la commands/
wc -l commands/*.md
```

Expected: `init-project.md` (~156줄), `baseline-review.md` (~51줄), `.gitkeep`.

- [ ] **Step 4: .gitkeep 제거**

```bash
rm commands/.gitkeep
```

### Task 2.4: DESIGN_DECISIONS.md 이관 + commit

**Files:**
- Create: `docs/DESIGN_DECISIONS.md` (임시 — Phase 4 에서 분할 후 삭제)

- [ ] **Step 1: 임시 복사**

```bash
cp "$ORIGINAL/docs/DESIGN_DECISIONS.md" docs/DESIGN_DECISIONS.md
```

- [ ] **Step 2: 전체 이관 상태 확인**

```bash
find . -type f -not -path '*/\.git/*' -not -path '*/docs/specs/*' -not -path '*/docs/plans/*' | sort
```

Expected 파일 목록 (총 20개):

```
./.gitignore
./CHANGELOG.md
./LICENSE
./README.md
./commands/baseline-review.md
./commands/init-project.md
./docs/DESIGN_DECISIONS.md
./scripts/baseline_status.py
./scripts/baseline_update_suggest.py
./scripts/check_accessibility_identifiers.py
./scripts/check_baseline_sync.py
./scripts/check_dict_duplicates.py
./scripts/install-hooks.sh
./scripts/pre-commit-framework.sh
./templates/BASELINE.md.tmpl
./templates/CLAUDE.md.tmpl
./templates/INDEX.md.tmpl
./templates/TESTING_FRAMEWORK.md.tmpl
./templates/baseline.yml.tmpl
./templates/gitignore.tmpl
./templates/settings.json.tmpl
```

- [ ] **Step 3: Commit**

```bash
git add commands/ scripts/ templates/ docs/DESIGN_DECISIONS.md
git commit -m "chore: _PROJECT_FRAMEWORK 원본 파일 이관 (generic 화 전)"
```

---

## Phase 3: Plugin · Marketplace manifest 작성

**목적:** `.claude-plugin/plugin.json` 과 `.claude-plugin/marketplace.json` 작성. Phase 0 확인 결과 기반.

**주의:** 아래 샘플 JSON 은 2026-04-23 시점의 Phase 0 확인 **이전** 추정치. Phase 0 에서 공식 스키마와 충돌하면 이 Task 안에서 수정 반영.

### Task 3.1: plugin.json 작성

**Files:**
- Create: `.claude-plugin/plugin.json`

- [ ] **Step 1: 기본 manifest 작성 (Phase 0 결과 반영)**

Create `.claude-plugin/plugin.json` — Phase 0 에서 확인한 공식 스키마에 맞게. 아래는 추정 기준 샘플:

```json
{
  "name": "claude-project-bootstrap",
  "version": "0.1.0",
  "description": "네거티브 우선 원칙과 베이스라인 하네스로 새 프로젝트를 부트스트랩하는 Claude Code 플러그인",
  "author": {
    "name": "Yu Seungjae",
    "email": "yu.seungjae@gmail.com"
  },
  "homepage": "https://github.com/seungjaeyuu/claude-project-bootstrap",
  "license": "MIT",
  "keywords": ["scaffold", "bootstrap", "korean", "e2e-testing", "baseline"],
  "commands": [
    "commands/init-project.md",
    "commands/baseline-review.md"
  ]
}
```

**⚠ Phase 0 에서 확인한 스키마와 다르면**: 필드명·구조를 수정. 특히:
- `commands` 가 자동 발견인지 명시 필요인지
- `name` 에 `@scope/` 네임스페이스 강제되는지
- `hooks`, `skills` 필드 필요 여부 (우리는 현재 None)

- [ ] **Step 2: JSON 문법 검증**

```bash
python3 -c "import json; json.load(open('.claude-plugin/plugin.json'))"
```

Expected: 에러 없음.

### Task 3.2: marketplace.json 작성 + commit

**Files:**
- Create: `.claude-plugin/marketplace.json`

- [ ] **Step 1: marketplace manifest 작성**

Create `.claude-plugin/marketplace.json` — 추정 기준 샘플:

```json
{
  "name": "seungjaeyuu-plugins",
  "owner": {
    "name": "Yu Seungjae",
    "email": "yu.seungjae@gmail.com"
  },
  "plugins": [
    {
      "name": "claude-project-bootstrap",
      "source": "./",
      "description": "네거티브 우선 원칙과 베이스라인 하네스로 새 프로젝트를 부트스트랩",
      "version": "0.1.0",
      "category": "scaffold"
    }
  ]
}
```

**⚠ Phase 0 에서 확인한 스키마가 다르면 수정.**

- [ ] **Step 2: JSON 문법 검증**

```bash
python3 -c "import json; json.load(open('.claude-plugin/marketplace.json'))"
```

- [ ] **Step 3: Commit**

```bash
git add .claude-plugin/
git commit -m "feat: plugin.json + marketplace.json manifest 작성"
```

---

## Phase 4: Generic 화 (사적 맥락 제거 + DESIGN_DECISIONS 분할 + 신규 docs)

**목적:** Spec Section 4 의 변환 규칙 적용. 31건 사적 맥락 제거, DESIGN_DECISIONS.md 를 `design-principles.md`(🟢 6건) + `changelog-decisions.md`(🟡 5건) + D12 삭제로 분할, `migration-guide.md` 신규 작성.

### Task 4.1: scripts 파일 내 ID 예시 generic

**Files:**
- Modify: `scripts/baseline_status.py:10-11`

- [ ] **Step 1: baseline_status.py 의 --help 예시 교체**

Edit `scripts/baseline_status.py`:

```
old_string:
  baseline_status.py --id PRV-06-R14        # 특정 ID 최신 판정 + 이력
  baseline_status.py --expected PRV-06-R14  # baseline 의 기준 항목 추출

new_string:
  baseline_status.py --id APP-01-R01        # 특정 ID 최신 판정 + 이력
  baseline_status.py --expected APP-01-R01  # baseline 의 기준 항목 추출
```

- [ ] **Step 2: check_accessibility_identifiers.py 경로 예시 교체**

Edit `scripts/check_accessibility_identifiers.py` line 21 근처:

```
old_string:
        sunnyway/apps/student_app_ios/SunnyWay

new_string:
        apps/ios/
```

- [ ] **Step 3: 검증 grep**

```bash
grep -rn "PRV-06\|sunnyway" scripts/
```

Expected: 매치 없음 (빈 출력).

### Task 4.2: templates/BASELINE.md.tmpl generic

**Files:**
- Modify: `templates/BASELINE.md.tmpl:48`

- [ ] **Step 1: EXAMPLE-S01 → APP-01-R01 교체**

Edit `templates/BASELINE.md.tmpl` 에서:

```
old_string: | EXAMPLE-S01 | SA | 시뮬 | (기대 동작 한 문장) | `2026-04-10 session` | 2026-04-12 실행 완료 |

new_string: | APP-01-R01 | (역할) | (플랫폼) | (기대 동작 한 문장) | `YYYY-MM-DD session` | YYYY-MM-DD 실행 완료 |
```

- [ ] **Step 2: 검증**

```bash
grep -n "EXAMPLE-S01\|2026-04-10\|2026-04-12" templates/BASELINE.md.tmpl
```

Expected: 매치 없음.

### Task 4.3: templates/CLAUDE.md.tmpl generic (10건 SunnyWay + 보호자 예시 라벨)

**Files:**
- Modify: `templates/CLAUDE.md.tmpl` (다중 위치)

사전에 원본을 grep 으로 전체 매치 위치 확인:

```bash
grep -n "SunnyWay\|보호자\|2026-04-1[0-9]\|Lane [A-D]" templates/CLAUDE.md.tmpl
```

- [ ] **Step 1: Line 39 체크리스트 항목**

```
old_string: - [ ] `/ACCESSIBILITY_IDENTIFIERS.md` 루트 배치 (UI 앱 한정) — SunnyWay 의 동명 파일 참조
new_string: - [ ] `/ACCESSIBILITY_IDENTIFIERS.md` 루트 배치 (UI 앱 한정) — 플랫폼별 카탈로그 정의
```

- [ ] **Step 2: Line 104 Accessibility 상세 참조**

```
old_string: **상세**: 프로젝트 루트 `/ACCESSIBILITY_IDENTIFIERS.md` (플랫폼별 §13~§15 포함) — SunnyWay 원본 참조.
new_string: **상세**: 프로젝트 루트 `/ACCESSIBILITY_IDENTIFIERS.md` (플랫폼별 §13~§15 포함) — 각 프로젝트 고유 카탈로그.
```

- [ ] **Step 3: Line 141 "보호자" 예시를 교육적 예시로 격하**

Edit `templates/CLAUDE.md.tmpl` 의 해당 섹션 — 기존 "예: `\"보호자\"` 사용, `\"가족\"/\"학부모\"` 금지 (SunnyWay 사례). 프로젝트별 정의." 를 다음으로 확장:

```markdown
### 📐 프로젝트 고유 용어 정의 (예시)

모든 프로젝트는 고유한 도메인 용어를 가지며, 팀 안에서 **하나의 용어로 통일** 해야 자동화 도구와 문서가 일관성을 유지할 수 있습니다.

예시 (실제 프로덕션 프로젝트의 경우):
- "보호자" 를 사용, "가족"/"학부모" 금지 — 도메인이 학원 셔틀 서비스
- "배송 건" 을 사용, "주문"/"패키지" 금지 — 도메인이 물류

본인 프로젝트의 도메인 용어를 여기에 명시하세요.
```

- [ ] **Step 4: Line 196 TESTING_FRAMEWORK 상세 참조**

```
old_string: > **상세 프레임워크 구현체**: SunnyWay `TESTING_FRAMEWORK.md` 원본 참조. 본 템플릿은 **핵심 규칙만** 나열.
new_string: > **상세 프레임워크**: 프로젝트 루트 `TESTING_FRAMEWORK.md` (이 플러그인의 템플릿 기반). 본 섹션은 **핵심 규칙만** 요약.
```

- [ ] **Step 5: Line 209 Cross-Lane 섹션 제목**

```
old_string: ### 8.2 🚫 Cross-Lane Destructive Op (P0 — 2026-04-14 Lane B 사고)
new_string: ### 8.2 🚫 Cross-Lane Destructive Op (P0)
```

- [ ] **Step 6: Line 224 사고 배경**

```
old_string: **사고 배경**: 2026-04-14 Lane B Codex 가 자기 "운영 권고" 를 자율 집행하여 Lane A/C/D 시뮬 + 워커 외부 살해, 303건 중 262건 손실.
new_string: **사고 배경**: 병렬 AI 테스트에서 워커가 자신의 리포트 내 "운영 권고" 를 자율 집행하면 다른 Lane 을 cross-kill 할 수 있음. 실제 프로덕션 사고 사례 존재.
```

- [ ] **Step 7: Line 263 BLOCKED 패턴 참조**

```
old_string: BLOCKED 원인과 해결법을 프레임워크 라이브러리에 누적. 상세: SunnyWay `TESTING_FRAMEWORK.md §13`.
new_string: BLOCKED 원인과 해결법을 프레임워크 라이브러리에 누적. 상세: `TESTING_FRAMEWORK.md §13`.
```

- [ ] **Step 8: Line 291 변경 이력**

```
old_string: | 2026-04-21 | **네거티브 우선** 설계로 개편 — 4층 범례 (🚫/📐/📎/💡) 도입, E2E 섹션을 SunnyWay TESTING_FRAMEWORK.md 참조로 축약, API 키는 `.claude/secrets/` 로 분리. 642줄 → ~260줄. |
new_string: | YYYY-MM-DD | **네거티브 우선** 설계 적용 — 4층 범례 (🚫/📐/📎/💡) 도입, E2E 섹션 축약, API 키는 `.secret/` 로 분리. |
```

- [ ] **Step 9: 검증 grep**

```bash
grep -n "SunnyWay\|sunnyway\|Lane B\|2026-04-1[0-9]\|2026-04-2[0-9]\|PR #[0-9]" templates/CLAUDE.md.tmpl
```

Expected: **단 한 건도 매치 없음**. (보호자 예시는 "실제 프로덕션 프로젝트의 경우" 라벨이 있으므로 OK.)

### Task 4.4: templates/TESTING_FRAMEWORK.md.tmpl generic (4건)

**Files:**
- Modify: `templates/TESTING_FRAMEWORK.md.tmpl` (다중 위치)

- [ ] **Step 1: Line 5 참고 서두**

```
old_string: > 멀티 에이전트 테스트(Codex 4-Lane, Orchestrator 등) 상세 사례는 **SunnyWay 프로젝트의 TESTING_FRAMEWORK.md §1~§19** 를 참고해 프로젝트에 맞게 확장.
new_string: > 멀티 에이전트 테스트(Codex 4-Lane, Orchestrator 등) 상세 사례는 프로젝트 고유 맥락에 맞게 확장하세요. 본 템플릿은 **공통 규약만** 담습니다.
```

- [ ] **Step 2: Line 49 사례 참조**

```
old_string: 상세 사례: SunnyWay TESTING_FRAMEWORK.md §6.10.1 (2026-04-14 Lane B 사고).
new_string: 상세 사례는 프로젝트 TESTING_FRAMEWORK.md 의 사고 이력 섹션 참조.
```

- [ ] **Step 3: Line 166 "SunnyWay 실전 사례" 블록**

해당 블록 전체 (SunnyWay 실전 사례 관련) 를 삭제하거나 다음으로 대체:

```markdown
> 실전 사례가 필요하면 각 프로젝트의 TESTING_FRAMEWORK.md 에 **프로젝트 고유 사고 이력** 섹션을 추가해 문서화하세요.
```

- [ ] **Step 4: Line 29 / 2 Cross-Lane 섹션**

해당 섹션 (P0 표시) 에 SunnyWay 날짜 참조 있으면 제거.

- [ ] **Step 5: 검증**

```bash
grep -n "SunnyWay\|sunnyway" templates/TESTING_FRAMEWORK.md.tmpl
```

Expected: 매치 없음.

### Task 4.5: DESIGN_DECISIONS.md 분할 — design-principles.md 작성

**Files:**
- Create: `docs/design-principles.md`

- [ ] **Step 1: design-principles.md 작성**

Create `docs/design-principles.md` — 🟢 6건 (D1, D3, D4, D5, D7, D8) 을 generic 화한 설계 원칙 문서:

```markdown
# claude-project-bootstrap 설계 원칙

> 본 플러그인은 실전 프로젝트에서 반복 시행착오로 결정화된 패턴을 **다음 프로젝트부터 기본값으로** 적용하기 위한 도구입니다. 여기서는 주요 설계 결정의 **근거** 를 기록합니다.

---

## 1. 네거티브 우선 + 4층 규칙 범례

**원칙**: 규칙을 "금지만" 적되, 프로젝트에 **특별히 해당되는 것만** 명시. 고성능 LLM (Opus 4.7+) 이 자력 판단 가능한 일반 모범 사례는 제외.

**4층**:

| 이모지 | 층위 | 의미 |
|---|---|---|
| 🚫 | Guardrail | 절대 금지. 롤백 불가한 피해 또는 사고 재발 방지. |
| 📐 | Schema | 스키마·용어·명명 계약. 일관성 확보. |
| 📎 | 참조 | 경로·환경·도구 메타. 지침 아님. |
| 💡 | 권장 | 모범 사례. 근거 제시 시 override 가능. |

---

## 2. 3-Template 베이스라인 규약

**문제**: 한 프로젝트의 `MASTER_TEST_BASELINE.md` 에 13가지 서로 다른 헤더 변형 혼재. 의미 같은 것을 다른 이름으로 부름 → 스크립트 파싱 불가, 사람 혼란.

**해결**: 3개 표준 Template 만 허용.

| Template | 대상 |
|---|---|
| A | 이미 실행된 ID |
| B | 미실행·소스 보강 |
| C | 버그 추적용 (집계 제외) |

**반영**: `templates/BASELINE.md.tmpl` 이 3 Template 으로 구조화.

---

## 3. 판정 Canonical = status.json

**문제**: baseline markdown 에 "최신 판정/메모" 를 한 셀에서 관리하면 판정·메모·후속과제·참조가 섞여 자동화 불가.

**해결**: **canonical 은 `status.json` 만**. baseline 의 텍스트 컬럼은 historical narrative.

| 데이터 | 위치 |
|---|---|
| 판정 (PASS/FAIL/BLOCK) | `docs/<app>/testing_harness/run/*_status.json` |
| 요약 | baseline "최신 요약" (판정 없이) |
| 후속 과제 | 프로젝트의 백로그 시스템 |
| 참조 | baseline "이전 프롬프트 매핑" 링크 |

---

## 4. 이중 배치 지양 + 3계층 발견 경로

**원칙**: 같은 규칙을 여러 곳에 복붙하지 않음. 대신 **"Claude 가 언제 Read 하는가"** 를 설계.

**발견 계층 (강제력 순)**:

- **T1**: Hook (기계적 강제) — 가장 확실
- **T2**: 자동 로드 (루트 CLAUDE.md) — 매 세션 인지
- **T3**: 조건부 로드 (앱별 CLAUDE.md) — 해당 영역 작업 시
- **T4**: On-demand (TESTING_FRAMEWORK.md 등) — Claude 가 Read 해야 발견

**플러그인 구조 반영**: `commands/` (명시적 호출), `templates/` (스캐폴드 시 1회), `scripts/` (target 프로젝트 복사 후 hook 에서 호출) 로 발견 시점 분리.

---

## 5. 하네스 도입 = `baseline.yml` entry 활성화

**문제**: "E2E 하네스 도입" 시점이 모호하면 사람·자동화가 각자 다르게 판단.

**해결**: **`baseline.yml` 의 `apps.<name>` entry 가 활성화되는 순간** = 하네스 도입 순간. 단일 SSOT.

**반영**: `templates/baseline.yml.tmpl` 이 commented-out entry + 활성화 설명으로 구성.

---

## 6. 트리거 기반 베이스라인 동기화

**문제**: "매 기능 수정마다 baseline 갱신" 은 매 프롬프트마다 Claude 가 판단해야 해서 거짓양성·음성 다수.

**해결**: **트리거 시점 일괄 검토 + Git diff 자동 제안**.

**트리거**:
- E2E 테스트 세션 시작
- 릴리스/베타 준비
- 정기 점검 (주 1회 권장)

**도구**: `/baseline-review` 슬래시 커맨드 → `scripts/baseline_update_suggest.py` 호출.

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-04-23 | 초판 — 6개 설계 원칙 편입 (기존 _PROJECT_FRAMEWORK 에서 generic 화) |
```

### Task 4.6: DESIGN_DECISIONS 분할 — changelog-decisions.md + migration-guide.md + DESIGN_DECISIONS.md 삭제

**Files:**
- Create: `docs/changelog-decisions.md`
- Create: `docs/migration-guide.md`
- Delete: `docs/DESIGN_DECISIONS.md` (임시 이관본)

- [ ] **Step 1: changelog-decisions.md 작성**

Create `docs/changelog-decisions.md` — 🟡 5건 (D2, D6, D9, D10, D11) 내부 결정 로그:

```markdown
# 내부 결정 로그

> 공개 설계 원칙(`design-principles.md`) 에 포함하지 않은 보조 결정들. Claude Code 컨벤션 진화·논쟁 여지·세대별 모델 차이에 민감한 항목이라 README 에서는 링크하지 않음.

---

## CL-02: 섹션 마커 철회

**결정**: baseline markdown 의 `<!-- baseline-section: active-tests -->` 메타 주석 계획 **철회**.

**근거**:
- ID 별 판정은 `status.json` 이 canonical
- 집계 제외는 `baseline.yml` 의 `exclude_prefixes` 로 달성 (BUG-* 등)
- 마커는 유지 부담만 증가

---

## CL-06: `.claude/rules/` 철폐 + `.secret/` 프로젝트 루트

**결정**: `.claude/rules/`, `.claude/secrets/` 둘 다 사용하지 않음.

**근거**:
- `.claude/` 는 Claude Code 로컬·전역 설정 디렉토리. 공식 구성은 `settings.json`, `commands/`, `agents/`.
- `.claude/rules/` 는 공식 아닌 관습. hidden 폴더라 사람 인지 어려움.
- **대안**: 규칙 문서는 루트 (`CLAUDE.md`, `TESTING_FRAMEWORK.md`), secrets 는 루트 `.secret/` 에.

**주의**: Claude Code 컨벤션이 향후 변경되면 재검토 필요.

---

## CL-09: 위험 명령 차단 Hook 철회

**결정**: `rm -rf`, `git reset --hard` 등을 PreToolUse hook 으로 **기계 차단** 하려던 계획 **철회**. CLAUDE.md Guardrail 문서 규칙만 유지.

**근거**:
- Hook 차단은 정당한 예외 (브랜치 정리 등) 도 막음
- 유연성 손실 > 안전성 이득

**논쟁 여지**: 팀 문화에 따라 강한 차단이 더 안전하다고 판단할 수 있음. PR 로 재논의 가능.

---

## CL-10: MEMORY.md 프로젝트 단위 인식

**결정**: MEMORY.md 는 **프로젝트 단위 단일 계층**. 글로벌 없음.

**근거 (실측)**:
- `~/.claude/MEMORY.md`, `~/.claude/memory/` 둘 다 존재하지 않음
- `~/.claude/projects/<인코딩된-경로>/memory/MEMORY.md` 가 프로젝트별 유일 경로
- 전역 기억은 `~/.claude/CLAUDE.md` 에 수동 기록

**주의**: Claude Code 의 memory 구조가 향후 변경될 수 있음.

---

## CL-11: 100단어 답변 제한 예외

**결정**: Claude 의 "final response ≤100 단어" 규약이 분석·회고·비교 요청에는 적용되지 않음. 루트 CLAUDE.md 에 예외 명시.

**근거**:
- Opus 4.7 의 향상된 reasoning 을 분석에 활용하려면 분량 여유 필요
- 평상 대화는 간결 유지

**주의**: 모델 세대 바뀌면 재평가.

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-04-23 | 초판 — 5개 보조 결정 편입 |
```

- [ ] **Step 2: migration-guide.md 작성**

Create `docs/migration-guide.md` — 기존 `_PROJECT_FRAMEWORK` 사용자용 마이그레이션 가이드:

```markdown
# Migration Guide — `_PROJECT_FRAMEWORK` → `claude-project-bootstrap`

기존에 로컬 `_PROJECT_FRAMEWORK` 폴더 + 글로벌 `~/.claude/commands/init-project.md` 로 프로젝트를 초기화했던 사용자용 마이그레이션 가이드.

## 변경 요약

| 기존 | 신규 |
|---|---|
| `~/Documents/GitHub/_PROJECT_FRAMEWORK/` 로컬 폴더 | `claude plugin install claude-project-bootstrap` |
| `/init-project` (글로벌 커맨드 파일) | `/init-project` (플러그인 커맨드) |
| 절대경로 `cp $PROJECT_FRAMEWORK/...` | 플러그인 내부 `${CLAUDE_PLUGIN_ROOT}/...` |
| `~/Documents/GitHub/_PROJECT_FRAMEWORK/hooks/install-hooks.sh` 수동 실행 | `/init-project` 가 내부적으로 실행 |

## 마이그레이션 절차

### 1. 기존 글로벌 커맨드 제거

기존 `~/.claude/commands/init-project.md` 가 있으면 제거:

```bash
rm ~/.claude/commands/init-project.md
# 또는 .bak 으로 백업된 경우:
rm ~/.claude/commands/init-project.md.bak
```

### 2. 글로벌 `~/.claude/CLAUDE.md` 정리

기존에 다음 섹션이 있다면 제거:

```markdown
## 🆕 새 프로젝트 초기화
작업 디렉토리에 `CLAUDE.md` 가 없으면 `/Users/.../_PROJECT_FRAMEWORK/README.md` 를 참조하고 `/init-project` 실행을 사용자에게 제안.
```

플러그인 설치 후에는 `/init-project` 를 **사용자가 명시적으로 호출** 하는 방식으로 변경됩니다.

### 3. 플러그인 설치

```bash
claude plugin marketplace add seungjaeyuu/claude-project-bootstrap
claude plugin install claude-project-bootstrap
```

### 4. 기존 `_PROJECT_FRAMEWORK` 폴더 처리

**삭제하지 마세요**. 참고용 로컬 백업으로 유지하거나, GitHub 의 archived 저장소 (`github.com/seungjaeyuu/_PROJECT_FRAMEWORK`) 를 참조하세요. 이미 `claude-project-bootstrap` 으로 대체됐으므로 로컬에서는 더 이상 참조할 일이 없습니다.

## 기능 변경

Phase 0.1 의 기능은 모두 동일하게 유지. 다음만 변경:

- **scripts 복사 경로**: `$PROJECT_FRAMEWORK/scripts/*.py` → `${CLAUDE_PLUGIN_ROOT}/scripts/*.py`
- **템플릿 파일 확장자**: `CLAUDE_TEMPLATE.md` → `CLAUDE.md.tmpl` (플러그인 내부)
- **설치 검증**: `/init-project` 가 내부 스모크 테스트 포함 (기존 install-hooks.sh 의 수동 메시지 개선)

## 트러블슈팅

### `/init-project` 커맨드를 못 찾는 경우

```bash
claude plugin list
```

`claude-project-bootstrap` 이 없으면 Step 3 다시 실행.

### 기존 `$PROJECT_FRAMEWORK` 환경 변수 참조

쉘 환경에 `PROJECT_FRAMEWORK` 환경 변수가 설정돼 있으면 제거:

```bash
# ~/.zshrc 또는 ~/.bashrc 에서
unset PROJECT_FRAMEWORK
# 그리고 해당 export 라인 삭제
```
```

- [ ] **Step 3: DESIGN_DECISIONS.md 삭제 (분할 완료)**

```bash
rm docs/DESIGN_DECISIONS.md
```

- [ ] **Step 4: Commit**

```bash
git add docs/design-principles.md docs/changelog-decisions.md docs/migration-guide.md
git rm docs/DESIGN_DECISIONS.md
git commit -m "docs: DESIGN_DECISIONS 를 design-principles + changelog-decisions + migration-guide 로 분할 편입"
```

---

## Phase 5: 경로 참조 치환 + README 전면 재작성

**목적:** 이관된 파일들의 경로 참조를 `${CLAUDE_PLUGIN_ROOT}` 로 치환. `/init-project` 커맨드 본문의 `cp $PROJECT_FRAMEWORK/...` 를 플러그인 경로로. README 전면 재작성.

### Task 5.1: commands/init-project.md 경로 치환

**Files:**
- Modify: `commands/init-project.md` (다중 위치)

사전 조사:

```bash
grep -n "PROJECT_FRAMEWORK" commands/init-project.md
```

예상 매치 라인: ~10건 (spec 파악 기준).

- [ ] **Step 1: 모든 `$PROJECT_FRAMEWORK` 를 `${CLAUDE_PLUGIN_ROOT}` 로 교체**

Edit `commands/init-project.md`: `replace_all: true` 로

```
old_string: $PROJECT_FRAMEWORK
new_string: ${CLAUDE_PLUGIN_ROOT}
```

- [ ] **Step 2: 템플릿 파일 확장자 변경 반영**

원본의 `cp $PROJECT_FRAMEWORK/CLAUDE_TEMPLATE.md ./CLAUDE.md` 류를 **플러그인 경로 + `.tmpl` 확장자** 로. 다음 치환들을 순차 Edit:

```
old: ${CLAUDE_PLUGIN_ROOT}/CLAUDE_TEMPLATE.md
new: ${CLAUDE_PLUGIN_ROOT}/templates/CLAUDE.md.tmpl

old: ${CLAUDE_PLUGIN_ROOT}/INDEX_TEMPLATE.md
new: ${CLAUDE_PLUGIN_ROOT}/templates/INDEX.md.tmpl

old: ${CLAUDE_PLUGIN_ROOT}/.gitignore.template
new: ${CLAUDE_PLUGIN_ROOT}/templates/gitignore.tmpl

old: ${CLAUDE_PLUGIN_ROOT}/TESTING_FRAMEWORK_TEMPLATE.md
new: ${CLAUDE_PLUGIN_ROOT}/templates/TESTING_FRAMEWORK.md.tmpl

old: ${CLAUDE_PLUGIN_ROOT}/BASELINE_TEMPLATE.md
new: ${CLAUDE_PLUGIN_ROOT}/templates/BASELINE.md.tmpl

old: ${CLAUDE_PLUGIN_ROOT}/scripts/baseline.yml.template
new: ${CLAUDE_PLUGIN_ROOT}/templates/baseline.yml.tmpl

old: ${CLAUDE_PLUGIN_ROOT}/hooks/install-hooks.sh
new: ${CLAUDE_PLUGIN_ROOT}/scripts/install-hooks.sh
```

- [ ] **Step 3: 라인 155-156 참조 업데이트**

기존 "참조" 섹션의 경로를 spec / design-principles 참조로:

```
old: - PROJECT_FRAMEWORK README: `/Users/yuseungjae/Documents/GitHub/_PROJECT_FRAMEWORK/README.md`
     - DESIGN_DECISIONS: `/Users/yuseungjae/Documents/GitHub/_PROJECT_FRAMEWORK/docs/DESIGN_DECISIONS.md`

new: - 플러그인 설계 원칙: `${CLAUDE_PLUGIN_ROOT}/docs/design-principles.md`
     - 스펙: `${CLAUDE_PLUGIN_ROOT}/docs/specs/2026-04-23-claude-project-bootstrap-plugin-design.md`
```

- [ ] **Step 4: 검증 grep**

```bash
grep -n "PROJECT_FRAMEWORK\|yuseungjae" commands/init-project.md
```

Expected: 매치 없음.

### Task 5.2: scripts/install-hooks.sh 경로 해석 수정

**Files:**
- Modify: `scripts/install-hooks.sh`

원본 `install-hooks.sh` 는 `FRAMEWORK="$(cd "$(dirname "$0")/.." && pwd)"` 로 **자기 상대경로** 에서 framework 루트 추론. 플러그인 구조에서는 **hooks/ 가 사라졌으므로** `dirname "$0"` 이 `scripts/` 가 됨 → `FRAMEWORK` 변수가 플러그인 루트를 가리키려면 한 단계만 상위.

- [ ] **Step 1: FRAMEWORK 변수 추론 로직 업데이트**

Edit `scripts/install-hooks.sh`:

```
old_string: FRAMEWORK="$(cd "$(dirname "$0")/.." && pwd)"

new_string: # 플러그인 설치 시: ${CLAUDE_PLUGIN_ROOT} 를 우선 사용
# 수동 실행 시: 스크립트의 자기 상위 디렉토리
FRAMEWORK="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
```

- [ ] **Step 2: settings.json 경로 참조 수정**

`install-hooks.sh` 의 라인 63 근처:

```
old: cp "$FRAMEWORK/hooks/settings.json.template" "$CC_SETTINGS"
new: cp "$FRAMEWORK/templates/settings.json.tmpl" "$CC_SETTINGS"
```

- [ ] **Step 3: baseline.yml 경로 참조 수정**

라인 80 근처:

```
old: cp "$FRAMEWORK/scripts/baseline.yml.template" "$ROOT/scripts/baseline.yml"
new: cp "$FRAMEWORK/templates/baseline.yml.tmpl" "$ROOT/scripts/baseline.yml"
```

- [ ] **Step 4: .gitignore 경로 참조**

라인 97 근처:

```
old: cp "$FRAMEWORK/.gitignore.template" "$ROOT/.gitignore"
new: cp "$FRAMEWORK/templates/gitignore.tmpl" "$ROOT/.gitignore"
```

- [ ] **Step 5: pre-commit 스크립트 출처 수정**

라인 40 근처:

```
old: cp "$FRAMEWORK/hooks/pre-commit-framework.sh" "$HOOK_TARGET"
new: cp "$FRAMEWORK/scripts/pre-commit-framework.sh" "$HOOK_TARGET"
```

- [ ] **Step 6: 검증**

```bash
grep -n "hooks/\|\.template" scripts/install-hooks.sh
```

Expected: `FRAMEWORK/hooks/` 나 `FRAMEWORK/...template` 류 매치 없음. (단, target 프로젝트 측 `.git/hooks/` 는 그대로 유지 — 이건 target 프로젝트의 실제 Git hook 디렉토리임.)

### Task 5.3: README.md 전면 재작성 + commit

**Files:**
- Modify: `README.md` (Phase 1 의 WIP 초안 → 최종판)

- [ ] **Step 1: README 전면 재작성**

Edit `README.md` → 아래 전체 내용으로 교체:

````markdown
# claude-project-bootstrap

> Claude Code plugin that bootstraps new projects with **negative-first** rules, a **baseline test harness**, and accessibility/dict-duplicate guards. Scaffolds CLAUDE.md, testing framework docs, pre-commit hooks, and a dynamic `baseline.yml` tailored to the project type you pick.

**본 플러그인은 새 프로젝트 시작 시 Claude Code 에서 일관된 규약으로 출발할 수 있게 하는 재사용 프레임워크입니다.** 실전 프로젝트에서 반복 시행착오로 결정화된 패턴을 다음 프로젝트부터 **기본값으로** 적용합니다.

---

## 빠른 시작

```bash
# 1. 마켓플레이스 등록
claude plugin marketplace add seungjaeyuu/claude-project-bootstrap

# 2. 설치
claude plugin install claude-project-bootstrap

# 3. 새 프로젝트 폴더에서 Claude Code 실행 후:
/init-project
```

`/init-project` 가 대화형 질의를 통해 필요한 파일만 생성합니다.

---

## 제공하는 것

### 슬래시 커맨드 2개

| 커맨드 | 용도 |
|---|---|
| `/init-project` | 새 프로젝트 초기화 — `CLAUDE.md`, `.gitignore`, `TESTING_FRAMEWORK.md`, `BASELINE.md`, hooks 등을 선택적으로 생성 |
| `/baseline-review` | E2E 테스트 베이스라인 갱신 제안 (Git diff 기반) |

### 생성되는 파일 (옵션별)

| 옵션 | 생성되는 파일 |
|---|---|
| 기본 (모두 필수) | `CLAUDE.md`, `INDEX.md`, `.gitignore`, `.secret/.gitkeep` |
| E2E 테스트 프레임워크 필요? (Yes) | `TESTING_FRAMEWORK.md`, `{APP}_MASTER_TEST_BASELINE.md`, `scripts/baseline.yml` |
| Firebase/Supabase 사용? (Yes) | default-deny 보안 규칙 안내 섹션 + `.env.example` 초안 |
| Hook 자동 설치? (Yes) | `.claude/settings.json`, `.git/hooks/pre-commit` symlink, `scripts/check_*.py`, `scripts/baseline_*.py` |
| Accessibility identifier 검증? (Yes) | `ACCESSIBILITY_IDENTIFIERS.md` 템플릿 + 관련 스크립트 |
| 개발 백로그 관리? (Yes) | `/개발예정사항.md` + `개발예정사항_상세/` 구조 |

### 제공하는 Python 스크립트 (target 프로젝트로 복사)

| 스크립트 | 기능 |
|---|---|
| `baseline_status.py` | 베이스라인 판정 상태 집계 |
| `baseline_update_suggest.py` | Git diff 기반 베이스라인 갱신 제안 |
| `check_baseline_sync.py` | pre-commit — UI 파일 수정 시 baseline 갱신 확인 |
| `check_accessibility_identifiers.py` | SwiftUI/Kotlin Compose accessibility 라벨 검증 |
| `check_dict_duplicates.py` | Swift/Kotlin/TypeScript dict literal 중복 키 검출 |

---

## 설계 철학

**네거티브 우선** — 규칙은 "하지 말라" 만 적고 그 외는 모두 허용. 고성능 LLM 이 자력 판단 가능한 일반 모범 사례는 템플릿에서 제외.

**4층 규칙 범례** — 🚫 Guardrail / 📐 Schema / 📎 참조 / 💡 권장. 각 규칙의 강제력을 명시.

**단일 SSOT + 발견 경로 최적화** — 같은 규칙을 여러 곳에 복붙하지 않음. "어느 맥락에서 Claude 가 Read 하는가" 를 설계.

상세 근거: [`docs/design-principles.md`](docs/design-principles.md)

---

## 마이그레이션 (기존 `_PROJECT_FRAMEWORK` 사용자)

기존에 `~/Documents/GitHub/_PROJECT_FRAMEWORK/` 로컬 폴더 + `~/.claude/commands/init-project.md` 를 사용하셨다면 [`docs/migration-guide.md`](docs/migration-guide.md) 참조.

---

## 문서

- [설계 원칙](docs/design-principles.md) — 왜 이렇게 설계했는지
- [내부 결정 로그](docs/changelog-decisions.md) — 보조 결정 기록
- [마이그레이션 가이드](docs/migration-guide.md) — 기존 사용자용
- [스펙 (전체 설계 문서)](docs/specs/2026-04-23-claude-project-bootstrap-plugin-design.md)

---

## 라이선스

[MIT](LICENSE) © 2026 Yu Seungjae
````

- [ ] **Step 2: Commit**

```bash
git add commands/init-project.md scripts/install-hooks.sh README.md
git commit -m "feat: ${CLAUDE_PLUGIN_ROOT} 경로 치환 + README 최종판 작성"
```

---

## Phase 6: 정적 검증

**목적:** 플러그인 저장소 전체에서 사적 맥락이 완전히 제거됐는지 grep 으로 확인. Spec Section 5.2 의 검증 10번 항목.

### Task 6.1: 사적 맥락 grep 0건 확인

- [ ] **Step 1: 금지 키워드 전수 검색**

```bash
grep -rn "SunnyWay\|sunnyway\|Lane B\|PRV-06\|2026-04-1[0-9]\|2026-04-2[0-9]\|PR #[0-9]\|DEV-066\|DEV-067\|DEV-068\|DEV-069\|EXAMPLE-S01" . \
  --exclude-dir=.git --exclude-dir=docs/specs --exclude-dir=docs/plans
```

**Expected**: **매치 0건**.

예외 허용 파일·섹션:
- `docs/specs/*`, `docs/plans/*` — 내부 설계 문서. generic 화 대상 아님.
- 날짜 `2026-04-23` — 플러그인 생성일. 허용.

- [ ] **Step 2: "보호자" 예시는 라벨 검증**

```bash
grep -B2 "보호자" templates/CLAUDE.md.tmpl
```

**Expected**: 바로 위 2줄 이내에 "실제 프로덕션 프로젝트의 경우" 라벨 존재.

- [ ] **Step 3: 매치 발견 시 수정**

grep 에서 매치가 나오면 해당 파일 열어 generic 화. 이 Task 는 **매치 0건 상태** 가 되어야 Phase 7 진입 가능.

---

## Phase 7: 로컬 동작 검증 (10 항목)

**목적:** Spec Section 5.2 의 검증 10항목 중 정적 항목(10번) 제외한 9개를 실제 Claude Code 세션에서 수행. 실패 항목 있으면 Phase 4-5 로 돌아가 수정.

**전제:** GitHub 에 아직 push 안 된 상태. 로컬 경로 기준으로 marketplace add 테스트.

### Task 7.1: GitHub 저장소 생성 + 초기 push

- [ ] **Step 1: GitHub 저장소 생성 (gh CLI)**

```bash
cd ~/Documents/GitHub/claude-project-bootstrap
gh repo create seungjaeyuu/claude-project-bootstrap --public \
  --description "Claude Code plugin: bootstrap new projects with negative-first rules + baseline harness" \
  --source=. --remote=origin
```

Expected: GitHub 저장소 생성 + origin remote 추가.

- [ ] **Step 2: Push**

```bash
git push -u origin main
```

Expected: 커밋 이력 전체 업로드.

- [ ] **Step 3: 저장소 확인**

```bash
gh repo view seungjaeyuu/claude-project-bootstrap --web
```

웹 브라우저에서 README 렌더링 확인.

### Task 7.2: 테스트 디렉토리에서 marketplace add + install (검증 1, 2)

- [ ] **Step 1: 빈 테스트 디렉토리 생성**

```bash
mkdir -p /tmp/test-bootstrap-$(date +%s)
cd /tmp/test-bootstrap-*
```

- [ ] **Step 2: 플러그인 등록·설치**

```bash
claude plugin marketplace add seungjaeyuu/claude-project-bootstrap
claude plugin install claude-project-bootstrap
```

**Expected (검증 1)**: "marketplace registered" 류 성공 메시지.
**Expected (검증 2)**: "plugin installed" + `claude plugin list` 에 표시.

- [ ] **Step 3: 커맨드 발견 확인**

Claude Code 세션 진입 후 `/` 입력해서 `/init-project` 와 `/baseline-review` 가 목록에 보이는지 확인.

### Task 7.3: /init-project 3가지 시나리오 검증 (검증 3, 4, 5, 9)

- [ ] **Step 1: 시나리오 A — 최소 질의 (E2E No, Hook No)**

테스트 디렉토리에서 Claude Code 세션 시작:

```
/init-project
```

답변:
- 이름: `test-minimal`
- 유형: 단일 웹 (Next.js)
- 언어: Next.js
- Q1~Q5 모두 No

**Expected (검증 3)**: `CLAUDE.md`, `INDEX.md`, `.gitignore`, `.secret/.gitkeep` 생성. 플레이스홀더 치환 완료.

- [ ] **Step 2: 시나리오 B — E2E Yes, iOS 단일 (검증 4)**

새 테스트 디렉토리에서:

```
/init-project
```

답변:
- 이름: `test-ios`
- 유형: 단일 모바일 (SwiftUI)
- Q1: Yes → iOS 선택
- 기타 No

**Expected (검증 4)**:
- `TESTING_FRAMEWORK.md`, `IOS_MASTER_TEST_BASELINE.md`, `scripts/baseline.yml` 생성
- `baseline.yml` 에 **iOS entry 만** 존재 (Android/Web/Flutter/Backend 예시 미포함)

검증 명령:

```bash
cat scripts/baseline.yml | grep -E "^  (ios|android|web|flutter|backend):"
```

Expected: `  ios:` 한 줄만 출력.

- [ ] **Step 3: 시나리오 C — E2E + Hook Yes (검증 5)**

새 테스트 디렉토리에서 `/init-project` 실행:
- Q1: Yes → iOS
- Q3: Yes (Hook 설치)

**Expected (검증 5)**:

```bash
ls -la .claude/settings.json .git/hooks/pre-commit scripts/
```

- `.claude/settings.json` 존재
- `.git/hooks/pre-commit` symlink 존재 (target: `scripts/pre-commit-framework.sh`)
- `scripts/` 안에 `check_accessibility_identifiers.py`, `check_baseline_sync.py`, `check_dict_duplicates.py`, `baseline_status.py`, `baseline_update_suggest.py`, `pre-commit-framework.sh` 존재
- `install-hooks.sh` 는 **복사되지 않음** (플러그인 내부 전용)

- [ ] **Step 4: 시나리오 D — 기존 CLAUDE.md 회귀 테스트 (검증 9)**

시나리오 A 의 디렉토리 (CLAUDE.md 이미 있음) 에서 다시 `/init-project`:

**Expected (검증 9)**: **중단** 하고 "CLAUDE.md 가 이미 존재합니다" 알림. 파일 덮어쓰기 없음.

### Task 7.4: Hook 동작 + /baseline-review 검증 (검증 6, 7, 8)

- [ ] **Step 1: PostToolUse hook 트리거 테스트 (검증 6)**

시나리오 C 디렉토리에서 Swift/Kotlin 파일 생성·편집:

```bash
mkdir -p apps/ios
touch apps/ios/TestView.swift
```

Claude Code 세션에서 Edit 툴로 `apps/ios/TestView.swift` 에 SwiftUI 코드 입력. accessibility identifier 누락된 버튼을 포함.

**Expected (검증 6)**: PostToolUse hook 이 `check_accessibility_identifiers.py` 실행, 위반 경고 출력 (차단 아님).

- [ ] **Step 2: pre-commit hook 동작 (검증 7)**

```bash
cd <시나리오 C 디렉토리>
git init
git add .
git commit -m "test: pre-commit hook 트리거"
```

**Expected (검증 7)**: pre-commit 이 `check_baseline_sync.py` + `check_dict_duplicates.py` 호출. UI 파일 수정 + baseline 미갱신 시 경고.

- [ ] **Step 3: /baseline-review 실행 (검증 8)**

시나리오 C 디렉토리에서 Claude Code 세션:

```
/baseline-review
```

**Expected (검증 8)**: `scripts/baseline_update_suggest.py` 호출, Git diff 분석 결과 출력.

- [ ] **Step 4: 실패 항목 정리**

검증 6~8 중 실패한 항목을 이 체크리스트에 기록:

| 검증 # | 통과/실패 | 실패 시 원인 추정 |
|---|---|---|
| 1 | ☐ | |
| 2 | ☐ | |
| 3 | ☐ | |
| 4 | ☐ | |
| 5 | ☐ | |
| 6 | ☐ | |
| 7 | ☐ | |
| 8 | ☐ | |
| 9 | ☐ | |
| 10 | ☐ (Phase 6 에서 이미 확인) | |

**실패 항목 있으면**: Phase 4~5 로 돌아가 수정 → Phase 6, 7 재실행.
**전부 통과 시**: Phase 8 진행.

---

## Phase 8: 공개 배포 + 기존 저장소 archive

**목적:** v0.1.0 태그 릴리스, 기존 `_PROJECT_FRAMEWORK` archive, `.bak` 백업 제거.

### Task 8.1: v0.1.0 릴리스

- [ ] **Step 1: CHANGELOG 업데이트**

Edit `CHANGELOG.md`:

```
old: ## [0.1.0] - TBD
new: ## [0.1.0] - 2026-04-23

### Added
- `/init-project` 슬래시 커맨드 — 대화형 프로젝트 초기화
- `/baseline-review` 슬래시 커맨드 — Git diff 기반 베이스라인 갱신 제안
- 7개 템플릿 (CLAUDE.md, INDEX.md, TESTING_FRAMEWORK.md, BASELINE.md, baseline.yml, settings.json, gitignore)
- 5개 Python 검증 스크립트 (baseline_status, baseline_update_suggest, check_baseline_sync, check_accessibility_identifiers, check_dict_duplicates)
- install-hooks.sh + pre-commit-framework.sh
- 설계 원칙 문서 (design-principles.md, changelog-decisions.md, migration-guide.md)
```

- [ ] **Step 2: 태그 생성 + push**

```bash
git add CHANGELOG.md
git commit -m "chore: CHANGELOG v0.1.0 확정"
git tag -a v0.1.0 -m "Initial release"
git push origin main --tags
```

- [ ] **Step 3: GitHub Release 생성**

```bash
gh release create v0.1.0 \
  --title "v0.1.0 — Initial release" \
  --notes-file CHANGELOG.md
```

### Task 8.2: 기존 `_PROJECT_FRAMEWORK` 저장소 archive

- [ ] **Step 1: 기존 저장소 README 에 migration notice 추가**

```bash
cd /Users/yuseungjae/Documents/GitHub/_PROJECT_FRAMEWORK
```

Edit `README.md` 최상단에 다음 블록 **추가** (기존 내용 위에):

```markdown
> ⚠ **이 저장소는 archive 되었습니다.**
>
> 후속 플러그인 저장소로 이관되었습니다: **[claude-project-bootstrap](https://github.com/seungjaeyuu/claude-project-bootstrap)**
>
> 마이그레이션 가이드: https://github.com/seungjaeyuu/claude-project-bootstrap/blob/main/docs/migration-guide.md

---

```

- [ ] **Step 2: Commit + push**

```bash
git add README.md
git commit -m "docs: archive notice — 후속 저장소 안내 추가"
git push origin main
```

- [ ] **Step 3: GitHub 에서 archive 처리**

```bash
gh repo archive seungjaeyuu/_PROJECT_FRAMEWORK --yes
```

Expected: 저장소가 read-only 상태로 전환.

### Task 8.3: `~/.claude/commands/init-project.md.bak` 최종 제거

- [ ] **Step 1: 검증 재확인**

Phase 7 의 검증 10항목 전체가 통과했는지 최종 확인.

**통과 시에만** Step 2 진행. 하나라도 실패 상태면 `.bak` 유지 후 디버깅.

- [ ] **Step 2: .bak 파일 제거**

```bash
rm ~/.claude/commands/init-project.md.bak
ls -la ~/.claude/commands/
```

Expected: `init-project.md.bak` 없음. (다른 글로벌 커맨드가 있을 수 있음 — 그것들은 유지.)

- [ ] **Step 3: 최종 상태 확인**

```bash
claude plugin list | grep claude-project-bootstrap
gh repo view seungjaeyuu/claude-project-bootstrap
gh repo view seungjaeyuu/_PROJECT_FRAMEWORK  # archived 표시 확인
```

---

## 완료 기준

- ✅ Phase 1~8 의 모든 Task 완료
- ✅ Phase 6 정적 grep 0건 (사적 맥락 완전 제거)
- ✅ Phase 7 의 검증 10항목 전부 PASS
- ✅ GitHub `seungjaeyuu/claude-project-bootstrap` public + v0.1.0 릴리스 태그
- ✅ GitHub `seungjaeyuu/_PROJECT_FRAMEWORK` archived 상태
- ✅ `~/.claude/commands/init-project.md.bak` 제거
- ✅ 플러그인 설치 후 빈 프로젝트에서 `/init-project` 1회 실행으로 기대 동작 재현

---

## 주의사항 (전체 Phase 공통)

1. **`_PROJECT_FRAMEWORK` 수정 금지** — Phase 8.2 의 archive notice 1건 외에는 건드리지 않음.
2. **SunnyWay 저장소 영향 금지** — 본 플러그인 개발은 `~/Documents/GitHub/claude-project-bootstrap/` 내에서만. SunnyWay worktree 파일에 영향 주면 안 됨.
3. **`git reset --hard` 는 이번 한정 허용** (사용자 명시 승인) 이지만, Phase 8.2 기존 저장소 archive 준비 단계에서만 사용 검토. 그 외는 사용 금지.
4. **커밋 단위**: 한 커밋 = 하나의 목적. 본 계획은 이미 단위별로 분리되어 있음. 편의상 batch 하지 말 것.
5. **Phase 7 실패 시**: 원인 파악 후 Phase 4-5 의 해당 Task 로 복귀. Phase 7 재실행.
