---
name: project-review
description: 이 저장소 전용 리뷰 워크플로로, 로컬 변경 사항을 저장소 아키텍처, ADR 기술 선택, 테스트, AGENTS.md의 CRITICAL 규칙, 빌드 상태와 대조해 확인할 때 사용한다. Codex가 현재 변경 사항을 리뷰하거나, harness step을 검증하거나, 구현 품질을 확인하거나, commit 또는 후속 작업 전에 위반 사항을 보고해야 할 때 사용한다.
---

# Project Review

이 프로젝트의 변경 사항을 저장소 규칙과 구현 문서에 맞춰 리뷰한다. 문제가 있으면 구체적인 finding과 파일 참조를 먼저 제시한다.

## 필수 맥락

리뷰 전에 다음 파일을 읽는다.

- `/AGENTS.md`
- `/docs/ARCHITECTURE.md`
- `/docs/ADR.md`

또한 `git status`, `git diff`, 대상 파일 읽기를 사용해 변경된 파일을 확인한다.

## 체크리스트

다음 항목을 검증한다.

1. 아키텍처 준수: 변경된 파일이 `ARCHITECTURE.md`의 디렉터리 구조와 경계를 따른다.
2. 기술 스택 준수: 구현이 `ADR.md`의 기술 선택 범위 안에 머문다.
3. 테스트 커버리지: 새 기능에 관련 테스트가 있다.
4. CRITICAL 규칙: `AGENTS.md`에서 CRITICAL로 표시된 규칙을 위반하지 않는다.
5. 빌드 상태: 문서화된 빌드 및 테스트 명령이 통과하거나, 실행할 수 없는 경우 그 이유를 명확히 보고한다.

## 명령어

이 저장소가 정의한 명령어를 우선 사용한다. package script가 없으면 가장 가까운 프로젝트 전용 검증 명령을 사용하고, 대체한 내용을 보고한다.

```bash
npm run build
npm test
```

## 출력

이슈가 발견되면 severity 순서로 finding을 먼저 나열하고 파일 및 line reference를 포함한다. 그 다음 아래 체크리스트 표를 제공한다.

| Item | Result | Notes |
| --- | --- | --- |
| Architecture compliance | PASS/FAIL | {details} |
| Technology stack compliance | PASS/FAIL | {details} |
| Test coverage | PASS/FAIL | {details} |
| CRITICAL rules | PASS/FAIL | {details} |
| Build health | PASS/FAIL | {details} |

각 위반 사항에는 구체적인 수정 방안을 제안한다. 이슈가 없으면 그 사실을 명확히 말하고, 실행하지 못한 테스트나 점검이 있으면 함께 언급한다.
