---
name: pr-watch-fix
description: Watch the GitHub PR for the current branch, wait for CI to finish, and autonomously fix failing jobs by reading logs, editing sources, and pushing. Stops cleanly when stuck.
allowed-tools: Bash Read Grep Glob Edit Write AskUserQuestion
user-invocable: true
---

Watch the open PR for the current branch, wait for CI, and fix failures.

## Loop

Repeat until the PR is fully green or you stop intentionally:

### 0. Stop any prior PR-watch Monitor

Before doing anything else, cancel a previous run's still-running poller. Re-invoking `/pr-watch-fix` always wins — the new run resets state.

Use `TaskList` to find Monitors whose description starts with `PR watch:` (the convention used by step 3) and call `TaskStop` on each. Do not stop tasks that don't start with this prefix — they belong to other work.

### 1. Find the PR

```bash
BRANCH="$(git branch --show-current)"
PR_JSON="$(gh pr list --head "$BRANCH" --state open --json number,url,headRefOid --limit 1)"
PR_NUMBER="$(printf '%s' "$PR_JSON" | jq -r '.[0].number // empty')"
```

- If `PR_NUMBER` is empty → **STOP**. Tell the user there is no open PR for the branch.
- Save the PR URL for reporting and the `headRefOid` so you can detect when a new push lands.

### 2. Inspect CI state

```bash
gh pr checks "$PR_NUMBER" --json name,bucket,state,workflow,link
```

Classify each check by `bucket`/`state`:

- `pass` → success
- `fail`, `cancel`, `skipping` → failure (treat `skipping` as success if the user wants — default: only `fail` and `cancel` count as failures)
- `pending`, `in_progress`, `queued`, `waiting`, `requested` → still running

Decide:

- **All `pass`** → **STOP**. Report success and the PR URL.
- **Any failure** → go to step 4 (fix).
- **No failure but some running** → go to step 3 (wait).

### 3. Wait for running jobs

Poll every **5 minutes**, fixed interval. No backoff — the user explicitly wants a 5-minute cadence so failures surface fast. Use a persistent `Monitor` with a description that starts with `PR watch:` so step 0 of a future invocation can find and stop it.

Example:

```
Monitor:
  description: "PR watch: PR #7790 CI"
  persistent: true
  command: |
    while true; do
      state="$(gh pr checks 7790 --json name,bucket 2>/dev/null || echo '[]')"
      counts="$(jq -r '[.[] | .bucket] | group_by(.) | map("\(.[0])=\(length)") | join(" ")' <<<"$state")"
      pending="$(jq -r '[.[] | select(.bucket=="pending")] | length' <<<"$state")"
      fail_now="$(jq -r '[.[] | select(.bucket=="fail" or .bucket=="cancel") | .name] | sort | join(",")' <<<"$state")"

      # Emit on new failures
      if [ -n "$fail_now" ] && [ "$fail_now" != "${prev_fail:-}" ]; then
        echo "[failures] $fail_now ($counts)"
        prev_fail="$fail_now"
      fi

      # Done condition: nothing pending
      if [ "$pending" = "0" ]; then
        echo "[final] $counts"
        break
      fi
      sleep 300
    done
```

The monitor emits notifications only on state changes (new failures or completion). It does not emit a notification every 5 minutes — that would be noise. If the user wants a heartbeat, they can ask.

If the same check has been pending for more than **90 minutes total** without a state change, the monitor must emit a `[stalled]` event and the agent should **ask the user** whether to keep waiting.

Do not poll faster than 5 minutes — it wastes API quota and produces no signal.

### 4. Collect logs from failing jobs

For each failing check, get its run + job IDs:

```bash
RUN_ID="$(gh pr checks "$PR_NUMBER" --json name,bucket,link \
  | jq -r '.[] | select(.bucket=="fail") | .link' \
  | sed 's|.*/runs/||; s|/job/.*||' | head -1)"
gh run view "$RUN_ID" --log-failed > /tmp/pr-watch-fail.log
```

Then read the tail of `/tmp/pr-watch-fail.log` and grep for the first concrete error (compiler error, test assertion, lint rule, missing file). Don't read the whole log if it's huge — find the actionable line.

If multiple jobs fail with **different** errors, handle them in this order: build failures → test failures → lint failures → flaky/intermittent. Group jobs that fail with the **same** error and treat them as one fix.

### 5. Decide if you can fix it

Apply the **"can I fix this cleanly?"** test before editing:

- Is the cause clear from the log? (compile error with file/line, test assertion with expected/actual, lint rule with location)
- Is the fix local to one or two files?
- Is the fix one of the standard MegaLinter patterns? (descriptor edit + `make megalinter-build`, fixture content, Python typo, Dockerfile pin)
- Have you already attempted this same fix and seen it fail? (track attempts in your task list — if the same error returns after a push, that's a strong signal you don't understand it)

If **any** answer is "no", **ASK THE USER** via `AskUserQuestion` instead of guessing:

- Show the failing job name, the key error line, and your hypothesis
- Offer 2-3 options when there are real alternatives
- Offer "stop and let me investigate" as an option when the cause is ambiguous

Specifically **STOP and ask** when:

- The error mentions an external service outage, rate limit, registry timeout, or "resource temporarily unavailable" (likely flake — pushing won't help)
- The same error appears after your previous fix push (your model of the bug is wrong)
- The fix would touch generated files (`linters/*/Dockerfile`, `flavors/*/Dockerfile`, `docs/descriptors/*`, anything with `@generated by .automation/build.py`) — fix the descriptor source instead
- The fix would require destructive git operations (force-push, branch rewrite, deletion)
- More than **3** fix-push cycles have run without turning any check from fail → pass
- A failure is in a workflow you don't recognize and can't trace to a source file

### 6. Apply the fix

- Edit the source (descriptor YAML, Python in `megalinter/`, fixtures in `.automation/test/`, workflows in `.github/workflows/`)
- If a descriptor changed, run `make megalinter-build` (NEVER `make megalinter-build-with-doc`)
- Run any obvious local validation that doesn't require Docker (syntax checks, `python -m py_compile`, `gh workflow view`)
- Do **not** introduce defensive hacks (skip-on-fail, retries, `|| true`) just to make CI green — fix the root cause

### 7. Commit & push

```bash
git status --short
git add <specific files>      # never `git add -A`
git commit -m "$(cat <<'EOF'
Fix CI: <one-line summary of the failure>

<optional 1-2 line body if non-obvious>

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

**Before pushing, reconcile with origin.** The MegaLinter auto-fix workflow pushes commits titled `[MegaLinter] Apply linters fixes` onto the PR branch. Detect and handle:

```bash
git fetch origin "$BRANCH"
NEW_REMOTE_COMMITS="$(git log --format='%s' HEAD..origin/"$BRANCH")"

if printf '%s\n' "$NEW_REMOTE_COMMITS" | grep -q '^\[MegaLinter\] Apply linters fixes'; then
    # Auto-fix bot pushed — try to rebase onto it (keeps the bot's fixes)
    if git pull --rebase origin "$BRANCH"; then
        git push
    else
        # Rebase failed with conflicts — abort and force-push our commit
        git rebase --abort
        git push --force-with-lease
    fi
else
    git push
fi
```

Notes:

- `--force-with-lease` (not `--force`) so we refuse to overwrite anything we haven't seen, except the bot commit we just observed
- This is the **only** authorized force-push path. Any other force-push needs explicit user permission
- If `NEW_REMOTE_COMMITS` contains commits that are **not** from the MegaLinter bot, **STOP** and ask the user — someone else pushed work, don't silently overwrite

After the push, capture the new `HEAD` SHA so you can wait for **its** workflow runs (not the previous ones). GitHub takes ~30s to register new runs; sleep 60 before re-entering step 2.

### 8. Loop

Go back to step 1. The loop ends when:

- All checks pass → success report
- You ask the user a question (loop pauses until they answer)
- You hit the 3-cycle cap without progress → ask before continuing
- The user interrupts

## Reporting

Each time you wake from a poll or finish a fix cycle, give the user **one short line**:

```
Cycle 2: build-deploy-dev failed (hadolint), pushed e0a44f1. Waiting 5m.
```

Do not paste full job logs into the conversation. Summarize and link to the run.

## Safety

- `git push` is the only network-mutating action — confirm the branch is not `main`/`master` before pushing
- Force-push is only authorized in **one** case: a `[MegaLinter] Apply linters fixes` commit landed on origin and rebasing onto it produces conflicts. Use `--force-with-lease`, never `--force`. Any other force-push needs explicit user permission.
- If `git fetch` shows commits on origin that are **not** the MegaLinter bot, stop and ask — someone else is working on the branch
- Never edit generated files — change the descriptor source and rebuild
- If `gh` is not authenticated or the repo isn't a GitHub repo, **STOP** and tell the user
