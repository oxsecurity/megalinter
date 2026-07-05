---
name: pr-watch-fix-renovate
description: Run the pr-watch-fix loop in parallel across every open Renovate-bot PR, each in its own git worktree. Use to green-light or triage all dependency-update PRs at once.
allowed-tools: Bash Agent AskUserQuestion Read
argument-hint: "[optional: specific PR numbers e.g. \"8313 7929\", or a max count]"
user-invocable: true
model: sonnet
---

Watch and fix CI for **all open Renovate-bot PRs at once** by fanning out one isolated git-worktree agent per PR. Each agent checks out its PR branch and runs the `/pr-watch-fix` loop independently, so many dependency-update PRs are driven to green (or triaged) in parallel.

This skill is a thin orchestrator. All per-PR intelligence — polling, log reading, fix/commit/push, bot-rebase handling, stop conditions — lives in `/pr-watch-fix`; do not reimplement it here.

Global git/PR rules (no AI attribution, commit-as-user, no pushes to `main`, no `--force`, stage by path) live in `CLAUDE.md` → **Git & PR Conventions**. Follow them.

## Step 0 — Preconditions

- `gh auth status` must succeed and the repo must be a GitHub repo. If not, **STOP** and tell the user.
- `git status --short` on the current working tree: uncommitted changes here are fine — the fan-out uses **separate worktrees**, so the main tree is never touched. Do not stash or reset it.

## Step 1 — Enumerate open Renovate PRs

Renovate authors PRs as `app/renovate` (this is distinct from `app/dependabot` — do **not** include dependabot).

```bash
gh pr list --author "app/renovate" --state open \
  --json number,title,headRefName,url,isDraft --limit 100 \
  | jq -r '.[] | select(.isDraft == false) | [.number, .headRefName, .title] | @tsv'
```

- If the list is empty → **STOP**. Report "No open Renovate PRs — nothing to do."
- If `$ARGUMENTS` names specific PR numbers, keep only those (and verify each is in the Renovate list; warn about any that aren't).
- If `$ARGUMENTS` is a bare integer, treat it as a **max count** (process the N most-recently-updated).

## Step 2 — Confirm scope

Show the user the numbered list you're about to process (number, branch, title — one line each).

- **≤ 6 PRs and no `$ARGUMENTS` filter**: proceed without asking.
- **> 6 PRs**: use `AskUserQuestion` to confirm before spawning that many long-running agents. Offer: "Process all N", "Process the newest 6", "Let me pick" (then take numbers), "Cancel". Each agent runs a 5-minute polling loop and consumes tokens — the user should opt into the scale.

## Step 3 — Fan out: one worktree agent per PR

Spawn **all** the agents in a **single message** (multiple `Agent` tool calls at once) so they run concurrently. For each PR use:

- `subagent_type`: `general-purpose`
- `isolation`: `"worktree"` — gives the agent an isolated checkout so parallel branch checkouts and pushes never collide
- `model`: `sonnet` — matches `/pr-watch-fix`'s own model; keep the orchestration cheap
- `description`: `"Renovate PR #<N> watch-fix"`

Prompt template (substitute `<N>`, `<BRANCH>`, `<TITLE>`):

```
You are running in an isolated git worktree. Drive CI for a single Renovate dependency-update PR to green, or triage it if stuck.

PR: #<N>  —  <TITLE>
Branch: <BRANCH>

Steps:
1. Check out the PR branch in this worktree:
     gh pr checkout <N>
   Then confirm with `git branch --show-current` — it must equal `<BRANCH>`.
   If checkout fails (branch deleted, PR closed/merged since enumeration), STOP and
   report "PR #<N>: gone (closed/merged/branch-deleted)". Do not guess.
2. Invoke the /pr-watch-fix skill and let it run its full loop for THIS branch.
   Do not open a new PR, do not switch branches, do not touch other PRs' branches.
3. Respect every stop condition in /pr-watch-fix: if it would ask the user a question
   (ambiguous fix, flaky external service, >3 fix cycles with no progress, someone
   else pushed non-bot commits), do NOT guess — STOP and return the question text so
   the orchestrator can surface it. An agent must never block waiting for interactive
   input; a stuck PR is a valid, reportable outcome.

Return EXACTLY ONE final line, no logs, in one of these shapes:
  PR #<N>: GREEN — <url>
  PR #<N>: STUCK — <one-line root cause / the question that needs the user> — <url>
  PR #<N>: GONE — closed/merged/branch-deleted
  PR #<N>: PUSHED, STILL RUNNING — <what you fixed, what's pending> — <url>
```

Notes:

- Each agent is autonomous and headless — it cannot prompt the user. That is why the prompt forces a *reportable* outcome instead of an interactive question. The orchestrator collects the questions and relays them.
- `gh pr checkout <N>` sets the branch to track the PR head; distinct Renovate PRs have distinct `renovate/*` branches, so no two worktrees contend for the same branch.
- Do **not** pass `subagent_type: "fork"` — a fresh `general-purpose` agent is far cheaper than forking full context into every PR, and `/pr-watch-fix` is self-contained.

## Step 4 — Aggregate and report

When all agents return, print a compact table — one row per PR — sorted by outcome (STUCK first, then PUSHED/RUNNING, then GREEN, then GONE):

```text
Renovate PR sweep — 8 PRs

STUCK    #7929  mypy v2         major bump: 4 type errors in server/ — needs your call — <url>
STUCK    #8150  graphql v17     peer-dep conflict, can't resolve cleanly — <url>
RUNNING  #8313  eslint-react    pushed lint fix, waiting on rebuild — <url>
GREEN    #8304  kubescape       — <url>
GREEN    #7693  golangci-lint   — <url>
GONE     #7711  secretlint v12  superseded/closed
```

Then, for each **STUCK** PR, surface the agent's question/root cause to the user in prose so they can decide. Do not silently drop stuck PRs.

If any PR is **PUSHED, STILL RUNNING**, tell the user they can re-run `/pr-watch-fix-renovate` (or `/pr-watch-fix` on that one branch) later to pick the loop back up.

## Step 5 — Worktree cleanup

The `Agent` tool auto-removes a worktree that ends unchanged. Worktrees where the agent committed locally but the push already landed on origin may linger. After reporting, list and prune stale sweep worktrees:

```bash
git worktree list
git worktree prune          # removes worktrees whose directory is already gone
```

Only remove a worktree once you've confirmed its work is pushed to origin (the agent's GREEN/RUNNING line implies a push). If unsure, leave it and tell the user which paths remain.

## Safety

- The only network-mutating action any agent performs is `git push` onto an **existing Renovate PR branch** (never `main`), via `/pr-watch-fix`'s own guarded push logic.
- Renovate branches are same-repo `renovate/*` branches, not forks — `gh pr checkout` is safe and needs no fork remote juggling.
- Never let this orchestrator edit code or push directly — all fixes go through the per-PR agents so each stays scoped to its own worktree and branch.
- If the same PR is already being watched by a running `/pr-watch-fix` Monitor in the main session, that's independent — the worktree agents run their own Monitors. Avoid launching this sweep twice concurrently for the same PR set.
