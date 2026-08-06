---
name: megalinter-check
description: Collect MegaLinter lint errors for the current repository. Use when the user wants to know if the code passes linting, why the MegaLinter CI job fails, or before/after fixing lint errors. Two modes - watch a CI job (GitHub Actions, GitLab CI, Azure Pipelines, Bitbucket Pipelines) and parse its logs, or run MegaLinter locally with Docker (full run or fast parallel standalone linter runs).
argument-hint: "[mode: watch|local] [PR/job URL or linter keys]"
allowed-tools: Bash, Read, Grep, Glob, Write, Agent, AskUserQuestion
user-invocable: true
licence: MegaLinter by OX Security, Copyright 2026 - https://megalinter.io/
---

# MegaLinter check

Collect the current MegaLinter errors and produce a compact error list that the `megalinter-fix` skill can consume.

## Choose a mode

- **Watch mode** — a MegaLinter CI job exists for the current branch/PR (running or completed): parse its logs. No Docker needed.
- **Local mode** — no CI job available, or the user wants a pre-push check: run MegaLinter with Docker via `npx mega-linter-runner`.
- **Targeted re-check** (local, after fixes): re-run only the previously-failing linters in parallel standalone images.

## Watch mode

1. Detect the provider from `git remote get-url origin` and the CI config files present.
2. Load the matching provider guide from this skill's directory — **only the one you need**:
   - GitHub Actions → `providers/github.md`
   - GitLab CI → `providers/gitlab.md`
   - Azure Pipelines → `providers/azure.md`
   - Bitbucket Pipelines → `providers/bitbucket.md`
3. Follow the guide: locate the MegaLinter job, wait for completion if running, fetch the logs of the MegaLinter step.
4. Parse the MegaLinter summary (the `❌`/`✅` table) and per-linter error sections.

## Local mode

Before the first local run, make sure the user is aware that running MegaLinter locally needs a reasonably powerful machine (CPU, RAM, free disk space) and a good internet connection: MegaLinter is Docker-based and the first run downloads a large image (can be several GB depending on the flavor). If that is a problem for the user, prefer watch mode (CI does the work).

Requires a container engine (docker or podman). If neither is installed and running, **ask the user** whether you should install or start one — then (and only then) load `container-engine.md` from this skill's directory for the setup instructions (prefer podman: free of charge even in enterprise contexts). If the user declines, fall back to watch mode.

Flavor and version are resolved automatically from `MEGALINTER_FLAVOR` / `MEGALINTER_VERSION` in `.mega-linter.yml` — do not pass `--flavor` or `--release` yourself.

```bash
npx mega-linter-runner                            # docker
npx mega-linter-runner --container-engine podman  # podman
```

Tip: for repeated local runs (e.g. fix → re-check loops), install the runner once with `npm install -g mega-linter-runner` and call `mega-linter-runner` directly — it avoids the `npx` package resolution overhead on every invocation.

- Add `--fix` if `.mega-linter.yml` defines `APPLY_FIXES` other than `none` (the repository has opted into auto-fixing).
- Then read `megalinter-reports/mega-linter-report.json` and `megalinter-reports/linters_logs/ERROR-*.log` instead of parsing the console output.

### First local run: prerun analysis

Before the **first** local full run on a repository (fresh `megalinter-setup`, or no `megalinter-reports/mega-linter-report.json` from a previous run), start with a prerun analysis so the real run is not wasted on a badly tuned configuration. Also use it later whenever the user asks to tune MegaLinter performances.

Prerun requires MegaLinter v10 or beta: check `MEGALINTER_VERSION` in `.mega-linter.yml` and skip this step (go straight to the full run) when the pinned version is older.

1. Run MegaLinter in analysis-only mode (fast: no linter is run, and the image pull is reused by the real run right after):

   ```bash
   npx mega-linter-runner --prerun
   ```

2. Read `megalinter-reports/prerun-report.json`. Each entry of `suggestions` describes a `.mega-linter.yml` change: `variable`, `operation` (`append` to a list / `set`), `values`, `safe`, `reason`, `details`.
3. Review the suggestions with the user:
   - `safe: true` suggestions (directories containing only gitignored files) do not change the linting scope - present them grouped, recommend applying them.
   - `safe: false` suggestions (well-known generated folder names still containing lintable files, flavor change) need an explicit user decision - ask about each one, with the file counts from `details`. A flavor change also requires updating the image reference in the CI workflow files.
4. Apply the accepted changes to `.mega-linter.yml`, then continue with the normal full run.

If the report file is missing after the run (image older than v10 that ignored `MEGALINTER_PRERUN` and linted everything), treat the output as a normal full run instead of re-running.

## Targeted re-check (after fixes)

Re-run only what previously failed, in parallel (max 4 concurrent containers):

```bash
npx mega-linter-runner --linter PYTHON_RUFF src/a.py src/b.py &
npx mega-linter-runner --linter MARKDOWN_MARKDOWNLINT README.md &
wait
```

**Version rule (all skills)**: runner and Docker image versions always follow `MEGALINTER_VERSION` from `.mega-linter.yml` — invoke `npx mega-linter-runner@beta` when it is `beta`, plain `npx mega-linter-runner` otherwise, and never pass `--release` yourself. Caveat until MegaLinter v10: standalone `megalinter-only-*` images are only multi-arch on the `beta` tag, so if a standalone run fails with a platform error while `MEGALINTER_VERSION` is not `beta`, inform the user and propose either pinning `MEGALINTER_VERSION: beta` or falling back to a full-image re-check.

- Pass the fixed files as arguments for file-scoped linters; omit the file list for project-scoped linters (e.g. `REPOSITORY_*`, `COPYPASTE_JSCPD`).
- Each run writes its reports to `megalinter-reports/<linter_key_lower>/` — no conflict between parallel runs.

## Output contract

Whatever the mode, summarize the result in this shape (this is what `megalinter-fix` consumes):

```json
{
  "status": "success|errors|failure",
  "linters": [
    {
      "key": "PYTHON_RUFF",
      "errors": 12,
      "fixable": true,
      "blocking": true,
      "files": ["src/a.py"],
      "samples": ["src/a.py:10:5 E501 line too long"]
    }
  ]
}
```

Distinguish **blocking** linters (❌, fail the job) from non-blocking ones (⚠️, `DISABLE_ERRORS: true`). A `failure` status means the job/run itself broke (container engine, network, configuration): include a `"failure_reason"` field with a short cause excerpt instead of linter errors. In watch mode, a `"job_url"` field may be added for reference.

## Performance check (even when the run is green)

MegaLinter's summary table includes an `Elapsed time` column per linter — always collect it. Add a `"slow_linters"` field to the output when any linter took **more than 30 seconds** or more than **25% of the total lint time**:

```json
"slow_linters": [{"key": "REPOSITORY_GRYPE", "elapsed_seconds": 116.6}]
```

When `slow_linters` is non-empty, load `performance.md` from this skill's directory and report the matching improvement suggestions to the user — explicitly noting that nothing is failing and these are pure speed wins. Never apply a performance change (exclusions, caching, disabling a linter) without the user's agreement.

## Optimization: sub-agents (Claude Code and compatible agents)

If sub-agents are available and the agent definitions are installed (see `megalinter-setup`):

- Watch mode → spawn `megalinter-watcher` with the branch/PR reference; it polls, fetches and parses, and returns the output contract.
- Local mode → spawn `megalinter-runner` with the command to run; it executes and digests the reports.
- Targeted re-check → spawn one `megalinter-runner` per standalone linter run, in parallel (max 4).

This keeps multi-megabyte CI logs and linter output out of your context. Without sub-agents, do everything inline.
