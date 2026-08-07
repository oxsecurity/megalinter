---
name: grafana-promql
license: Apache-2.0
metadata:
  internal: true
  author: Grafana Labs
  source: https://github.com/grafana/skills (skills/grafana-core/promql)
description: Write, validate, and optimize PromQL for Prometheus / Grafana Mimir / Grafana Cloud Metrics. Covers `rate` vs `irate` vs `increase`, label matchers and regex, `sum / avg / topk / by / without` aggregation, classic + native `histogram_quantile`, ratios with divide-by-zero guards, `absent` / `changes` for staleness, time offsets and `predict_linear`, recording-rule naming, SLO + burn-rate math, and a cardinality-hunting playbook. Use when writing a metric query, fixing wrong p95s, building an error-budget alert, debugging "query is slow", finding the noisy label that blew up cardinality, or migrating a dashboard query to a recording rule — even when the user says "calculate the error rate", "p99 latency", "sum by service", "why is this query slow", or "what's filling Mimir" without naming PromQL.
---

# PromQL Query Patterns

> **Docs**: <https://prometheus.io/docs/prometheus/latest/querying/basics/>

PromQL returns either an **instant vector**, a **range vector**, or a **scalar**.

**Golden rule:** `rate()` / `increase()` require a range vector ≥ 4× the scrape interval. 60s scrape → use `[5m]` minimum.

## Prerequisites

- A Prometheus / Mimir / Grafana Cloud endpoint to query (`/api/v1/query` or via Grafana Explore)
- The PromQL pattern library in [`references/patterns.md`](references/patterns.md)

## Common Workflows

### 1. Write + validate a query

```bash
# 0. Point at your Prometheus/Mimir. For Grafana Cloud, use the metrics endpoint
#    and add basic auth (-u "<metrics_user>:<token>") to each curl below.
PROM=http://localhost:9090   # or https://prometheus-prod-XX.grafana.net/api/prom

# 1. Sketch the query — for "5xx error rate per service":
EXPR='sum(rate(http_requests_total{status_code=~"5.."}[5m])) by (service)'

# 2. Validate syntax + that the metric/labels exist
curl -sG --data-urlencode "query=${EXPR}" \
  "$PROM/api/v1/query" | jq '.status, (.data.result|length)'
# Expect: "success" and result count > 0. If 0 — check label spelling and scrape activity:
curl -sG --data-urlencode "match[]=http_requests_total" "$PROM/api/v1/series" | jq '.data | length'

# 3. Sanity-check the magnitude — open Grafana Explore, paste the expr,
#    confirm the values look right against a known ground truth (k6 run, log count, etc.)
```

### 2. Common patterns to copy

**Per-status request rate** (aggregate AFTER rate):

```promql
sum(rate(http_requests_total{job="api"}[5m])) by (status_code)
```

**p95 latency** (must keep `le` in the inner aggregation):

```promql
histogram_quantile(0.95,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service))
```

**Error rate with divide-by-zero guard:**

```promql
sum(rate(http_requests_total{status_code=~"5.."}[5m]))
  / (sum(rate(http_requests_total[5m])) > 0)
```

Full library (recording rules, SLO burn-rate, offsets, cardinality hunt, native histograms): [`references/patterns.md`](references/patterns.md).

### 3. Convert a slow dashboard query into a recording rule

```yaml
# 1. Pick the slow expression, give it a recording-rule name
groups:
  - name: http_request_rates
    interval: 1m
    rules:
      - record: job:http_request_duration_p95:rate5m
        expr: |
          histogram_quantile(0.95,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le, job))
```

```bash
# 2. After rules load, verify the new metric exists
curl -sG --data-urlencode "query=job:http_request_duration_p95:rate5m" \
  "$PROM/api/v1/query" | jq '.data.result | length'   # → > 0

# 3. Verify it matches the original expression for at least one sample window
# (Both queries should produce the same value at the same timestamp.)

# 4. Replace the dashboard panel expression with the recording-rule metric.
```

## Common bugs

- `histogram_quantile` returns NaN → forgot `by (le)` in the inner aggregation
- "No data" → check the metric exists (`/api/v1/series`) and the window ≥ 4× scrape interval
- Wrong rate magnitude → counter was aggregated before `rate()` (always `rate()` first)
- Query timeout → series count too high; use `topk(...)` + a recording rule + drop high-cardinality labels (see [`references/patterns.md`](references/patterns.md))

## Resources

- [PromQL basics](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Operators](https://prometheus.io/docs/prometheus/latest/querying/operators/)
- [Functions](https://prometheus.io/docs/prometheus/latest/querying/functions/)
- [Grafana Mimir](https://grafana.com/docs/mimir/latest/)
