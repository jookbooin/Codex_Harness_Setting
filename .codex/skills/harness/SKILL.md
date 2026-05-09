---
name: harness
description: 이 저장소 전용 harness 워크플로로, 단계별 구현 작업을 계획하고 실행할 때 사용한다. Codex가 phase 계획을 만들거나, 작업을 step 파일로 나누거나, `phases/index.json` 또는 `phases/{task-name}/index.json`을 관리하거나, `scripts/execute.py`를 실행하거나, 실패/차단된 harness step을 복구하거나, 이 저장소의 phase/step harness를 통해 작업해야 할 때 사용한다.
---

# Harness

구현 계획과 순차 실행에는 이 저장소의 harness 워크플로를 사용한다. step 독립성을 보존한다. 모든 step 파일은 이전 대화에 의존하지 않고 새 Codex 세션이 실행할 수 있을 만큼 충분한 맥락을 포함해야 한다.

## 워크플로

### 1. 탐색

제품 의도, 아키텍처, 디자인 제약을 이해하기 위해 `/docs/` 아래의 `PRD.md`, `ARCHITECTURE.md`, `ADR.md`, `UI_GUIDE.md` 같은 문서를 읽는다. 계획 또는 실행 전에 프로젝트 규칙 확인을 위해 `AGENTS.md`를 읽는다.

### 2. 명확화

구현에 제품 결정, 기술적 트레이드오프, 자격 증명, 외부 서비스, 수동 설정이 필요하면 step을 만들거나 실행하기 전에 열린 쟁점을 사용자에게 제시한다.

### 3. Step 설계

구현 계획 작성을 요청받으면 여러 개의 작은 step을 초안으로 작성하고, 파일을 만들기 전에 피드백을 요청한다.

다음 규칙을 따른다.

1. 범위를 최소화한다. 하나의 step은 하나의 레이어 또는 모듈만 다뤄야 한다. 여러 모듈이 함께 변경되어야 하면 step을 나눈다.
2. 각 step을 자체 완결적으로 만든다. "앞서 논의한 대로"처럼 이전 대화에 의존하는 표현을 쓰지 않는다. 필요한 맥락은 step 파일에 넣는다.
3. 준비를 강제한다. 실행 세션이 편집 전에 코드를 읽도록 관련 문서와 이전 step의 파일을 나열한다.
4. 유용한 경우 시그니처와 인터페이스를 명시하되, 반드시 필요한 규칙이 아니라면 구현 세부사항은 실행 agent에게 맡긴다.
5. `npm run build`, `npm test`처럼 실행 가능한 인수 기준을 사용한다.
6. "Do not do X. Reason: Y." 형식의 구체적인 경고를 작성한다.
7. 각 step 이름은 `project-setup`, `api-layer`, `auth-flow` 같은 kebab-case slug로 정한다.

## Phase 파일

모든 작업을 추적하려면 `phases/index.json`을 만들거나 업데이트한다. 이미 존재하면 `phases` 배열에 새 항목을 추가한다.

```json
{
  "phases": [
    {
      "dir": "0-mvp",
      "status": "pending"
    }
  ]
}
```

다음 필드를 사용한다.

- `dir`: 작업 디렉터리 이름.
- `status`: `pending`, `completed`, `error`, `blocked` 중 하나.
- 파일을 만들 때 timestamp를 추가하지 않는다. `scripts/execute.py`가 `completed_at`, `failed_at`, `blocked_at`을 기록한다.

작업 상세 정보는 `phases/{task-name}/index.json`에 만든다.

```json
{
  "project": "<project-name>",
  "phase": "<task-name>",
  "steps": [
    { "step": 0, "name": "project-setup", "status": "pending" },
    { "step": 1, "name": "core-types", "status": "pending" },
    { "step": 2, "name": "api-layer", "status": "pending" }
  ]
}
```

다음 필드 규칙을 사용한다.

- `project`: `AGENTS.md`의 프로젝트 이름.
- `phase`: 디렉터리 이름과 일치하는 작업 이름.
- `steps[].step`: 0부터 시작하는 step 번호.
- `steps[].name`: kebab-case slug.
- `steps[].status`: 초기값은 `pending`.
- `created_at` 또는 step `started_at`을 추가하지 않는다. `scripts/execute.py`가 이를 기록한다.

상태 전환:

| Status | Fields | Writer |
| --- | --- | --- |
| `completed` | `completed_at`, `summary` | Codex가 `summary`를 작성하고, `execute.py`가 timestamp를 작성한다 |
| `error` | `failed_at`, `error_message` | Codex가 message를 작성하고, `execute.py`가 timestamp를 작성한다 |
| `blocked` | `blocked_at`, `blocked_reason` | Codex가 reason을 작성하고, `execute.py`가 timestamp를 작성한다 |

`summary`는 이후 step에 유용한 한 줄 출력 요약이어야 하며, 생성된 파일과 중요한 결정을 포함해야 한다.

## Step 파일 템플릿

step마다 `phases/{task-name}/step{N}.md` 파일을 하나씩 만든다.

````markdown
# Step {N}: {name}

## Files to Read

Read these files first and understand the architecture and design intent:

- `/AGENTS.md`
- `/docs/ARCHITECTURE.md`
- `/docs/ADR.md`
- {files created or modified by previous steps}

Read previous-step code carefully before editing.

## Task

{Concrete implementation instructions. Include paths, relevant classes or functions, interface signatures, and logic requirements. Keep snippets at interface/signature level unless implementation details are mandatory. State any non-negotiable rules clearly.}

## Acceptance Criteria

```bash
npm run build
npm test
```

## Verification

1. Run the acceptance criteria commands.
2. Check architecture constraints:
   - Follow the directory structure in `ARCHITECTURE.md`.
   - Stay within the technology decisions in `ADR.md`.
   - Do not violate CRITICAL rules in `AGENTS.md`.
3. Update `phases/{task-name}/index.json`:
   - Success: set `status` to `completed` and write a one-line `summary`.
   - Failure after 3 fix attempts: set `status` to `error` and write a concrete `error_message`.
   - User action required: set `status` to `blocked`, write a concrete `blocked_reason`, and stop.

## Prohibitions

- {Specific "Do not do X. Reason: Y" items for this step}
- Do not break existing tests.
````

## 실행

저장소 루트에서 harness를 실행한다.

```bash
python scripts/execute.py {task-name}
python scripts/execute.py {task-name} --push
```

`scripts/execute.py`가 처리하는 일:

- `feat-{task-name}` 브랜치를 만들거나 체크아웃한다.
- `AGENTS.md`와 `docs/*.md`의 guardrail을 모든 step prompt에 주입한다.
- 완료된 step 요약을 이후 step prompt로 전달한다.
- 실패한 step을 이전 오류 메시지와 함께 최대 3회 재시도한다.
- 코드 변경(`feat`)과 메타데이터 변경(`chore`)을 두 개의 commit으로 분리한다.
- `started_at`, `completed_at`, `failed_at`, `blocked_at`을 기록한다.

## 복구

`error` step은 해당 step의 `status`를 `pending`으로 되돌리고 `error_message`를 제거한 뒤 harness를 다시 실행한다.

`blocked` step은 `blocked_reason`을 해결하고, `status`를 `pending`으로 되돌리고, `blocked_reason`을 제거한 뒤 harness를 다시 실행한다.
