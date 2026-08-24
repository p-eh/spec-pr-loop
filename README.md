# spec-pr-loop

A Claude Code plugin marketplace with one plugin, `spec-pr-loop`: a
spec-driven, PR-review-iteration workflow — propose a change as an OpenSpec
artifact set, implement it task by task, ship it as a worktree-per-PR, and
iterate through review comments to a clean merge. Pure workflow, no project
domain content.

## Install (per repo)

```
claude plugin marketplace add F:/dev/spec-pr-loop
claude plugin install spec-pr-loop
```

## What's inside

**OpenSpec bundle** (`skills/openspec-*`, `commands/opsx/*.md`) — the stock
propose / apply / update / sync / archive / explore skill set plus
`openspec-stub` for proposal-only deferred ideas. Requires the `openspec` CLI.

**PR lifecycle** — three skills, three different points in the loop:
- `open-pr` — closes the gap between a section/capability being fully
  implemented and a PR existing for review. Confirms scope, checks the
  worktree is clean and committed, proposes branch/title/body, and only
  pushes + runs `gh pr create` after explicit confirmation. Never merges.
- `pr-comment-triage` — works unresolved PR review comments one at a time,
  *during* review.
- `finish-pr` — wrap-up audit run *after* comments are addressed: checks
  GitHub thread-resolution status via GraphQL (a reply is not the same as a
  resolved thread), checks OpenSpec completion/archive status, runs the
  project's own guard checks (lint/tests/drift checks), and mines the full
  review history for 3+ occurrence patterns worth automating or documenting.
  Never resolves threads or merges — reports and lets the user decide.

Pairs with the **worktree-per-PR** convention: each unit of work (an OpenSpec
change section, a capability boundary) gets its own worktree/branch, pushed
as its own PR against the main branch.

**`git-guard.py`** (`hooks/`) — PreToolUse hook, wired via `hooks/hooks.json`.
Blocks destructive git commands (`reset --hard`, `checkout -f`/`checkout .`/
`checkout <path>`, `restore`, `clean -f`, `stash drop/clear`) matched at
command position (won't false-positive on a commit message that happens to
contain the words). Denies and tells Claude to checkpoint first.

**`spec-interview`** (`skills/`) — turns a flat one-paragraph ask into an
OpenSpec proposal via a strict staged interview (one question-group per
turn: scope, edge cases, acceptance criteria, project-specific constraints),
then a synthesis the user must explicitly confirm before `openspec new
change` runs. Reads the nearest `CLAUDE.md` for project constraints rather
than assuming a specific stack.

**Templates** (`spec-pr-loop/templates/`) — copy into a new repo, don't
symlink (each repo should be free to diverge intentionally):
- `gitignore.template` — merged common core (`.env`, `__pycache__/`,
  `node_modules/`, `.claude/settings.local.json`, etc.) plus commented
  examples of two useful patterns: allowlisting a specific committed sample
  file inside an otherwise-ignored data directory, and ignoring generated
  binary assets by extension while keeping hand-authored companion files.
- `pre-commit-config.template.yaml` — lint/format on every commit via
  `language: system` (avoids a Windows long-path issue some pre-commit
  managed envs hit). Chosen over a Claude-side PostToolUse lint hook because
  it fires on every commit regardless of what made the edit, not just
  Claude's own Write/Edit calls.

## Deliberately excluded

- An archive-notify hook that bridges completed OpenSpec changes into an
  Obsidian wiki vault — specific to that setup, not general workflow.
- An idea-capture command that routes raw ideas into hardcoded category
  files — not reusable as-is and not clearly wanted.
