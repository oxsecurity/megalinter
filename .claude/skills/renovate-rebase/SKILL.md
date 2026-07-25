---
name: renovate-rebase
description: Tick the Renovate "Dependency Dashboard" issue checkboxes (Rate-Limited + Open sections) to force creation of rate-limited PRs and rebase of all open Renovate PRs. Runs autonomously, no confirmation.
allowed-tools: Bash Read
argument-hint: "[optional: sections e.g. \"open\" or \"rate-limited\", plus --individual / --trigger-run]"
user-invocable: true
model: sonnet
---

Force Renovate to act now: find the **Dependency Dashboard** GitHub issue and tick its checkboxes in the **Rate-Limited** and **Open** sections. Renovate watches its own dashboard issue body — a ticked box is an instruction:

- **Rate-Limited** → create the PRs that `prHourlyLimit` / `prConcurrentLimit` is holding back
- **Open** → retry/rebase every already-created Renovate PR against the current `main`

**Run this skill straight through to the end without asking the user anything.** No confirmation prompts, no `AskUserQuestion`, no pausing to show a preview — invoking the skill *is* the authorization. Ticking these boxes is exactly the intended effect, including when it rebases every open Renovate PR and re-triggers their CI.

All the mechanics live in `.claude/skills/renovate-rebase/tick_dashboard.py`. Do not hand-edit the issue body from the model — the body is ~2000 lines and a manual rewrite risks corrupting the Detected Dependencies section.

## Step 1 — Tick the checkboxes

```bash
python .claude/skills/renovate-rebase/tick_dashboard.py
```

That single command finds the dashboard issue (open issue titled `Dependency Dashboard`, authored by `app/renovate`), ticks one aggregate checkbox per targeted section, and pushes the new body back with `gh issue edit`:

- Open → `<!-- rebase-all-open-prs -->` *Click on this checkbox to rebase all open PRs at once*
- Rate-Limited → `<!-- create-all-rate-limited-prs -->` *…force the creation of all rate-limited PRs at once*

One aggregate box has the same effect as ticking every line individually, with a far smaller diff on the issue. It is the default — keep it unless the user asked for something else.

Pass extra flags only when `$ARGUMENTS` asks for something narrower or wider:

| Flag | Effect |
| --- | --- |
| `--sections open` | only that section (comma-separated; `rate-limited,open` is the default) |
| `--individual` | tick every PR line instead of the section's "all at once" box — use when the user wants specific PRs, or when Renovate rendered no aggregate box |
| `--trigger-run` | also tick `<!-- manual job -->` ("run Renovate again on this repository") so the queued requests are picked up on the next poll instead of the next schedule |
| `--issue N` / `--title "..."` | when `renovate.json` overrides `dependencyDashboardTitle` or several dashboards match |
| `--repo owner/name` | act on another repo (defaults to the current one) |
| `--dry-run` | preview only — **only** when the user explicitly asks for a preview |

The script is self-contained and never prompts. Read its output and keep going:

- `SECTION ABSENT` for **rate-limited** is normal, not an error — Renovate only renders that section while it is actually holding PRs back. Carry on with **open**.
- `no unticked checkbox` means the request is already pending from an earlier run. Nothing more to do for that section; continue to verification.
- `Nothing changed` means every targeted request was already pending. Report that and stop — do not retry or escalate to `--individual`.

If `gh` is not authenticated the script exits with the `gh` error; report that and stop, since nothing else in the skill can proceed.

Other sections exist (`Pending Status Checks`, `Awaiting Schedule`, `PR Edited (Blocked)`, `PR Closed (Blocked)`). Only pass them in `--sections` if the user explicitly asks — the *Blocked* ones **discard commits / recreate closed PRs**, which is destructive.

## Step 2 — Verify

```bash
gh pr list --author "app/renovate" --state open --json number,title,updatedAt --limit 100
```

Two valid outcomes on the issue itself, both success:

- boxes still show `[x]` → Renovate hasn't polled yet (typically a few minutes on the hosted Mend app)
- boxes are back to `[ ]` → **Renovate already processed the request and unticked them.** This is the expected end state, not a lost edit.

So verify against the PR list rather than the checkbox state: fresh `updatedAt` timestamps and new PR numbers mean the rebases and rate-limited creations landed. Run the command once — do not poll in a loop waiting for Renovate.

## Step 3 — Report

Tell the user, in a few lines: the issue number, which sections were ticked and how many boxes, how many open Renovate PRs will be rebased, and that Renovate acts on its next run (minutes, not instant). If those PRs then need their CI driven to green, point at `/pr-watch-fix-renovate`.

## Safety

- The only mutation is an **edit to the Renovate dashboard issue body**. No branch, no push, no PR is touched by this skill directly — Renovate itself performs the force-pushes on its own `renovate/*` branches. That is why it is safe to run unattended.
- Never rewrite the issue body by hand or with a broad `sed`; the "Detected Dependencies" block is thousands of lines and must round-trip untouched. The script only flips `- [ ]` → `- [x]` inside the targeted sections.
- Never tick `PR Closed (Blocked)` (recreates PRs the maintainers deliberately closed) or `PR Edited (Blocked)` (**discards manual commits** on those branches) without an explicit request from the user.
- Run the tick command once per invocation. Renovate needs minutes to process; re-ticking mid-flight just churns CI.
