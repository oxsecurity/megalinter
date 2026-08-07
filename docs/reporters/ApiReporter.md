---
title: API / Observability Reporter for MegaLinter
description: Sends MegaLinter results (quality gate, errors, linters, top rules & files) to Grafana, Datadog, Elastic or New Relic, with ready-to-use dashboards
---
<!-- markdownlint-disable MD013 MD025 MD033 MD041 -->

# API Reporter

Sends MegaLinter results to **observability platforms**: [Grafana](../observability/grafana.md) (Loki + Prometheus), [Datadog](../observability/datadog.md), [Elastic](../observability/elastic.md) and [New Relic](../observability/newrelic.md).

See the [**Observability**](../observability.md) documentation for the quick start, the ready-to-use dashboards and the per-provider setup guides.

![MegaLinter Grafana repository dashboard](../assets/images/grafana-scr.png)

## Payload (version 2)

At the end of each run, the reporter builds a payload containing:

- **Run-level KPIs**: quality gate status, repository health score (0-100), blocking / non-blocking / auto-fixed error counts, linters status counts, files analyzed, run duration
- **One record per linter**: descriptor, linter key, severity, blocking status, errors found, files analyzed, elapsed time, human-readable output
- **Top rules and top files** per linter (up to 20 each), parsed from the linters SARIF output (disable with `API_REPORTER_DETAILS: false`)

The payload is delivered to each provider declared in `API_REPORTER_PROVIDER` (comma-separated list). Delivery is implemented with plain HTTPS calls: no agent or forwarder to install.

## Configuration

| Variable                      | Description                                                                           | Default   |
|:------------------------------|:--------------------------------------------------------------------------------------|:----------|
| `API_REPORTER`                | Activates the API reporter                                                            | `false`   |
| `API_REPORTER_PROVIDER`       | Comma-separated list of target providers: `grafana`, `datadog`, `elastic`, `newrelic` | `grafana` |
| `API_REPORTER_DETAILS`        | Include per-rule and per-file breakdowns in the payload                               | `true`    |
| `API_REPORTER_ORG_IDENTIFIER` | Organization identifier added to all records                                          |           |
| `API_REPORTER_DEBUG`          | Log the payloads sent to the providers                                                | `false`   |

Provider variables (authentication, endpoints) are described on each provider page:

- [Grafana variables](../observability/grafana.md#sending-data) (`API_REPORTER_URL`, `API_REPORTER_METRICS_URL`, basic auth / bearer variables)
- [Datadog variables](../observability/datadog.md#sending-data) (`API_REPORTER_DATADOG_*`)
- [Elastic variables](../observability/elastic.md#sending-data) (`API_REPORTER_ELASTIC_*`)
- [New Relic variables](../observability/newrelic.md#sending-data) (`API_REPORTER_NEWRELIC_*`)

Legacy `NOTIF_API_*` variables from the v1 reporter are still accepted as aliases of their `API_REPORTER_*` counterparts.

## Migration from payload v1

MegaLinter v10 replaces the v1 payload:

- Metric series are renamed: `linter_run_*` becomes `megalinter_linter_run_*`, and new run-level `megalinter_run_*` series are added
- Loki streams now carry a `recordType` label (`run`, `linter`, `rule`, `file`), and high-cardinality values (`runId`, `jobUrl`) moved from labels to the log line
- The v1 Grafana dashboards (`docs/grafana`) are superseded by the v2 dashboards: re-provision them with `npx mega-linter-runner --upload-dashboards grafana` (see [Grafana integration](../observability/grafana.md))

## Troubleshooting

Define `API_REPORTER_DEBUG: true` to log the exact payloads sent to each provider, and the API error responses in case of failure. Delivery failures never fail the MegaLinter run: they are reported as warnings in the console log.
