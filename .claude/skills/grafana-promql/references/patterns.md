# PromQL pattern library

## Rate, counter, and aggregation

```promql
# rate() — per-second average
rate(http_requests_total[5m])

# CORRECT: rate first, then aggregate
sum(rate(http_requests_total{job="api"}[5m])) by (status_code)

# WRONG: never sum() a raw counter before rate()
sum(http_requests_total) by (status_code)   # do NOT then rate()

# increase() — total count over window
increase(http_requests_total[1h])
```

`rate` vs `irate`:
- `rate()` smooths the full window — use for dashboards + alerts
- `irate()` uses the last two samples — for spike detection only, never alerting

## Label matchers

```promql
http_requests_total{job="api", status_code="200"}
http_requests_total{status_code=~"5.."}
http_requests_total{status_code!~"2.."}
http_requests_total{env=~"staging|production"}
```

## Aggregation

```promql
sum(rate(http_requests_total[5m])) by (service)
avg(node_cpu_seconds_total{mode="idle"}) by (instance)

# Top 5 by request rate
topk(5, sum(rate(http_requests_total[5m])) by (service))

# Count of distinct label values
count(count(up) by (job)) by ()
```

`by` keeps only listed labels; `without` drops only listed labels.

## Histogram quantiles

```promql
# Classic histogram
histogram_quantile(0.99,
  sum(rate(http_request_duration_seconds_bucket{job="api"}[5m])) by (le))

# Multi-service comparison — must include le AND service
histogram_quantile(0.95,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service))

# Native histograms (Prometheus 2.40+)
histogram_quantile(0.95, sum(rate(http_request_duration_seconds[5m])))
```

Forgetting `by (le)` is the most common bug — `histogram_quantile` returns NaN or wrong values.

## Ratios and error rates

```promql
# Error fraction
sum(rate(http_requests_total{status_code=~"5.."}[5m]))
  / sum(rate(http_requests_total[5m]))

# Success percentage
(1 - sum(rate(http_requests_total{status_code=~"5.."}[5m]))
     / sum(rate(http_requests_total[5m]))) * 100

# Avoid divide-by-zero
sum(rate(errors_total[5m]))
  / (sum(rate(requests_total[5m])) > 0)
```

## Absence and staleness

```promql
absent(up{job="api"})                  # metric disappeared
changes(up{job="api"}[5m]) == 0        # value not changing → stale exporter
count_over_time(up{job="api"}[5m]) > 0 # at least one sample in window
```

## Time offsets

```promql
# Current vs 1h ago
rate(http_requests_total[5m])
  - rate(http_requests_total[5m] offset 1h)

# Day-over-day
rate(http_requests_total[5m])
  / rate(http_requests_total[5m] offset 1d)

# Predict 2h ahead from 1h trend (linear regression)
predict_linear(node_filesystem_avail_bytes[1h], 2 * 3600)
```

## Recording rules

Naming: `<aggregation_level>:<metric_name>:<operation_and_window>`

```yaml
groups:
  - name: http_request_rates
    interval: 1m
    rules:
      - record: job:http_requests_total:rate5m
        expr:   sum(rate(http_requests_total[5m])) by (job)

      - record: job:http_errors:ratio5m
        expr: |
          sum(rate(http_requests_total{status_code=~"5.."}[5m])) by (job)
          / sum(rate(http_requests_total[5m])) by (job)

      - record: job:http_request_duration_p95:rate5m
        expr: |
          histogram_quantile(0.95,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le, job))
```

## SLO + burn-rate

```promql
# Availability SLO over 30 days
1 - (sum(increase(http_requests_total{status_code=~"5.."}[30d]))
     / sum(increase(http_requests_total[30d])))

# 1h burn-rate vs target (replace 0.999 with your SLO target)
( sum(rate(http_requests_total{status_code=~"5.."}[1h]))
  / sum(rate(http_requests_total[1h])) )
  / (1 - 0.999)
```

## Cardinality controls

```promql
# Top 10 metrics by series count
topk(10, count by (__name__)({__name__=~".+"}))

# Series count for one metric
count(http_requests_total)

# Cardinality of one label
count(count by (user_id)(http_requests_total))
```

Drop a high-cardinality label at scrape time (Alloy):

```alloy
prometheus.scrape "api" {
  targets = [...]
  rule { source_labels = ["user_id"]
         action        = "labeldrop" }
}
```

## Other common patterns

```promql
# Service availability (alert)
avg_over_time(up{job="api"}[5m]) < 0.9

# Saturation — disk full in <4h
predict_linear(node_filesystem_avail_bytes{mountpoint="/"}[1h], 4 * 3600) < 0

# Throughput spike — current rate > 3x 1h average
rate(http_requests_total[5m])
  > 3 * avg_over_time(rate(http_requests_total[5m])[1h:5m])
```
