---
name: spec-interview
description: Turn a flat one-paragraph scope statement into a staged interview, then a real OpenSpec proposal. Use when the user hands you a rough one-paragraph ask ("spec this out", "turn this into a proposal") instead of a ready-made spec.
category: Workflow
tags: [openspec, spec-driven]
---

Turn a flat, one-paragraph scope statement into a full OpenSpec change
proposal, via a staged interview — never by writing the spec by hand, and
never by dumping all clarifying questions in one message.

**Input**: `$ARGUMENTS` is the flat scope paragraph (a few sentences, not a
spec).

## Scope guard

Operate only on the OpenSpec tree closest to the current working directory
(the nearest ancestor `openspec/` — resolve it the same way `openspec status`
does). If the repo has multiple independent OpenSpec trees (e.g. a subproject
with its own `openspec/`, separate from the repo root's), ask which one this
proposal belongs to before proceeding rather than guessing.

## Step 1 — Staged interview (STRICT: one question-group per turn)

Ask the groups below **in order, one group per message**. Each group is 2-4
related questions max. Wait for the user's reply before asking the next group
— never combine groups, never skip one even if `$ARGUMENTS` already seems to
answer it (confirm briefly instead of assuming).

1. **Scope & boundaries**
   - What's explicitly in scope? What's explicitly out of scope?
   - Which existing systems/files does this touch?

2. **Edge cases**
   - What are the 2-3 edge cases most likely to break this?
   - Any known-tricky interaction with an existing subsystem (a state
     machine, a shared config object, a fixed-timestep loop, a migration in
     flight)?

3. **Acceptance criteria**
   - What observable behavior proves this is done?
   - Any new config/tuning values this needs?

4. **Project-specific constraints** (read the nearest `CLAUDE.md` first, if
   one exists, for anything this repo calls out — a planned migration, a
   portability target, a stack constraint)
   - Does this design assume anything about the current stack/approach that
     would NOT survive a known planned change (e.g. an engine swap, a
     framework migration, a vendor cutover)?
   - **Always produce an explicit constraints/portability flags list** in the
     final proposal, even if the user says "don't worry about it yet" or
     "nothing" — write "none identified" rather than omitting the section.

## Step 2 — Synthesize (before touching OpenSpec)

After all four groups are answered, synthesize the answers into this 5-part
skeleton and present it back to the user as a single reviewable block:

1. **Current state**
2. **Desired behavior**
3. **Technical rationale**
4. **Scope guards**
5. **Acceptance criteria**

(plus the constraints/portability flags list from step 1.4, always present.)

Ask for explicit go/no-go on this synthesis. **Do not proceed to step 3 until
the user confirms.** If they want changes, revise and re-present — do not
silently patch and move on.

## Step 3 — Generate the real OpenSpec proposal

Only after confirmation:

1. Derive a kebab-case change name from the synthesis (e.g. "add whistle
   command" → `add-whistle-command`).
2. `openspec new change "<name>"`
3. Follow the same artifact-creation loop as `openspec-propose`:
   - `openspec status --change "<name>" --json` to get the required artifact
     set and dependency order
   - For each artifact, `openspec instructions <artifact-id> --change "<name>" --json`
     for its `template`/`instruction`/`rules`
   - Write `proposal.md` from the step-2 synthesis directly (current state /
     desired behavior / technical rationale — this is the `why` and `what`),
     fold scope guards + acceptance criteria + constraints/portability flags
     into the appropriate artifacts per each artifact's `template`
   - Re-run `status --json` after each artifact until the required set is
     `done`/`skipped`
4. Show final `openspec status --change "<name>"` and summarize what was
   created, same output shape as `openspec-propose`.

## Rules

- Never ask more than one question-group per turn.
- Never call `openspec new change` before the user has confirmed the 5-part
  synthesis.
- Always include the constraints/portability flags section in the final
  proposal, even when empty — write "none identified", never omit it.
- Never touch a different OpenSpec tree than the one confirmed in the scope
  guard.
