# Watch a MegaLinter job on GitLab CI

Requires the [`glab` CLI](https://gitlab.com/gitlab-org/cli), authenticated (`glab auth status`).

## Find the pipeline and job

```bash
# Latest pipelines for the current branch
glab ci list --per-page 5

# Status of the pipeline for the current branch (live view)
glab ci status --branch "$(git branch --show-current)"

# Jobs of a pipeline (find the one named "mega-linter" / "megalinter")
glab api "projects/:id/pipelines/<pipeline-id>/jobs" | jq '.[] | {id, name, status}'
```

## Wait for completion

Poll `glab api "projects/:id/pipelines/<pipeline-id>" | jq .status` every 30-60 seconds until `success` or `failed`.

## Fetch the logs

```bash
glab ci trace <job-id>       # streams/prints the job log
```

## Parse

In the log, locate:

- The summary table: lines starting with `❌` (blocking errors) or `⚠️` (non-blocking) with linter key and error count.
- Per-linter sections containing raw error lines with file paths.

Extract only linters with errors, their counts, files and up to 10 sample error lines each.

## Artifacts (optional)

If the job declares `megalinter-reports` artifacts:

```bash
glab api "projects/:id/jobs/<job-id>/artifacts/megalinter-reports/mega-linter-report.json"
```
