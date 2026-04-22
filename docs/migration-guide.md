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

플러그인 설치 후에는 `/init-project` 를 **사용자가 명시적으로 호출** 하는 방식으로 변경됩니다 (자동 제안 규칙 불필요 — 사용자가 플러그인 설치를 인지하고 있는 상태이므로).

### 3. 플러그인 설치

```bash
claude plugin marketplace add seungjaeyuu/claude-project-bootstrap
claude plugin install claude-project-bootstrap
```

### 4. 기존 `_PROJECT_FRAMEWORK` 폴더 처리

**삭제하지 마세요**. 참고용 로컬 백업으로 유지하거나, GitHub 의 archived 저장소 (`github.com/seungjaeyuu/_PROJECT_FRAMEWORK`) 를 참조하세요. 이미 `claude-project-bootstrap` 으로 대체됐으므로 로컬에서는 더 이상 참조할 일이 없습니다.

## 기능 변경

기존 `_PROJECT_FRAMEWORK` 의 기능은 모두 동일하게 유지. 다음만 변경:

- **scripts 복사 경로**: `$PROJECT_FRAMEWORK/scripts/*.py` → `${CLAUDE_PLUGIN_ROOT}/scripts/*.py`
- **템플릿 파일 확장자**: `CLAUDE_TEMPLATE.md` → `CLAUDE.md.tmpl` (플러그인 내부 정리)
- **hooks 폴더 경로**: `$PROJECT_FRAMEWORK/hooks/install-hooks.sh` → `${CLAUDE_PLUGIN_ROOT}/scripts/install-hooks.sh` (scripts/ 로 통합)

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

### 기존 프로젝트에 복사된 scripts 는?

이미 `/init-project` 로 초기화한 기존 프로젝트의 `scripts/check_*.py`, `scripts/baseline_*.py` 는 그대로 유지하세요. 플러그인 업데이트 시 target 프로젝트의 scripts 를 자동으로 갱신하지 않습니다 — 각 프로젝트가 독립적으로 동작하도록 설계되어 있기 때문. 수동 업데이트가 필요하면 해당 프로젝트에서 `/init-project --update-scripts` (v0.2+ 예정) 를 호출하거나 파일을 직접 교체하세요.
