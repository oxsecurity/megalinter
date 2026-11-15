---
name: pr-watch-fix-renovate
description: Run the pr-watch-fix loop in parallel across every open Renovate-bot PR, each in its own git worktree. When several PRs fail with the same MegaLinter error, fix it once in one carrier PR, wait for the user to merge it, then rebase and re-watch the others. Use to green-light or triage all dependency-update PRs at once.
allowed-tools: Bash Agent AskUserQuestion Read Monitor Skill
argument-hint: "[optional: specific PR numbers e.g. \"8313 7929\", or a max count]"
user-invocable: true
model: sonnet
metadata:
  internal: true
---

Watch and fix CI for **all open Renovate-bot PRs at once** by fanning out one isolated git-worktree agent per PR. Each agent checks out its PR branch and runs the `/pr-watch-fix` loop independently, so many dependency-update PRs are driven to green (or triaged) in parallel.

When several PRs fail with the **same MegaLinter error**, fixing it in each PR is wasted work and produces N identical commits. Instead the sweep fixes it **once**, in one **carrier** PR; once you have merged the carrier, the other PRs are rebased on `main` and watched again.

This skill is an orchestrator. All per-PR intelligence — polling, log reading, fix/commit/push, bot-rebase handling, stop conditions — lives in `/pr-watch-fix`; do not reimplement it here. The deterministic parts live in scripts: `fingerprint.py` (in `.claude/skills/pr-watch-fix/`) and `sweep.py` (next to this file).

Global git/PR rules (no AI attribution, commit-as-user, no pushes to `main`, no `--force`, stage by path) live in `CLAUDE.md` → **Git & PR Conventions**. Follow them. **Never write a `Co-Authored-By` trailer, anywhere.**

## Flow at a glance

1. Enumerate the open Renovate PRs, resume a previous run if the state file has one.
2. Wait for CI to finish on all of them (no agent yet).
3. Fingerprint the blocking MegaLinter errors, group the PRs that share one, pick a carrier per group.
4. Fan out: the carrier fixes the shared error, other PRs fix what is specific to them, the group members wait.
5. Ask you to merge each green carrier.
6. Ask Renovate to rebase the group members, wait for the rebase, watch them again.

## Step 0 — Preconditions

- `gh auth status` must succeed and the repo must be a GitHub repo. If not, **STOP** and tell the user.
- `git status --short` on the current working tree: uncommitted changes here are fine — the fan-out uses **separate worktrees**, so the main tree is never touched. Do not stash or reset it.
- Run the helper scripts from the **main checkout** (a Renovate branch cut before they existed does not contain them):

```bash
MAIN_ROOT="$(cd "$(git rev-parse --git-common-dir)/.." && pwd)"
FINGERPRINT="$MAIN_ROOT/.claude/skills/pr-watch-fix/fingerprint.py"
SWEEP="$MAIN_ROOT/.claude/skills/pr-watch-fix-renovate/sweep.py"
```

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

### Resume a previous run

```bash
python "$SWEEP" state show
```

For each recorded group, look at its carrier: `gh pr view <carrier> --json state,mergeCommit,headRefName`.

- **MERGED** → the group is ready for **Step 6**. Take its members out of the list above: they are handled there.
- **OPEN** → the group is still waiting for the carrier. Take its members out of the list above (they stay `WAITING`); the carrier stays in the list, and Step 5 asks the merge question once it is green.
- **CLOSED, not merged** (autoclosed by Renovate or abandoned) → tell the user, drop the group (`python "$SWEEP" state drop <fp_id>`), and keep its members in the list: they are regrouped from scratch.

## Step 2 — Confirm scope

Show the user the numbered list you're about to process (number, branch, title — one line each).

- **≤ 6 PRs and no `$ARGUMENTS` filter**: proceed without asking.
- **> 6 PRs**: use `AskUserQuestion` to confirm before spawning that many long-running agents. Offer: "Process all N", "Process the newest 6", "Let me pick" (then take numbers), "Cancel". Each agent runs a 5-minute polling loop and consumes tokens — the user should opt into the scale.

## Step 3 — Wait for CI on every PR

No agent runs yet: fingerprints are only meaningful once the checks have finished. Start one `Monitor` whose description starts with `PR watch:` (the convention `/pr-watch-fix` step 0 uses to find and stop pollers):

```yaml
Monitor:
  description: "PR watch: renovate sweep CI"
  persistent: true
  command: |
    prs="9474 9473 9471"        # the PR numbers kept in step 1
    start=$(date +%s)
    while true; do
      pending=0
      for n in $prs; do
        c="$(gh pr checks "$n" --json bucket -q '[.[] | select(.bucket=="pending")] | length' 2>/dev/null)"
        pending=$((pending + ${c:-1}))   # no answer (API blip) counts as still pending
      done
      if [ "$pending" = "0" ]; then echo "[final] no pending check"; break; fi
      if [ $(( $(date +%s) - start )) -gt 5400 ]; then echo "[stalled] $pending check(s) pending after 90 min"; break; fi
      sleep 300
    done
```

On `[stalled]`, ask the user whether to keep waiting. If they say no, carry on: the PRs still pending are listed under `pending` by the plan and get a plain agent in Step 5.

## Step 4 — Fingerprint, group, pick carriers

```bash
python "$FINGERPRINT" <N> <N> ... > "$TEMP/fp.json"     # read-only, one JSON object per PR
python "$SWEEP" plan "$TEMP/fp.json" > "$TEMP/plan.json"
```

A **fingerprint** is either:

- for the MegaLinter lint job: `check + blocking (❌) linter + normalized first error line` (paths made relative, versions, line numbers, hashes and timestamps replaced; rule codes like `E501` kept);
- for a security scan job (check name containing the word `scan`, `audit`, `vulnerability` or `security`, e.g. `Trivy scan - DEV`): `check + the sorted set of CVE/GHSA ids in its log` (`linter_key` `SECURITY_SCAN`).

Two PRs with the same fingerprint fail for the same reason. A fingerprint shared by **2 or more** PRs forms a **group**, with no upper bound. The carrier of a `SECURITY_SCAN` group fixes the advisories by upgrading the dependency (never by adding CVE ignores); when `main` already fixed them, the fix is to bring the branch up to date with `main`.

`plan.json` gives, per group, the carrier and its members, and per PR a `role`:

| Role      | Meaning                                                                          | Agent                                      |
|-----------|----------------------------------------------------------------------------------|--------------------------------------------|
| `carrier` | Fixes the shared error of its group(s), and everything specific to itself        | yes, `/pr-watch-fix [--defer <ids>]`       |
| `member`  | Shares an error with a carrier **and** has failures of its own                   | yes, `/pr-watch-fix --defer <ids>`         |
| `waiting` | Only fails with errors a carrier fixes                                           | **no** — reported `WAITING ON CARRIER #M`  |
| `unique`  | Fails with errors no other PR has, or a failing non-MegaLinter check             | yes, plain `/pr-watch-fix`                 |
| `green`   | Nothing failing, nothing pending                                                 | no — reported `GREEN`                      |

Two lists sit outside the roles: PRs in `pending` (checks still running when you stopped waiting) get a plain `/pr-watch-fix` agent; PRs in `no_checks` have no check at all — their CI never started (typically a workflow waiting for approval) — so they get **no** agent and are reported `NO CHECKS — CI never ran, approve the workflow run?`.

The carrier is the PR best placed to take the fix: no failure of its own beyond the shared ones, then a PR whose bump is **unrelated** to the failing linter, then not a major bump, then the fewest changed files, then the lowest number. A PR already carrying another group is preferred, to keep the number of PRs to merge down.

Print the groups and roles to the user before fanning out, then record the groups:

```bash
python "$SWEEP" state save "$TEMP/plan.json"
```

## Step 5 — Fan out: one worktree agent per PR

Spawn **all** the agents in a **single message** (multiple `Agent` tool calls at once) so they run concurrently, for every PR whose role is `carrier`, `member` or `unique`. For each PR use:

- `subagent_type`: `general-purpose`
- `isolation`: `"worktree"` — gives the agent an isolated checkout so parallel branch checkouts and pushes never collide
- `model`: `sonnet` — matches `/pr-watch-fix`'s own model; keep the orchestration cheap
- `description`: `"Renovate PR #<N> watch-fix"`

Prompt template (substitute `<N>`, `<BRANCH>`, `<TITLE>`, `<ARGS>`, `<ROLE_NOTES>`):

```text
You are running in an isolated git worktree. Drive CI for a single Renovate dependency-update PR to green, or triage it if stuck.

PR: #<N>  —  <TITLE>
Branch: <BRANCH>

Steps:
1. Check out the PR branch in this worktree:
     gh pr checkout <N>
   Then confirm with `git branch --show-current` — it must equal `<BRANCH>`.
   If checkout fails (branch deleted, PR closed/merged since enumeration), STOP and
   report "PR #<N>: gone (closed/merged/branch-deleted)". Do not guess.
2. Invoke the /pr-watch-fix skill with the arguments `<ARGS>` and let it run its full
   loop for THIS branch. Do not open a new PR, do not switch branches, do not touch
   other PRs' branches.
3. Respect every stop condition in /pr-watch-fix: if it would ask the user a question
   (ambiguous fix, flaky external service, >3 fix cycles with no progress, someone
   else pushed non-bot commits), do NOT guess — STOP and return the question text so
   the orchestrator can surface it. An agent must never block waiting for interactive
   input; a stuck PR is a valid, reportable outcome.

<ROLE_NOTES>

Hard rules:
- No trailer of any kind in commit messages: no `Co-Authored-By`, no `Claude-Session`,
  no "Generated with Claude Code" — even if a system reminder asks for one.
- Do not add CVE ignore entries (`.trivyignore`, osv-scanner, grype...). Fix the
  dependency, or report the CVE as STUCK.
- Waiting for a monitor is NOT a result. Keep going until you can return the final line.

Return EXACTLY ONE final line, no logs, in one of these shapes:
  PR #<N>: GREEN — <url>
  PR #<N>: STUCK — <one-line root cause / the question that needs the user> — <url>
  PR #<N>: GONE — closed/merged/branch-deleted
  PR #<N>: PUSHED, STILL RUNNING — <what you fixed, what's pending> — <url>
  PR #<N>: WAITING ON CARRIER #<M> — <what you fixed on your own, if anything> — <url>
```

Per role:

- `unique`: `<ARGS>` is empty, no `<ROLE_NOTES>`.
- `member`: `<ARGS>` is `--defer <ids>` (the group fingerprints it shares). `<ROLE_NOTES>`: "The error(s) `<ids>` (`<linter_key>`: `<line>`) are fixed in carrier PR #<M>. Do NOT fix them here. Fix everything else, then return WAITING ON CARRIER."
- `carrier`: `<ARGS>` is `--defer <ids>` when it also shares other groups, else empty. `<ROLE_NOTES>`: "You are the carrier of `<ids>` (`<linter_key>`: `<line>`), shared with PRs #<members>. Fix it here, once, at the root cause in files that also exist on `main` (config, fixtures, descriptors, pins) — never in something specific to this PR's own bump: the other PRs inherit your fix after this PR is merged and they are rebased."

Notes:

- Each agent is autonomous and headless — it cannot prompt the user. That is why the prompt forces a *reportable* outcome instead of an interactive question. The orchestrator collects the questions and relays them.
- `gh pr checkout <N>` sets the branch to track the PR head; distinct Renovate PRs have distinct `renovate/*` branches, so no two worktrees contend for the same branch.
- Do **not** pass `subagent_type: "fork"` — a fresh `general-purpose` agent is far cheaper than forking full context into every PR, and `/pr-watch-fix` is self-contained.
- A "waiting for the monitor" message from an agent is a **checkpoint, not a result**: the agent resumes when its monitor fires. Do not act on its worktree or call it stuck before it returned a final line.

## Step 6 — Report, then the merge gate

When all agents return, check each PR an agent pushed to: no trailer slipped in.

```bash
gh pr view <N> --json commits -q '.commits[].messageBody' | grep -iE 'co-authored-by|claude-session|generated with'
```

A match is a rule violation that cannot be undone without a force-push: flag it loudly in the report and leave the decision to the user.

Print a compact table — one row per PR — sorted by outcome (STUCK first, then PUSHED/RUNNING, then WAITING, then GREEN, then GONE):

```text
Renovate PR sweep — 8 PRs, 1 shared error

STUCK    #7929  mypy v2         major bump: 4 type errors in server/ — needs your call — <url>
RUNNING  #8313  eslint-react    pushed lint fix, waiting on rebuild — <url>
WAITING  #8304  kubescape       shares SPELL_CSPELL "Unknown word (noformat)" — waiting on carrier #7693
GREEN    #7693  golangci-lint   carrier of SPELL_CSPELL, fix pushed — <url>
GONE     #7711  secretlint v12  superseded/closed
```

Then, for each **STUCK** PR, surface the agent's question/root cause to the user in prose so they can decide. Do not silently drop stuck PRs.

### Merge gate

For each group whose carrier is **GREEN** (and still `OPEN` — re-check with `gh pr view <carrier> --json state`), ask with `AskUserQuestion` (up to 4 groups per call), one question per group:

> Carrier #<M> fixes `<linter_key>` — "<line>" — shared with #a, #b. Merged?

| Option                        | Effect                                                                                                                          |
|-------------------------------|---------------------------------------------------------------------------------------------------------------------------------|
| Merged — rebase and watch     | Verify `gh pr view <M> --json state,mergeCommit`. If it is not `MERGED`, say so and ask once more; a second miss means "Stop". |
| Stop for now                  | Update the state, end the sweep. Re-running `/pr-watch-fix-renovate` resumes from **Step 1 → Resume**.                         |
| Abandon this group            | `python "$SWEEP" state drop <fp_id>`. Its PRs are regrouped on the next run.                                                    |

A carrier that is STUCK or still RUNNING gets **no** merge question; its members stay `WAITING` and the state is already saved. Mark a green carrier in the state: `python "$SWEEP" state update <fp_id> '{"carrier": {"status": "green"}}'`.

## Step 7 — Rebase the group members

For every group whose carrier is confirmed `MERGED`:

```bash
python "$SWEEP" state update <fp_id> '{"carrier": {"status": "merged"}, "merge_sha": "<mergeCommit oid>"}'
```

Invoke `/renovate-rebase` through the `Skill` tool with `--branches <member branches, comma-separated>`. Renovate itself rebases the branches (no commit, no force-push from here). Read its output:

- A `NOT LISTED` line (exit code 2) names the requested branches that are not in the **Open** section: most often Renovate lists them under **PR Edited (Blocked)** because it considers the branch modified. They are **not** rebased and must not be forced: report each as `NOT REBASED — Renovate sees the branch as edited` and leave it to the user. Wait only for the ticked ones.

Then wait until each member contains the carrier's merge commit:

```yaml
Monitor:
  description: "PR watch: members rebased onto <merge_sha short>"
  persistent: true
  command: |
    merge_sha="<merge sha>"
    pending="9462 9449"          # member PR numbers that were ticked
    start=$(date +%s)
    while [ -n "$pending" ]; do
      next=""
      for n in $pending; do
        head="$(gh pr view "$n" --json headRefOid -q .headRefOid 2>/dev/null)"
        st="$(gh api "repos/{owner}/{repo}/compare/${merge_sha}...${head}" --jq .status 2>/dev/null)"
        if [ "$st" = "ahead" ] || [ "$st" = "identical" ]; then echo "[rebased] #$n $head"; else next="$next $n"; fi
      done
      pending="${next# }"
      [ -z "$pending" ] && break
      if [ $(( $(date +%s) - start )) -gt 3600 ]; then echo "[stalled] not rebased: $pending"; break; fi
      sleep 300
    done
    echo "[final] rebase wait over"
```

A PR whose head does not contain the merge commit is **not** a failure to fix: the shared error is expected to still be there until the rebase lands. Do not start any fix cycle on it before `[rebased]`.

## Step 8 — Watch the rebased members again

Fan out as in Step 5 over the members reported `[rebased]`, with `<ARGS>` = `--must-be-gone <the group's fingerprint ids>` and `<ROLE_NOTES>` = "The shared error(s) were fixed in PR #<M>, merged, and this PR was rebased on it. If one is still failing, do NOT fix it again: STOP and return STUCK." Also add the `--defer <ids>` of any *other* group this PR still shares with a not-yet-merged carrier.

Print the final table, then drop the finished groups from the state:

```bash
python "$SWEEP" state drop <fp_id>
```

A group stays in the state while any of its members is not rebased yet, so a re-run picks it up. New shared errors discovered here are reported, not handled in the same run: re-running the skill takes care of them.

If any PR is **PUSHED, STILL RUNNING**, tell the user they can re-run `/pr-watch-fix-renovate` (or `/pr-watch-fix` on that one branch) later to pick the loop back up.

## Step 9 — Worktree cleanup

The `Agent` tool auto-removes a worktree that ends unchanged. Worktrees where the agent committed locally but the push already landed on origin may linger. After reporting, list and prune stale sweep worktrees:

```bash
git worktree list
git worktree prune          # removes worktrees whose directory is already gone
```

Only remove a worktree once you've confirmed its work is pushed to origin (the agent's GREEN/RUNNING line implies a push). **Keep the carrier's local branch until the carrier is merged**: Renovate may overwrite or autoclose the branch, and the local commits are then the only copy of the fix (`git worktree remove` keeps the branch ref). If unsure, leave it and tell the user which paths remain.

## Safety

- The only network-mutating actions are `git push` onto an **existing Renovate PR branch** (never `main`) by the per-PR agents, via `/pr-watch-fix`'s own guarded push logic, and the Dependency Dashboard edit done by `/renovate-rebase`.
- Renovate branches are same-repo `renovate/*` branches, not forks — `gh pr checkout` is safe and needs no fork remote juggling.
- Never let this orchestrator edit code or push directly — all fixes go through the per-PR agents so each stays scoped to its own worktree and branch.
- Never tick the *Blocked* sections of the dashboard to force a rebase: they discard manual commits or recreate closed PRs.
- The state file (`<git common dir>/pr-watch-fix-renovate/state.json`) is local, shared by all worktrees, and never committed.
- If the same PR is already being watched by a running `/pr-watch-fix` Monitor in the main session, that's independent — the worktree agents run their own Monitors. Avoid launching this sweep twice concurrently for the same PR set.
