#!/usr/bin/env python3
"""Require test changes before production code edits."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


CODE_EXTENSIONS = {
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".go",
    ".h",
    ".hpp",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".py",
    ".rs",
    ".swift",
    ".ts",
    ".tsx",
}

NON_PRODUCT_ROOTS = {
    ".codex",
    ".github",
    ".gitlab",
    "docs",
    "phases",
    "reference",
}

TEST_DIR_NAMES = {
    "__tests__",
    "spec",
    "specs",
    "test",
    "tests",
    "e2e",
}

PATCH_FILE_RE = re.compile(r"^\*\*\* (?:Add|Update|Delete) File: (.+)$")


def _read_payload() -> dict[str, Any]:
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def _tool_command(payload: dict[str, Any]) -> str:
    tool_input = payload.get("tool_input")
    if isinstance(tool_input, dict):
        command = tool_input.get("command")
        if isinstance(command, str):
            return command
    return ""


def _changed_paths_from_patch(command: str) -> set[str]:
    paths: set[str] = set()
    for line in command.splitlines():
        match = PATCH_FILE_RE.match(line.strip())
        if match:
            paths.add(match.group(1).strip())
    return paths


def _parts(path: str) -> tuple[str, ...]:
    return tuple(part for part in Path(path.replace("\\", "/")).parts if part not in {"", "."})


def _is_test_path(path: str) -> bool:
    parts = _parts(path)
    lowered = [part.lower() for part in parts]
    name = lowered[-1] if lowered else ""
    stem = Path(name).stem

    return (
        any(part in TEST_DIR_NAMES for part in lowered)
        or name.startswith("test_")
        or stem.endswith("_test")
        or ".test." in name
        or ".spec." in name
    )


def _is_product_code_path(path: str) -> bool:
    parts = _parts(path)
    if not parts:
        return False

    first = parts[0].lower()
    if first in NON_PRODUCT_ROOTS:
        return False

    suffix = Path(parts[-1]).suffix.lower()
    return suffix in CODE_EXTENSIONS and not _is_test_path(path)


def _git_changed_paths(root: Path) -> set[str]:
    paths: set[str] = set()
    commands = [
        ["git", "diff", "--name-only"],
        ["git", "diff", "--cached", "--name-only"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    ]
    for command in commands:
        try:
            result = subprocess.run(
                command,
                cwd=root,
                capture_output=True,
                text=True,
                timeout=10,
            )
        except (OSError, subprocess.TimeoutExpired):
            continue
        if result.returncode == 0:
            paths.update(line.strip() for line in result.stdout.splitlines() if line.strip())
    return paths


def _cwd(payload: dict[str, Any]) -> Path:
    cwd = payload.get("cwd")
    return Path(cwd if isinstance(cwd, str) and cwd else os.getcwd())


def _deny(reason: str) -> int:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        },
    }))
    return 0


def main() -> int:
    payload = _read_payload()
    command = _tool_command(payload)
    changed_paths = _changed_paths_from_patch(command)
    if not changed_paths:
        return 0

    product_paths = sorted(path for path in changed_paths if _is_product_code_path(path))
    if not product_paths:
        return 0

    patch_has_tests = any(_is_test_path(path) for path in changed_paths)
    worktree_has_tests = any(_is_test_path(path) for path in _git_changed_paths(_cwd(payload)))
    if patch_has_tests or worktree_has_tests:
        return 0

    sample = ", ".join(product_paths[:3])
    if len(product_paths) > 3:
        sample += ", ..."
    return _deny(
        "TDD guard blocked production code changes without a test change. "
        f"Add or modify a test first, then retry. Production files: {sample}"
    )


if __name__ == "__main__":
    raise SystemExit(main())
