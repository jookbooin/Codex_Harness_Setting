---
name: harness
description: Project-specific harness workflow for planning and executing phased implementation work. Use when Codex is asked to create phase plans, split work into step files, manage `phases/index.json` or `phases/{task-name}/index.json`, run `scripts/execute.py`, recover failed or blocked harness steps, or perform work through this repository's phase/step harness.
---

# Harness

Use this repository's harness workflow for implementation planning and sequential execution. Preserve step independence: every step file must contain enough context for a fresh Codex session to execute it without relying on prior chat.

## Workflow

### 1. Explore

Read `/docs/` documents such as `PRD.md`, `ARCHITECTURE.md`, `ADR.md`, and `UI_GUIDE.md` to understand the product intent, architecture, and design constraints. Read `AGENTS.md` for project rules before planning or execution.

### 2. Clarify

If implementation requires product decisions, technical tradeoffs, credentials, external services, or manual setup, present the open point to the user before creating or running steps.

### 3. Design Steps

When asked to write an implementation plan, draft multiple small steps and request feedback before creating files.

Follow these rules:

1. Keep scope minimal. One step should touch one layer or module. Split steps when multiple modules must change together.
2. Make each step self-contained. Do not write phrases that depend on prior chat, such as "as discussed earlier." Put required context in the step file.
3. Force preparation. List relevant docs and files from previous steps so the executing session reads code before editing.
4. Specify signatures and interfaces where useful, but leave implementation details to the executing agent unless a hard rule is required.
5. Use executable acceptance criteria, such as `npm run build` and `npm test`.
6. Write concrete warnings in the form "Do not do X. Reason: Y."
7. Name each step with a kebab-case slug such as `project-setup`, `api-layer`, or `auth-flow`.

## Phase Files

Create or update `phases/index.json` to track all tasks. If it already exists, append a new item to the `phases` array.

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

Use these fields:

- `dir`: task directory name.
- `status`: `pending`, `completed`, `error`, or `blocked`.
- Do not add timestamps when creating the file. `scripts/execute.py` records `completed_at`, `failed_at`, and `blocked_at`.

Create `phases/{task-name}/index.json` for the task details:

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

Use these field rules:

- `project`: project name from `AGENTS.md`.
- `phase`: task name matching the directory name.
- `steps[].step`: zero-based step number.
- `steps[].name`: kebab-case slug.
- `steps[].status`: initially `pending`.
- Do not add `created_at` or step `started_at`; `scripts/execute.py` records them.

State transitions:

| Status | Fields | Writer |
| --- | --- | --- |
| `completed` | `completed_at`, `summary` | Codex writes `summary`; `execute.py` writes timestamp |
| `error` | `failed_at`, `error_message` | Codex writes message; `execute.py` writes timestamp |
| `blocked` | `blocked_at`, `blocked_reason` | Codex writes reason; `execute.py` writes timestamp |

The `summary` must be a one-line output summary useful for later steps, including created files and important decisions.

## Step File Template

Create one `phases/{task-name}/step{N}.md` file per step.

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

## Execution

Run the harness from the repository root:

```bash
python scripts/execute.py {task-name}
python scripts/execute.py {task-name} --push
```

`scripts/execute.py` handles:

- Creating or checking out `feat-{task-name}`.
- Injecting guardrails from `AGENTS.md` and `docs/*.md` into every step prompt.
- Passing completed step summaries into later step prompts.
- Retrying failed steps up to 3 times with the previous error message.
- Separating code changes (`feat`) and metadata changes (`chore`) into two commits.
- Recording `started_at`, `completed_at`, `failed_at`, and `blocked_at`.

## Recovery

For an `error` step, change that step's `status` back to `pending`, remove `error_message`, and rerun the harness.

For a `blocked` step, resolve the `blocked_reason`, change `status` back to `pending`, remove `blocked_reason`, and rerun the harness.
