# Watch a MegaLinter job on GitHub Actions

Requires the [`gh` CLI](https://cli.github.com/), authenticated (`gh auth status`).

## Find the run

```bash
# Runs for the current branch (MegaLinter workflow is usually named "MegaLinter")
gh run list --branch "$(git branch --show-current)" --limit 5 --json databaseId,name,status,conclusion,url

# Runs attached to the current PR
gh pr checks --json name,state,link
```

## Wait for completion

```bash
gh run watch <run-id> --exit-status   # blocks until the run completes
```

Or poll `gh run view <run-id> --json status,conclusion` every 30-60 seconds.

## Fetch the logs

```bash
# Only the failing steps (preferred — much smaller)
gh run view <run-id> --log-failed

# Full log of the MegaLinter job if needed
gh run view <run-id> --job <job-id> --log
```

## Parse

In the log, locate:

- The summary table: lines starting with `❌` (blocking errors) or `⚠️` (non-blocking) with linter key and error count.
- Per-linter sections delimited by the linter key header, containing the raw error lines with file paths.

Extract only linters with errors, their counts, files and up to 10 sample error lines each.

## Artifacts (optional)

If the workflow uploads the `megalinter-reports` artifact, `gh run download <run-id> -n megalinter-reports` gives you `mega-linter-report.json` — more reliable to parse than logs.
