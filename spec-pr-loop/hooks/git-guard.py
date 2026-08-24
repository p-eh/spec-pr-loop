#!/usr/bin/env python
"""
PreToolUse guard: block destructive git commands that silently discard
uncommitted work, and tell Claude to checkpoint / ask first.

Reads the hook payload JSON on stdin, inspects tool_input.command, and — if it
matches a data-losing git invocation — emits a PreToolUse "deny" decision.
Anything else is allowed (no output, exit 0).

Added 2026-07-06 after `git checkout -- character.json` reverted a file that
carried ~500 lines of uncommitted work. See memory/feedback_git_destructive_ops.
"""
import json
import re
import sys

# Only match a git invocation at COMMAND POSITION — start of the command, or
# right after a shell separator (newline, ; | & or a subshell/backtick). This
# deliberately does NOT match git phrases embedded in quoted strings such as a
# commit message (`-m "git reset --hard"`), an echo, or grep, which appear
# mid-token rather than at command position. `[ \t]*(?:sudo …)?(?:VAR=… )*`
# tolerates leading sudo / env assignments. Everything after git stays within
# one command segment via `[^|&;\n]*`, so compound commands
# ("cd x && git reset --hard") are still caught on the git segment.
_CMD = r"(?:^|[\n;&|`(])[ \t]*(?:sudo[ \t]+)?(?:[A-Za-z_]\w*=\S+[ \t]+)*git\b"
# Optional git global options (-C <dir>, -c <cfg>) that may sit between `git`
# and the subcommand. The destructive SUBCOMMAND must come right after these —
# so `git commit -m "...reset --hard..."` (subcommand=commit) never matches the
# reset rule, while `git reset --hard` and `git -c x=y reset --hard` do.
_SUB = _CMD + r"[ \t]+(?:-C[ \t]+\S+[ \t]+|-c[ \t]+\S+[ \t]+)*"

DESTRUCTIVE = [
    (re.compile(_SUB + r"reset\b[^|&;\n]*--hard"),
     "`git reset --hard` discards all uncommitted changes in tracked files."),
    (re.compile(_SUB + r"checkout\b[^|&;\n]*(?:\s--\s|\s--$|--force|\s-f\b)"),
     "`git checkout -- <path>` / `-f` overwrites the working copy, discarding uncommitted edits."),
    (re.compile(_SUB + r"checkout\b[^|&;\n]*\s\.(?:\s|$)"),
     "`git checkout .` discards all uncommitted changes in the current tree."),
    # `git checkout <path-looking-token>` without -b/-B (branch create) — the exact
    # shape that caused data loss. Heuristic: a token with a path sep or file ext.
    (re.compile(_SUB + r"checkout\b(?![^|&;\n]*\s-[bB]\b)[^|&;\n]*\s\S*(?:/|\.\w{1,5})(?:\s|$)"),
     "`git checkout <file>` discards uncommitted edits to that file."),
    (re.compile(_SUB + r"restore\b"),
     "`git restore` overwrites working-tree files, discarding uncommitted edits."),
    (re.compile(_SUB + r"clean\b[^|&;\n]*\s-[a-zA-Z]*f"),
     "`git clean -f` permanently deletes untracked files (including generated assets)."),
    (re.compile(_SUB + r"stash\b[^|&;\n]*\b(?:drop|clear)\b"),
     "`git stash drop/clear` permanently deletes stashed changes."),
]


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0  # can't parse -> don't interfere
    command = (payload.get("tool_input") or {}).get("command", "")
    if not isinstance(command, str) or not command:
        return 0

    for rx, why in DESTRUCTIVE:
        if rx.search(command):
            reason = (
                f"BLOCKED — {why}\n"
                "This can silently destroy the user's uncommitted work. Do NOT run it. "
                "Instead: (1) make a checkpoint first (WIP commit or `git stash`), "
                "(2) to undo only your own edits, revert them precisely rather than a "
                "blanket checkout/restore, and (3) ask the user before running any "
                "destructive git command against files that already have changes."
            )
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }))
            return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
