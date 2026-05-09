---
name: project-review
description: Project-specific review workflow for checking local changes against this repository's architecture, ADR technology choices, tests, AGENTS.md CRITICAL rules, and build health. Use when Codex is asked to review current changes, validate a harness step, check implementation quality, or report violations before committing or continuing work.
---

# Project Review

Review this project's changes against the repository rules and implementation documents. Lead with concrete findings and file references when there are problems.

## Required Context

Read these files before reviewing:

- `/AGENTS.md`
- `/docs/ARCHITECTURE.md`
- `/docs/ADR.md`

Also inspect the changed files using `git status`, `git diff`, and targeted file reads.

## Checklist

Verify these items:

1. Architecture compliance: changed files follow the directory structure and boundaries in `ARCHITECTURE.md`.
2. Technology stack compliance: implementation stays within the technology choices in `ADR.md`.
3. Test coverage: new functionality has relevant tests.
4. CRITICAL rules: no rule in `AGENTS.md` marked CRITICAL is violated.
5. Build health: the documented build and test commands pass, or any inability to run them is reported clearly.

## Commands

Prefer the commands defined by this repository. If package scripts do not exist, use the closest available project-specific validation command and report the substitution.

```bash
npm run build
npm test
```

## Output

If issues are found, list findings first in severity order with file and line references. Then provide this checklist table:

| Item | Result | Notes |
| --- | --- | --- |
| Architecture compliance | PASS/FAIL | {details} |
| Technology stack compliance | PASS/FAIL | {details} |
| Test coverage | PASS/FAIL | {details} |
| CRITICAL rules | PASS/FAIL | {details} |
| Build health | PASS/FAIL | {details} |

For each violation, propose a concrete fix. If no issues are found, state that clearly and mention any tests or checks that were not run.
