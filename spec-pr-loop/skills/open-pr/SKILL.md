---
name: open-pr
description: Push the current worktree branch and open a PR once a scoped unit of work (an OpenSpec capability/section, or whatever boundary the user names) is implemented and committed. Use when openspec-apply-change reports a section/capability fully done, or the user says "open the PR" / "ship this". Always confirms before pushing or creating anything.
category: Workflow
tags: [openspec, pr, worktree]
---

Closes the gap between `openspec-apply-change` finishing a scoped unit of
work and a PR actually existing for `pr-comment-triage`/`finish-pr` to act
on. Nothing in this workflow pushes or opens a PR silently — this skill
always proposes, then waits for explicit confirmation, before doing anything
that touches the remote.

## When this runs

- `openspec-apply-change` just reported all tasks in a section/capability
  boundary complete (not necessarily the whole change — see worktree-per-PR
  below).
- The user explicitly asks to open/ship a PR for the current worktree.

Never trigger on a partially-done section. If it's unclear whether the
current uncommitted/committed work is meant to be one PR's worth, ask rather
than assume.

## Steps

1. **Confirm scope.** State what this PR would cover (which tasks/section,
   or — if the project doesn't define capability boundaries — ask the user
   what scope this PR should be). One PR per capability/section is the
   default; don't bundle unrelated sections into one branch, and don't split
   a single small section into multiple PRs either.

2. **Check the worktree is clean and committed.**
   - `git status` — if there are uncommitted changes, stop and ask whether to
     commit them first (don't commit on the user's behalf without asking what
     the message should say, unless they've already told you their commit
     message conventions).
   - Confirm the branch actually diverges from the PR's target branch
     (`git log <target>..HEAD --oneline`) — an empty diff means there's
     nothing to open a PR for.

3. **Propose, then wait for confirmation.** Show:
   - Branch name and target branch
   - Commit list that would be included
   - Draft PR title and body (title: the section/capability name; body:
     summary drawn from the change's `proposal.md`/spec delta if the project
     uses OpenSpec, otherwise from the commit list)

   Do not push or create anything until the user confirms.

4. **On confirmation:**
   ```bash
   git push -u origin <branch>
   gh pr create --title "<title>" --body "<body>" --base <target>
   ```
   Report the PR URL.

5. **Do not merge.** Opening the PR is the end of this skill's job — review,
   comment-triage (`pr-comment-triage`), and the wrap-up audit (`finish-pr`)
   happen after, and merging is always the user's explicit call, never
   automatic.

## Guardrails

- Never push or run `gh pr create` without the user having confirmed the
  scope, branch, and draft title/body in that same turn.
- Never commit on the user's behalf to "clean up" the worktree before
  pushing — surface uncommitted changes and ask.
- Never bundle multiple unrelated sections/capabilities into one PR, and
  never split one coherent unit of work across multiple PRs, without the
  user asking for that explicitly.
- If the target branch can't be determined confidently (no obvious base,
  ambiguous remote), ask rather than guess.
