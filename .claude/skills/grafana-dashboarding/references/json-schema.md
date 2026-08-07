# Dashboard + panel JSON schema

## Dashboard root

```json
{
  "title": "My Dashboard",
  "uid": "my-dashboard-v1",
  "tags": ["service", "production"],
  "time":     { "from": "now-1h", "to": "now" },
  "refresh":  "30s",
  "timezone": "browser",
  "schemaVersion": 41,
  "templating":  { "list": [] },
  "annotations": { "list": [] },
  "panels": []
}
```

- `uid` — stable identifier; keep short
- `schemaVersion` — `41` for Grafana 11+
- `time.from` / `to` — relative (`now-1h`) or absolute ISO
- `refresh` — `"30s"`, `"1m"`, `"5m"`, `""` (off)

## Panel

```json
{
  "id": 1,
  "type": "timeseries",
  "title": "Request Rate",
  "gridPos": { "x": 0, "y": 0, "w": 12, "h": 8 },
  "datasource": { "type": "prometheus", "uid": "${datasource}" },
  "targets": [{
    "expr": "sum(rate(http_requests_total{job=\"$job\"}[5m])) by (status_code)",
    "legendFormat": "{{status_code}}",
    "refId": "A"
  }],
  "fieldConfig": {
    "defaults": {
      "unit": "reqps",
      "thresholds": { "mode": "absolute", "steps": [
        { "color": "green",  "value": null },
        { "color": "yellow", "value": 1000 },
        { "color": "red",    "value": 5000 }
      ]}
    },
    "overrides": []
  },
  "options": {
    "legend":  { "calcs": ["mean","max","last"], "displayMode": "table", "placement": "bottom" },
    "tooltip": { "mode": "multi", "sort": "desc" }
  }
}
```

`gridPos`: 24-column grid. Widths: full=24, half=12, third=8, quarter=6. Height 1 unit ≈ 30 px.

## Panel types

| Panel | Use case |
|---|---|
| **Time series** | Any metric over time |
| **Stat** | Single value + sparkline |
| **Gauge** | % or value against min/max |
| **Bar gauge** | Side-by-side comparison |
| **Table** | Multi-column data |
| **Heatmap** | Distribution over time |
| **Logs** | Loki log streams |
| **Traces** | Tempo trace search |
| **Text** | Markdown docs |
| **Candlestick** | OHLC / min-max-avg |
| **Node graph** | Service dependency graph |

## Useful units

```
reqps        requests/sec
ops          ops/sec
Bps          bytes/sec
percentunit  0.0-1.0 as %
bytes        bytes (auto-scales)
decbytes     decimal bytes (1 KB = 1000 B)
ms / s       milliseconds / seconds
dtdurationms 1h 2m 3s
short        compact (1.2k, 3.4M)
none         raw number
```

## Template variables

```json
{ "name":"job", "type":"query", "datasource":{"type":"prometheus","uid":"prometheus"},
  "query":{"query":"label_values(up, job)","refId":"A"},
  "refresh":2, "includeAll":true, "multi":true, "label":"Service" }

{ "name":"cluster", "type":"constant", "query":"production", "label":"Cluster" }

{ "name":"datasource", "type":"datasource", "pluginId":"prometheus",
  "includeAll":false, "label":"Prometheus" }
```

Multi-value variables expand to a regex OR: `$job=["api","worker"]` → `job=~"api|worker"`.
Chained: `label_values(kube_pod_info{namespace=\"$namespace\"}, pod)`.

## Transformations

```json
"transformations": [
  { "id": "merge", "options": {} },
  { "id": "organize", "options": {
      "renameByName":  { "Value #A": "Request Rate", "Value #B": "Error Rate" },
      "excludeByName": { "Time": true }
  }},
  { "id": "calculateField", "options": {
      "alias": "Error %", "mode": "reduceRow",
      "reduce": { "reducer": "last" },
      "binary": { "left": "errors", "right": "total", "operator": "/" }
  }},
  { "id": "filterByValue", "options": {
      "filters": [{ "fieldName":"Error %", "config":{ "id":"greater", "options":{ "value":0.01 }}}],
      "type": "include", "match": "any"
  }}
]
```

Common IDs: `merge`, `organize`, `rename`, `calculateField`, `filterByValue`, `groupBy`, `sortBy`, `limit`, `labelsToFields`, `seriesToRows`, `partitionByValues`.

## Links & annotations

```json
"links": [
  { "title":"Go to details", "url":"/d/details?var-service=${__field.labels.service}", "targetBlank":false },
  { "title":"Runbook",        "url":"https://wiki.example.com/runbook/${job}", "icon":"external link",
    "targetBlank":true, "type":"link" }
]
```

Built-in vars: `${__value.raw}`, `${__field.labels.job}`, `${__url.params}`, `${__from}` / `${__to}` (Unix ms).

Loki annotation:

```json
{ "datasource":{"type":"loki","uid":"loki"},
  "expr":"{job=\"deployments\"} |= \"deployed\"",
  "name":"Deployments", "iconColor":"blue",
  "titleFormat":"{{service}} deployed", "textFormat":"{{version}} by {{author}}" }
```

Prometheus annotation:

```json
{ "datasource":{"type":"prometheus","uid":"prometheus"},
  "expr":"changes(kube_deployment_status_observed_generation{namespace=\"production\"}[5m]) > 0",
  "step":"60s", "name":"Deployments", "iconColor":"blue",
  "titleFormat":"Deploy: {{deployment}}" }
```
