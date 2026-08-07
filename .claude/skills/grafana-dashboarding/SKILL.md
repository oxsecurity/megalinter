---
name: grafana-dashboarding
license: Apache-2.0
metadata:
  internal: true
  author: Grafana Labs
  source: https://github.com/grafana/skills (skills/grafana-core/dashboarding)
description: Build, modify, and ship Grafana dashboards as JSON via the HTTP API — panel types (timeseries / stat / gauge / table / heatmap / logs / traces / node-graph), `gridPos` 24-column layout, units, thresholds, template + datasource + chained variables, transformations (`organize` / `calculateField` / `filterByValue`), panel + dashboard links with `${__field.labels.x}` / `${__from}`, and Loki/Prometheus annotations. Use when scripting dashboard creation, writing the dashboard JSON for a new service, adding a `$job` dropdown variable, computing an "Error %" column with a transformation, overlaying deploys as annotations, or pushing a dashboard via `POST /api/dashboards/db` — even when the user says "create a dashboard for this metric", "add a service dropdown", "show errors as percentage", "overlay our deploys", or "export the dashboard JSON" without naming the API or schema. After every API push, verify with the returned `version` plus a GET on the dashboard UID.
---

# Grafana Dashboard Authoring

> **Docs**: <https://grafana.com/docs/grafana/latest/dashboards/>

Dashboards are JSON. Author once, push via API, share by `uid`.

## Prerequisites

- Grafana stack (OSS, Enterprise, or Cloud) reachable from your machine
- API token with `dashboards:write` (`Authorization: Bearer <token>`)
- `jq` for inspecting responses
- The JSON-schema cheat sheet in [`references/json-schema.md`](references/json-schema.md)

## Common Workflows

### 1. Push a new dashboard via the API + verify

```bash
# 1. Build the payload — wrap the dashboard JSON, set folder, mark overwrite
cat > /tmp/dash.json <<'JSON'
{
  "dashboard": {
    "uid": "demo-svc-v1",
    "title": "Demo Service",
    "schemaVersion": 41,
    "tags": ["demo"],
    "time": { "from": "now-1h", "to": "now" },
    "templating": { "list": [] },
    "panels": [{
      "id": 1, "type": "timeseries", "title": "Request Rate",
      "gridPos": { "x": 0, "y": 0, "w": 24, "h": 8 },
      "datasource": { "type": "prometheus", "uid": "prometheus" },
      "targets": [{
        "expr": "sum(rate(http_requests_total[5m])) by (status_code)",
        "legendFormat": "{{status_code}}", "refId": "A"
      }],
      "fieldConfig": { "defaults": { "unit": "reqps" }, "overrides": [] }
    }]
  },
  "folderUid": "",
  "overwrite": true,
  "message": "initial push"
}
JSON

# 2. Validate the JSON BEFORE you send it (catches trailing-comma typos)
jq empty /tmp/dash.json && echo "json ok"

# 3. POST
RESP=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "$GRAFANA/api/dashboards/db" -d @/tmp/dash.json)
echo "$RESP" | jq '{status, uid, url, version}'
# Expect: status="success", url="/d/demo-svc-v1/...", version=1 (incremented on each push)

# 4. Verify the round-trip — read it back and confirm one panel + the expected title
curl -s -H "Authorization: Bearer $TOKEN" \
  "$GRAFANA/api/dashboards/uid/demo-svc-v1" \
  | jq '{title: .dashboard.title, panels: (.dashboard.panels | length)}'
# Expect: {"title":"Demo Service","panels":1}

# 5. Open the dashboard in a browser — confirm the panel renders with data.
```

### 2. Add a `$job` template variable to an existing dashboard

```bash
# 1. Fetch existing dashboard
curl -s -H "Authorization: Bearer $TOKEN" \
  "$GRAFANA/api/dashboards/uid/demo-svc-v1" > /tmp/dash.json

# 2. Edit templating.list — append:
#   { "name":"job", "type":"query",
#     "datasource":{"type":"prometheus","uid":"prometheus"},
#     "query":{"query":"label_values(up, job)","refId":"A"},
#     "refresh":2, "includeAll":true, "multi":true, "label":"Service" }
#  (Use jq, an editor, or the Grafana UI — schema in references/json-schema.md.)

# 3. Update the panel expr to use the variable: rate(http_requests_total{job=~"$job"}[5m])

# 4. POST it back with overwrite: true. Verify the variable appears in the UI dropdown.
```

### 3. Compute an "Error %" column with a transformation

```json
{
  "id": "calculateField",
  "options": {
    "alias": "Error %", "mode": "reduceRow",
    "reduce": { "reducer": "last" },
    "binary": { "left": "errors", "right": "total", "operator": "/" }
  }
}
```

Add this to the panel's `transformations: []`. Verify in the UI panel inspector — the new field should appear and update with the variable selection.

Full schema (panels, units, all transformations, annotations, links): [`references/json-schema.md`](references/json-schema.md).

## API reference

```bash
# Get
curl -s -H "Authorization: Bearer $TOKEN" \
  "$GRAFANA/api/dashboards/uid/<uid>" | jq '.dashboard'

# Search
curl -s -H "Authorization: Bearer $TOKEN" \
  "$GRAFANA/api/search?query=kubernetes&type=dash-db" | jq '.[] | {uid,title,folderTitle}'

# Create folder
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" "$GRAFANA/api/folders" \
  -d '{"uid":"platform-team","title":"Platform Team"}'
```

For dashboards embedded in app plugins, use `@grafana/scenes` (skill `grafana-o11y:grafana-scenes`).

## Resources

- [Dashboard JSON model](https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/view-dashboard-json-model/)
- [HTTP API — dashboards](https://grafana.com/docs/grafana/latest/developers/http_api/dashboard/)
- [Panel types](https://grafana.com/docs/grafana/latest/panels-visualizations/)
- [Variables](https://grafana.com/docs/grafana/latest/dashboards/variables/)
- [Transformations](https://grafana.com/docs/grafana/latest/panels-visualizations/query-transform-data/transform-data/)
