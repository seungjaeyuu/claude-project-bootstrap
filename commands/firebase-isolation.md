---
description: Add Firebase isolation guardrails — .firebaserc + firebase.json predeploy hook + verify script + CLAUDE.md guard — Firebase 격리 안전장치 도입
argument-hint: (선택 없음 — 대화형)
allowed-tools: Read, Write, Edit, Bash(cp:*), Bash(mkdir:*), Bash(cat:*), Bash(diff:*), Bash(ls:*), Bash(rm:*), Bash(grep:*), Bash(chmod:*), Bash(python3:*)
---

> **v0.3.0**: 이 커맨드는 `/init --firebase` 에 통합되었습니다. 동일 기능을 실행합니다.

# /firebase-isolation — Firebase 프로젝트 격리 도입

다른 Firebase 프로젝트로 잘못 deploy 되는 사고를 메커니즘으로 차단. `predeploy` hook 이 어디서 호출되든 (Claude / 사용자 직접 / CI) 활성 프로젝트 검증을 자동 실행.

## 4중 안전장치

- **자동 백업**: `.firebaserc` / `firebase.json` / `CLAUDE.md` / `INDEX.md` 변경 전 `_backup_v0.1/` 으로 복사
- **Diff preview**: 변경 적용 전 diff 출력 → yes/no
- **영역 독립**: Firebase 관련 파일만 변경. 다른 도구 설정 보존
- **idempotent**: 이미 격리 설정된 프로젝트면 갱신 (project ID 변경 등) 가능

## 절차

### Step 1. Firebase project ID 입력

사용자에게 프로젝트 ID 받기 (예: `appfoo-prod`). 이 값을 `<FB_PROJECT_ID>` 라 한다.

### Step 2. 백업

```bash
mkdir -p _backup_v0.1
TS=$(date +%Y%m%d_%H%M%S)
[ -f .firebaserc ] && cp .firebaserc "_backup_v0.1/.firebaserc.${TS}"
[ -f firebase.json ] && cp firebase.json "_backup_v0.1/firebase.json.${TS}"
[ -f CLAUDE.md ] && cp CLAUDE.md "_backup_v0.1/CLAUDE.md.${TS}"
[ -f INDEX.md ] && cp INDEX.md "_backup_v0.1/INDEX.md.${TS}"

# .gitignore 등록 (이미 있으면 skip)
if [ -f .gitignore ] && ! grep -q "^_backup_v0.1/" .gitignore; then
  echo "" >> .gitignore
  echo "# claude-project-bootstrap 마이그/재설정 자동 백업" >> .gitignore
  echo "_backup_v0.1/" >> .gitignore
fi
```

### Step 3. `.firebaserc` 작성

```bash
cat > .firebaserc <<EOF
{
  "projects": {
    "default": "<FB_PROJECT_ID>"
  }
}
EOF
```

기존 `.firebaserc` 가 있고 `default` 가 다른 ID 면 사용자 confirm 후 덮어씀.

### Step 4. `firebase.json` predeploy hook 등록

기존 파일 있으면 4개 영역(functions/hosting/firestore/storage)의 `predeploy` 키만 머지 (다른 키 보존). 없으면 `templates/firebase.json.tmpl` 복사.

머지 로직 (Claude 가 직접):
1. 기존 firebase.json read → dict 파싱
2. `functions.predeploy` / `hosting.predeploy` / `firestore.predeploy` / `storage.predeploy` 각각:
   - 키 자체가 없으면 신규 생성: `["python3 scripts/check_firebase_project.py"]`
   - 이미 있으면 배열에 append (중복은 skip)
3. 결과 Write

### Step 5. 검증 스크립트 복사

```bash
mkdir -p scripts
cp ${CLAUDE_PLUGIN_ROOT}/scripts/check_firebase_project.py scripts/
chmod +x scripts/check_firebase_project.py
```

### Step 6. CLAUDE.md 본체에 §NEW Firebase 격리 추가 (사용자 confirm 후)

기존 CLAUDE.md 의 §변경이력 직전에 다음 3줄 삽입:

```markdown
## NEW. 🚫 Firebase 프로젝트 격리 (project: <FB_PROJECT_ID>)

- `firebase deploy` 단독 호출 금지. 반드시 `--project <FB_PROJECT_ID>` 명시
- 사용자에게 deploy 명령 안내 시 `--project` 명시 형태로 제공
- predeploy hook 이 활성 프로젝트와 `.firebaserc` 일치를 자동 검증
```

이미 §NEW Firebase 섹션이 있으면 project ID 만 갱신 (idempotent).

### Step 7. INDEX.md 에 직접 실행 체크리스트 추가 (있으면)

```markdown
## Firebase deploy (직접 실행 체크리스트)

터미널 직접 deploy 시 1초 검증:
1. `cat .firebaserc` → `projects.default` 가 `<FB_PROJECT_ID>` 인지 확인
2. `firebase deploy --project <FB_PROJECT_ID> --only <services>`
```

### Step 8. 글로벌 캐시 검증 + 완료 리포트

```bash
python3 scripts/check_firebase_project.py --init-check "<FB_PROJECT_ID>"
```

```
✅ Firebase 격리 설정 완료

   project ID: <FB_PROJECT_ID>
   생성·수정: .firebaserc / firebase.json / scripts/check_firebase_project.py
              / CLAUDE.md (§NEW 3줄) / INDEX.md (체크리스트)
   백업: _backup_v0.1/<원본>.<TS>

다음 deploy 전 권장:
   firebase use <FB_PROJECT_ID>
```

## 참조

- spec: `${CLAUDE_PLUGIN_ROOT}/docs/specs/2026-05-05-v0.2.0-permissions-and-doc-slimming-design.md` §4, §9
- 검증 스크립트 사양: `${CLAUDE_PLUGIN_ROOT}/scripts/check_firebase_project.py`
