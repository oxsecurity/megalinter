# Chart Types Reference

Complete schema reference for each supported chart type via the Kibana dashboards & visualizations API.

**Supported Chart Types:**

- `metric` — Single metric value
- `xy` — Line, area, bar charts
- `gauge` — Gauge visualization
- `heatmap` — Heatmap charts
- `tag_cloud` — Tag/word cloud
- `data_table` — Data tables
- `region_map` — Region/choropleth maps
- `pie`, `treemap`, `mosaic`, `waffle` — Partition charts (use `pie` with `styling.donut_hole` for donuts: `"s"`, `"m"`,
  or `"l"`)

## DataView Aggregation Operations

When using `data_view_reference` or `data_view_spec` datasets, the following operations are available:

| Operation            | Description                          | Requires Field |
| -------------------- | ------------------------------------ | -------------- |
| `count`              | Document count                       | No             |
| `average`            | Average value                        | Yes            |
| `sum`                | Sum of values                        | Yes            |
| `max`                | Maximum value                        | Yes            |
| `min`                | Minimum value                        | Yes            |
| `unique_count`       | Cardinality                          | Yes            |
| `median`             | Median value                         | Yes            |
| `standard_deviation` | Standard deviation                   | Yes            |
| `percentile`         | Percentile (with `percentile` param) | Yes            |
| `percentile_rank`    | Percentile rank (with `rank` param)  | Yes            |
| `last_value`         | Last value (with `time_field`)       | Yes            |
| `date_histogram`     | Time buckets (for x-axis)            | Yes            |
| `terms`              | Top values (for x-axis/breakdown)    | Yes            |

## Metric

Single metric value display. Uses a `metrics` (plural) array with `type: "primary"` or `type: "secondary"`.

**ES|QL:**

```json
{
  "type": "metric",
  "data_source": {
    "type": "esql",
    "query": "FROM logs | STATS count = COUNT()"
  },
  "metrics": [
    {
      "type": "primary",
      "column": "count"
    }
  ]
}
```

**dataView:**

```json
{
  "type": "metric",
  "data_source": { "type": "data_view_reference", "ref_id": "90943e30-9a47-11e8-b64d-95841ca0b247" },
  "metrics": [
    {
      "type": "primary",
      "operation": "count",
      "label": "Total Events"
    }
  ]
}
```

**Metric Item Properties:**

| Property    | Type   | Required | Description                                                     |
| ----------- | ------ | -------- | --------------------------------------------------------------- |
| `type`      | string | Yes      | `"primary"` or `"secondary"`                                    |
| `operation` | string | dataView | Aggregation name (for dataView only; not used with ES\|QL)      |
| `column`    | string | ES\|QL   | ES\|QL column name                                              |
| `field`     | string | dataView | Field name (required for dataView aggregations needing a field) |
| `label`     | string | No       | Display label                                                   |

**Metric Styling:** Styling is configured at the **config root level** (sibling to `type`, `data_source`, `metrics`),
not inside `metrics[]`. Uses `primary` and `secondary` sub-objects:

```json
{
  "type": "metric",
  "data_source": { ... },
  "metrics": [{ "type": "primary", "operation": "count" }],
  "styling": {
    "primary": {
      "position": "bottom",
      "labels": { "alignment": "left" },
      "value": { "sizing": "auto", "alignment": "right" }
    }
  }
}
```

> **Tip:** For ES|QL metrics in dashboards, avoid redundant labels by leaving the panel `title` empty (`""`) and
> aliasing the column name in ES|QL with backticks (e.g. ``STATS `Total Requests` = COUNT()`` and setting
> `"column": "Total Requests"`).

## XY Charts

Line, area, and bar charts. For ES|QL, the `data_source` goes **inside each layer**.

### Bar Chart

```json
{
  "type": "xy",
  "layers": [
    {
      "type": "bar",
      "data_source": {
        "type": "esql",
        "query": "FROM logs | STATS count = COUNT() BY status"
      },
      "x": { "column": "status" },
      "y": [{ "column": "count" }]
    }
  ]
}
```

### Line Chart (Time Series)

```json
{
  "type": "xy",
  "axis": {
    "x": { "scale": "temporal", "domain": { "type": "fit", "rounding": false } }
  },
  "layers": [
    {
      "type": "line",
      "data_source": {
        "type": "esql",
        "query": "FROM logs | WHERE @timestamp <= ?_tend AND @timestamp > ?_tstart | STATS count = COUNT() BY BUCKET(@timestamp, 75, ?_tstart, ?_tend)"
      },
      "x": { "column": "BUCKET(@timestamp, 75, ?_tstart, ?_tend)", "label": "@timestamp" },
      "y": [{ "column": "count" }]
    }
  ]
}
```

### Area Chart

```json
{
  "type": "xy",
  "axis": {
    "x": { "scale": "temporal", "domain": { "type": "fit", "rounding": false } }
  },
  "layers": [
    {
      "type": "area",
      "data_source": {
        "type": "esql",
        "query": "FROM metrics | WHERE @timestamp <= ?_tend AND @timestamp > ?_tstart | STATS avg_cpu = AVG(cpu) BY BUCKET(@timestamp, 75, ?_tstart, ?_tend)"
      },
      "x": { "column": "BUCKET(@timestamp, 75, ?_tstart, ?_tend)", "label": "@timestamp" },
      "y": [{ "column": "avg_cpu" }]
    }
  ]
}
```

### Multiple Y-Axis Values

```json
{
  "type": "xy",
  "axis": {
    "x": { "scale": "temporal", "domain": { "type": "fit", "rounding": false } }
  },
  "layers": [
    {
      "type": "line",
      "data_source": {
        "type": "esql",
        "query": "FROM logs | WHERE @timestamp <= ?_tend AND @timestamp > ?_tstart | STATS count = COUNT(), errors = COUNT(CASE(level == \"error\", 1, null)) BY BUCKET(@timestamp, 75, ?_tstart, ?_tend)"
      },
      "x": { "column": "BUCKET(@timestamp, 75, ?_tstart, ?_tend)", "label": "@timestamp" },
      "y": [
        { "column": "count", "label": "Total" },
        { "column": "errors", "label": "Errors" }
      ]
    }
  ]
}
```

### Split Series (Color by Field)

```json
{
  "type": "xy",
  "axis": {
    "x": { "scale": "temporal", "domain": { "type": "fit", "rounding": false } }
  },
  "layers": [
    {
      "type": "line",
      "data_source": {
        "type": "esql",
        "query": "FROM logs | WHERE @timestamp <= ?_tend AND @timestamp > ?_tstart | STATS count = COUNT() BY BUCKET(@timestamp, 75, ?_tstart, ?_tend), host"
      },
      "x": { "column": "BUCKET(@timestamp, 75, ?_tstart, ?_tend)", "label": "@timestamp" },
      "y": [{ "column": "count" }],
      "breakdown_by": { "column": "host" }
    }
  ]
}
```

**Layer Types:**

- `bar` — Vertical bars
- `bar_stacked` — Stacked bars
- `bar_percentage` — Percentage bars
- `bar_horizontal` — Horizontal bars
- `bar_horizontal_stacked` — Horizontal stacked bars
- `bar_horizontal_percentage` — Horizontal percentage bars
- `line` — Line chart
- `area` — Area chart
- `area_stacked` — Stacked area
- `area_percentage` — Percentage area

## Gauge

For ES|QL, reference the query output column directly. Do not pass `min`/`max`/`goal` for ES|QL gauges — the API injects
defaults. Do **not** include `operation` in `metric` — it is not a valid property for gauge and will be rejected.

```json
{
  "type": "gauge",
  "data_source": {
    "type": "esql",
    "query": "FROM logs | STATS success_rate = COUNT(CASE(TO_INTEGER(status) == 200, 1, null)) * 100.0 / COUNT()"
  },
  "metric": { "column": "success_rate" }
}
```

**Gauge Properties:**

| Property        | Type   | Required | Description        |
| --------------- | ------ | -------- | ------------------ |
| `metric.column` | string | Yes      | ES\|QL column name |

## Heatmap

```json
{
  "type": "heatmap",
  "data_source": {
    "type": "esql",
    "query": "FROM kibana_sample_data_logs | STATS count = COUNT() BY hour = DATE_EXTRACT(\"hour_of_day\", @timestamp), day = DATE_EXTRACT(\"day_of_week\", @timestamp)"
  },
  "x": { "column": "hour" },
  "y": { "column": "day" },
  "metric": { "column": "count" }
}
```

## Tag Cloud

Uses `tag_by` for the tag dimension and `metric` for the value.

```json
{
  "type": "tag_cloud",
  "data_source": {
    "type": "esql",
    "query": "FROM logs | STATS count = COUNT() BY keyword"
  },
  "tag_by": { "column": "keyword" },
  "metric": { "column": "count" }
}
```

## Datatable

For ES|QL, uses `metrics` and `rows` arrays. Each entry uses `{ column: "..." }`.

```json
{
  "type": "data_table",
  "data_source": {
    "type": "esql",
    "query": "FROM logs | STATS count = COUNT(), avg_bytes = AVG(bytes) BY host"
  },
  "metrics": [{ "column": "count" }, { "column": "avg_bytes" }],
  "rows": [{ "column": "host" }]
}
```

**For dataView**, the datatable uses aggregation operations:

```json
{
  "type": "data_table",
  "data_source": { "type": "data_view_reference", "ref_id": "90943e30-9a47-11e8-b64d-95841ca0b247" },
  "metrics": [{ "operation": "count" }, { "operation": "average", "field": "bytes" }],
  "rows": [
    {
      "operation": "terms",
      "fields": ["host.keyword"],
      "limit": 15,
      "rank_by": { "type": "metric", "metric_index": 0, "direction": "desc" }
    }
  ]
}
```

## Partition (Pie, Treemap, Mosaic, Waffle)

Partition charts display parts of a whole. Uses a flat structure (no `layers`) with `metrics` for the slice sizes and
`group_by` for the rings or groupings. The schema is identical for all partition types—simply change `"type": "pie"` to
`"treemap"`, `"mosaic"`, or `"waffle"`. To create a donut, use `"type": "pie"` with `"styling": { "donut_hole": "m" }`.
Valid `donut_hole` values are `"none"`, `"s"`, `"m"`, or `"l"`.

**ES|QL Example:**

```json
{
  "type": "pie",
  "data_source": {
    "type": "esql",
    "query": "FROM logs | STATS count = COUNT() BY os"
  },
  "metrics": [{ "column": "count" }],
  "group_by": [{ "column": "os" }]
}
```

## Region Map

```json
{
  "type": "region_map",
  "data_source": {
    "type": "esql",
    "query": "FROM logs | STATS count = COUNT() BY geo.country_iso_code"
  },
  "region": { "column": "geo.country_iso_code" },
  "metric": { "column": "count" }
}
```

## Common Patterns

### Renaming Columns for Clarity

```json
{
  "type": "metric",
  "data_source": {
    "type": "esql",
    "query": "FROM logs | STATS total_events = COUNT(), error_count = COUNT(CASE(level == \"error\", 1, null)) | EVAL error_rate = ROUND(error_count * 100.0 / total_events, 2)"
  },
  "metrics": [{ "type": "primary", "column": "error_rate" }]
}
```

### Time Bucketing

**Auto buckets (Recommended):**

Do **not** reassign the BUCKET result. Use the full expression as both the `BY` clause and the `column` reference, with
a `label` for display:

```esql
WHERE @timestamp <= ?_tend AND @timestamp > ?_tstart | STATS count = COUNT() BY BUCKET(@timestamp, 75, ?_tstart, ?_tend)
```

```json
"x": { "column": "BUCKET(@timestamp, 75, ?_tstart, ?_tend)", "label": "@timestamp" }
```

**Important:** Always set `"scale": "temporal"` on the x-axis for time series charts. Without it, Kibana treats the
bucket column as categorical text and renders unsorted, verbose timestamp strings instead of a proper multilevel time
axis.

```json
"axis": {
  "x": { "scale": "temporal", "domain": { "type": "fit", "rounding": false } }
}
```

**Hourly buckets:**

```esql
STATS count = COUNT() BY bucket = DATE_TRUNC(1 hour, @timestamp)
```

**Daily buckets:**

```esql
STATS count = COUNT() BY bucket = DATE_TRUNC(1 day, @timestamp)
```

**5-minute buckets:**

```esql
STATS count = COUNT() BY bucket = DATE_TRUNC(5 minutes, @timestamp)
```

### Number Formatting

Use the `format` property on metrics, y-axis columns, and gauge metrics to display values with proper units.

| Format     | Properties                                                        | Example Output |
| ---------- | ----------------------------------------------------------------- | -------------- |
| `bytes`    | `{ "type": "bytes", "decimals": 0 }`                              | 5 KB, 19 KB    |
| `bits`     | `{ "type": "bits", "decimals": 1 }`                               | 40.2 kbit      |
| `number`   | `{ "type": "number", "decimals": 2, "compact": true }`            | 5.75K          |
| `percent`  | `{ "type": "percent", "decimals": 1 }`                            | 42.5%          |
| `duration` | `{ "type": "duration", "from": "milliseconds", "to": "seconds" }` | 1.5 s          |
| `custom`   | `{ "type": "custom", "pattern": "0,0.00" }`                       | 5,750.16       |

All formats accept an optional `"suffix"` (e.g., `" /s"` for rate displays).

**Percent formatting:** Two options depending on the value range. `"type": "percent"` expects a decimal fraction (0.425
→ 42.5%). `{ "type": "number", "decimals": 1, "suffix": "%" }` works when the value is already a whole-number percentage
(42.5 → 42.5%).

**dataView operation example:**

```json
{ "operation": "average", "field": "bytes", "format": { "type": "bytes", "decimals": 0 } }
```

**ES|QL column example:**

```json
{ "column": "avg_bytes", "format": { "type": "bytes", "decimals": 0 } }
```

**Gauge metric example:**

```json
"metric": { "operation": "max", "field": "bytes", "format": { "type": "bytes", "decimals": 0 } }
```

### Filtering in ES|QL

```esql
FROM logs
| WHERE @timestamp > NOW() - 24 hours AND level == "error"
| STATS count = COUNT() BY host
```
