## Why

Agent Studio's `ux-ui-consolidation` (2026-10-24) sets up a UI guideline per project: a Controls section in `DESIGN.md` (or the file the project's `CLAUDE.md` names), a showcase of the controls, and checks in the test suite for what can be checked mechanically (raw colours, native tooltips, one-off button styles, inline font sizes). Its `design-guideline` skill has an audit mode for drift, run on request.

What tests can't see slips through review: a control used for the wrong job, a list's action in the wrong place, a new kind of control nobody agreed to. `finish-pr` already wraps up a PR and mines its review history for patterns worth a check, so it's the natural place to look at a PR's UI changes against the guideline.

## What Changes

Stub: the rough shape only, not designed yet.

- When a PR touches UI and the project has a guideline, `finish-pr` reviews the changed screens against it: the audit mode of `design-guideline`, limited to what the PR changes.
- Findings are listed like its other findings, for the user to pick from; a rule that keeps coming up is offered as a new check, as `finish-pr` already does for review patterns.

## Capabilities

### New Capabilities

None yet: stub only.

### Modified Capabilities

None yet.

## Impact

Not assessed yet. Open questions:

- **Detecting "touches UI":** by file paths the guideline names, by stack (styles, components), or by asking.
- **Without Agent Studio:** `design-guideline` ships in Agent Studio's bundled plugin. In a plain terminal session it isn't loaded; whether `finish-pr` then skips the review, or carries a minimal version of the audit itself.
- **Screenshots:** a review of the look needs the running UI; whether it uses `canvas_screenshot` when in Agent Studio, or reviews the code only.
