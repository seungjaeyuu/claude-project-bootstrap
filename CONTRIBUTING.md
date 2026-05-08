# Contributing / 기여 가이드

> **Language**: This project's primary language is Korean, but issues and PRs in English are welcome.

## Quick Start

```bash
# 1. Fork & clone
git clone https://github.com/<your-username>/claude-project-bootstrap.git
cd claude-project-bootstrap

# 2. Install the plugin locally
claude plugin install --local .

# 3. Test in a scratch directory
mkdir /tmp/test-project && cd /tmp/test-project
# then run /claude-project-bootstrap:init-project
```

## 이슈 & PR

- **버그 리포트**: `.github/ISSUE_TEMPLATE/bug_report.md` 양식 사용
- **기능 제안**: `.github/ISSUE_TEMPLATE/feature_request.md` 양식 사용
- **질문**: `.github/ISSUE_TEMPLATE/question.md` 양식 사용
- **PR**: 하나의 PR 에는 하나의 목적만 포함

## 커밋 컨벤션

[Conventional Commits](https://www.conventionalcommits.org/) 를 따릅니다.

```
<type>(<scope>): <subject>

feat(init-project):   새 기능
fix(permissions):     버그 수정
docs(principles):     문서 변경
chore(release):       빌드/릴리스
refactor(scripts):    리팩토링
```

## 코드 기여 시 확인 사항

1. `scripts/check_version_sync.py` — plugin.json / marketplace.json 버전 동기화 확인
2. `scripts/check_doc_size.py` — CLAUDE.md 120줄, RULES 250줄 임계치
3. 템플릿 수정 시 `/init-project` 로 새 디렉터리에 실행해 결과 확인

## 릴리스

maintainer 만 수행합니다.

```bash
scripts/release.sh <new_version>   # 버전 갱신 + 커밋 + 태그
git push origin main --tags
gh release create v<new_version> --title "v<new_version> — <제목>" --notes-file -
```

## License

MIT. 기여한 코드도 동일 라이선스로 배포됩니다.
