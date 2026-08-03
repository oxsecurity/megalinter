# Watch a MegaLinter job on Bitbucket Pipelines

Bitbucket has no official CLI: use the REST API 2.0 with `curl`. Authentication via a
[workspace/repository access token](https://support.atlassian.com/bitbucket-cloud/docs/access-tokens/)
(`Authorization: Bearer $BITBUCKET_TOKEN`) or an app password (`curl -u user:app_password`).

Set the base once:

```bash
BB="https://api.bitbucket.org/2.0/repositories/<workspace>/<repo_slug>"
AUTH="Authorization: Bearer $BITBUCKET_TOKEN"
```

## Find the pipeline

```bash
# Latest pipelines for the current branch
curl -s -H "$AUTH" "$BB/pipelines/?target.branch=$(git branch --show-current)&sort=-created_on&pagelen=5" \
  | jq '.values[] | {uuid, build_number: .build_number, state: .state.name, result: .state.result.name?}'
```

## Wait for completion

Poll every 30-60 seconds until `state.name` is `COMPLETED`:

```bash
curl -s -H "$AUTH" "$BB/pipelines/<pipeline-uuid>" | jq '{state: .state.name, result: .state.result.name?}'
```

## Fetch the logs

```bash
# List steps, find the MegaLinter one
curl -s -H "$AUTH" "$BB/pipelines/<pipeline-uuid>/steps/" \
  | jq '.values[] | {uuid, name, state: .state.name}'

# Fetch the step log (plain text)
curl -s -H "$AUTH" "$BB/pipelines/<pipeline-uuid>/steps/<step-uuid>/log"
```

## Parse

In the log, locate:

- The summary table: lines starting with `❌` (blocking errors) or `⚠️` (non-blocking) with linter key and error count.
- Per-linter sections containing raw error lines with file paths.

Extract only linters with errors, their counts, files and up to 10 sample error lines each.
