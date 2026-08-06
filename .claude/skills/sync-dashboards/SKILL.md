---
name: sync-dashboards
description: Keep the MegaLinter observability dashboards (docs/dashboards/) in sync with the ApiReporter v2 payload and metrics contract. Use after modifying ApiReporter.py, megalinter/api_providers/, or the dashboards themselves.
disable-model-invocation: false
allowed-tools: Read Glob Grep Write Edit Bash
argument-hint: "[what changed, e.g. 'added a run metric xyz']"
---

You maintain the consistency between the MegaLinter observability payload and the provider dashboards.

## The contract

- **Producer**: `megalinter/reporters/ApiReporter.py` builds the v2 payload (run-level KPIs incl. `qualityGateStatus` and the 0-100 `healthScore`, per-linter records, SARIF-derived `rulesBreakdown`/`filesBreakdown`); `megalinter/api_providers/ApiProvider.py` defines the metric fields (`run_metric_fields`, `linter_metric_fields`) and each `ApiProvider*` subclass maps them to its backend (Prometheus/Loki, Datadog, Elastic, New Relic).
- **Contract file**: `.automation/dashboard_builders/contract.py` lists the same fields, labels (base + run-level `megalinterVersion`/`megalinterFlavor`), record types and metric name prefixes.
- **Consumers**: the `DashboardBuilder*` classes in `.automation/dashboard_builders/` generate `docs/dashboards/` (Grafana JSON, Datadog JSON, New Relic JSON, Kibana ndjson + `manifest.json`).

## Dashboard design invariants (keep them when editing)

- **Fleet-to-detail navigation**: Grafana org table/charts carry data links to the Repository dashboard (`var-repo`), which links to Linter Detail (`var-linter`); Datadog uses the `git_repo_name`/`git_branch_name` template variables + `__SELF_URL__` custom links (substituted by the uploader); New Relic has Repository/Branch NRQL variables, a "Repository detail" page and facet links (`__REPOSITORY_DETAIL_PAGE_GUID__`, substituted by the uploader's second pass); Kibana relies on native click-to-filter.
- **Branch filtering** must stay available on every platform (Grafana `$branch`, Datadog `$git_branch_name`, New Relic `{{gitBranchName}}` with `%` default, Kibana filter bar).
- **Rating drill-down**: every rating (A-E) tile leads to a "Why this rating?" explanation — Grafana dedicated dashboard (uid `megalinter-rating`, linked from the rating stats), New Relic dedicated page (facet-linkable via the `__RATING_PAGE_GUID__` marker), Datadog group widget, Elastic markdown + breakdown panels. It must always show: the formula, linters success/warning/error counts, and the linters dragging the score down.
- **Derived KPIs**: the A-E rating is a dashboard-side range mapping of `healthScore` (A>=90, B>=80, C>=65, D>=50, else E); "time saved" is `totalErrorsFixed * 5` minutes — keep formulas consistent across providers and documented in `docs/observability.md`.
- **Agnostic dashboards**: no account ids, datasource uids, or instance URLs hardcoded in generated files — placeholders are resolved by `mega-linter-runner/lib/upload-dashboards.js` at upload time so anyone can provision them on their own account.
- **Value-conditional styling**: KPIs are colored by value on every platform — Grafana thresholds/background stat tiles/color-background table cells/threshold-zone areas, Datadog `conditional_formats` + semantic timeseries palettes (warm=errors, cool=health, purple=duration), New Relic billboard `thresholds` + fixed series colors (Blocking=red, Non-blocking=yellow), Kibana Lens custom palettes on metric panels. Keep the semantics: green=good, yellow=warning, red=blocking, blue=neutral/informative.
- **Cardinality**: `runId`, `jobUrl`, rule ids and file paths never become metric tags or Loki stream labels.

## Process

1. Identify what changed (new/renamed/removed payload field, label, record type, or a dashboard improvement request).
2. Apply the change consistently:
   - Payload change → update `contract.py` AND the relevant `DashboardBuilder*` panels/queries.
   - Dashboard-only change → update the `DashboardBuilder*` class (never edit `docs/dashboards/*` directly — they are generated).
3. Regenerate: `python .automation/build_dashboards.py` (use the repo venv).
4. Verify sync: `python .automation/build_dashboards.py --check` must pass, and `megalinter/tests/test_megalinter/api_reporter_v2_test.py` must still pass (`pytest megalinter/tests/test_megalinter/api_reporter_v2_test.py`).
5. If credentials are available in `.env` (GRAFANA_HOST/GRAFANA_TOKEN, DD_TOKEN, ELASTIC_HOST/ELASTIC_API_KEY, NEW_RELIC_HOST/NEW_RELIC_API_KEY), offer to upload the regenerated dashboards to the live instances with `node mega-linter-runner/lib/index.js --upload-dashboards <provider>` (set `MEGALINTER_DASHBOARDS_DIR` to the local `docs/dashboards` folder) and verify with provider queries that the dashboards' metrics/fields return data.
6. Update the documentation if the metrics reference changed: `docs/observability.md` and `docs/observability/<provider>.md`.

## Rules

- Payload/metric renames are breaking changes: mention them in `CHANGELOG.md` (beta section) with a migration note.
- Keep metric label cardinality low: `runId`, `jobUrl`, rule ids and file paths never become metric tags or Loki stream labels — they belong in log lines/documents.
- Datadog tag keys are snake_case (`git_repo_name`, `linter_key`, `record_type`); everywhere else camelCase.
