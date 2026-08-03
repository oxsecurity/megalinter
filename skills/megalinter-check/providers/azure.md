# Watch a MegaLinter job on Azure Pipelines

Requires the [`az` CLI](https://learn.microsoft.com/cli/azure/) with the `azure-devops` extension (`az extension add --name azure-devops`), authenticated (`az login` or `AZURE_DEVOPS_EXT_PAT` environment variable).

Set defaults once to simplify commands:

```bash
az devops configure --defaults organization=https://dev.azure.com/<org> project=<project>
```

## Find the run

```bash
# Latest runs for the current branch
az pipelines runs list --branch "$(git branch --show-current)" --top 5 \
  --query "[].{id:id, name:definition.name, status:status, result:result}" -o table
```

## Wait for completion

Poll every 30-60 seconds until `status` is `completed`:

```bash
az pipelines runs show --id <run-id> --query "{status:status, result:result}"
```

## Fetch the logs

```bash
# List the log entries of the run, then fetch the MegaLinter step's log by id
az devops invoke --area build --resource logs \
  --route-parameters project=<project> buildId=<run-id> \
  --api-version 7.1 -o json

az devops invoke --area build --resource logs \
  --route-parameters project=<project> buildId=<run-id> logId=<log-id> \
  --api-version 7.1 -o json
```

(The logs endpoint is `https://dev.azure.com/<org>/<project>/_apis/build/builds/<run-id>/logs/<log-id>` — a PAT with `Build (read)` scope in the `Authorization: Basic` header also works with plain `curl`.)

## Parse

In the log, locate:

- The summary table: lines starting with `❌` (blocking errors) or `⚠️` (non-blocking) with linter key and error count.
- Per-linter sections containing raw error lines with file paths.

Extract only linters with errors, their counts, files and up to 10 sample error lines each.
