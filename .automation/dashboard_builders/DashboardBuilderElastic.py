#!/usr/bin/env python3
"""
Elastic dashboard builder: Kibana saved objects (4 data views + 1 dashboard
with Lens panels) over the megalinter-runs/linters/rules/files indexes
written by ApiProviderElastic.
"""

import json

from dashboard_builders.contract import PAYLOAD_VERSION
from dashboard_builders.DashboardBuilder import DashboardBuilder


class DashboardBuilderElastic(DashboardBuilder):
    provider = "elastic"

    def build(self) -> dict:
        objects = [
            self.data_view("megalinter-runs"),
            self.data_view("megalinter-linters"),
            self.data_view("megalinter-rules"),
            self.data_view("megalinter-files"),
            self.dashboard(),
        ]
        ndjson = "\n".join([json.dumps(obj) for obj in objects]) + "\n"
        return {"elastic/megalinter-dashboards.ndjson": ndjson}

    def manifest_entries(self) -> list:
        return [
            {
                "provider": "elastic",
                "file": "elastic/megalinter-dashboards.ndjson",
                "title": "MegaLinter - Overview",
            }
        ]

    def data_view(self, index_name):
        return {
            "id": index_name,
            "type": "index-pattern",
            "attributes": {
                "title": index_name,
                "name": index_name,
                "timeFieldName": "@timestamp",
            },
            "references": [],
            "managed": False,
            "coreMigrationVersion": "8.8.0",
            "typeMigrationVersion": "8.0.0",
        }

    # Value-conditional palette for Lens metric panels
    def metric_palette(self, stops, range_max):
        color_stops = [{"color": color, "stop": stop} for color, stop in stops]
        return {
            "type": "palette",
            "name": "custom",
            "params": {
                "name": "custom",
                "steps": len(color_stops),
                "stops": [
                    {"color": color, "stop": stop}
                    for color, stop in [
                        (
                            stops[i][0],
                            stops[i + 1][1] if i + 1 < len(stops) else range_max,
                        )
                        for i in range(len(stops))
                    ]
                ],
                "colorStops": color_stops,
                "rangeType": "number",
                "rangeMin": stops[0][1],
                "rangeMax": range_max,
                "continuity": "above",
                "reverse": False,
            },
        }

    def health_palette(self):
        return self.metric_palette(
            [("#cc5642", 0), ("#d6bf57", 50), ("#209280", 80)], 100
        )

    def errors_palette(self):
        return self.metric_palette([("#209280", 0), ("#cc5642", 1)], 10000)

    def warning_palette(self):
        return self.metric_palette([("#209280", 0), ("#d6bf57", 1)], 10000)

    def lens_metric_panel(
        self, panel_index, title, index, field, agg="sum", palette=None
    ):
        layer_id = f"layer-{panel_index}"
        column_id = f"col-{panel_index}"
        visualization_state = {
            "layerId": layer_id,
            "layerType": "data",
            "metricAccessor": column_id,
        }
        if palette is not None:
            visualization_state["palette"] = palette
        return {
            "type": "lens",
            "gridData": {},
            "panelIndex": panel_index,
            "embeddableConfig": {
                "attributes": {
                    "title": title,
                    "visualizationType": "lnsMetric",
                    "type": "lens",
                    "references": [
                        {
                            "type": "index-pattern",
                            "id": index,
                            "name": f"indexpattern-datasource-layer-{layer_id}",
                        }
                    ],
                    "state": {
                        "visualization": visualization_state,
                        "query": {"query": "", "language": "kuery"},
                        "filters": [],
                        "datasourceStates": {
                            "formBased": {
                                "layers": {
                                    layer_id: {
                                        "columns": {
                                            column_id: {
                                                "label": title,
                                                "dataType": "number",
                                                "operationType": agg,
                                                "sourceField": field,
                                                "isBucketed": False,
                                                "scale": "ratio",
                                                "params": {"emptyAsNull": False},
                                            }
                                        },
                                        "columnOrder": [column_id],
                                        "incompleteColumns": {},
                                    }
                                }
                            }
                        },
                    },
                },
                "enhancements": {},
            },
        }

    def lens_top_values_panel(
        self, panel_index, title, index, group_field, metric_field
    ):
        layer_id = f"layer-{panel_index}"
        col_group = f"col-{panel_index}-group"
        col_metric = f"col-{panel_index}-metric"
        return {
            "type": "lens",
            "gridData": {},
            "panelIndex": panel_index,
            "embeddableConfig": {
                "attributes": {
                    "title": title,
                    "visualizationType": "lnsXY",
                    "type": "lens",
                    "references": [
                        {
                            "type": "index-pattern",
                            "id": index,
                            "name": f"indexpattern-datasource-layer-{layer_id}",
                        }
                    ],
                    "state": {
                        "visualization": {
                            "legend": {"isVisible": True, "position": "right"},
                            "preferredSeriesType": "bar_horizontal",
                            "layers": [
                                {
                                    "layerId": layer_id,
                                    "layerType": "data",
                                    "seriesType": "bar_horizontal",
                                    "xAccessor": col_group,
                                    "accessors": [col_metric],
                                }
                            ],
                        },
                        "query": {"query": "", "language": "kuery"},
                        "filters": [],
                        "datasourceStates": {
                            "formBased": {
                                "layers": {
                                    layer_id: {
                                        "columns": {
                                            col_group: {
                                                "label": group_field,
                                                "dataType": "string",
                                                "operationType": "terms",
                                                "sourceField": group_field,
                                                "isBucketed": True,
                                                "scale": "ordinal",
                                                "params": {
                                                    "size": 15,
                                                    "orderBy": {
                                                        "type": "column",
                                                        "columnId": col_metric,
                                                    },
                                                    "orderDirection": "desc",
                                                    "otherBucket": False,
                                                    "missingBucket": False,
                                                    "parentFormat": {"id": "terms"},
                                                },
                                            },
                                            col_metric: {
                                                "label": f"Sum of {metric_field}",
                                                "dataType": "number",
                                                "operationType": "sum",
                                                "sourceField": metric_field,
                                                "isBucketed": False,
                                                "scale": "ratio",
                                                "params": {"emptyAsNull": False},
                                            },
                                        },
                                        "columnOrder": [col_group, col_metric],
                                        "incompleteColumns": {},
                                    }
                                }
                            }
                        },
                    },
                },
                "enhancements": {},
            },
        }

    def lens_date_histogram_panel(
        self, panel_index, title, index, fields, split_field=None
    ):
        layer_id = f"layer-{panel_index}"
        col_date = f"col-{panel_index}-date"
        metric_columns = {}
        for field_index, field_def in enumerate(fields):
            field, label = field_def[0], field_def[1]
            agg = field_def[2] if len(field_def) > 2 else "sum"
            metric_columns[f"col-{panel_index}-m{field_index}"] = {
                "label": label,
                "dataType": "number",
                "operationType": agg,
                "sourceField": field,
                "isBucketed": False,
                "scale": "ratio",
                "params": {"emptyAsNull": False},
            }
        split_columns = {}
        col_split = f"col-{panel_index}-split"
        if split_field is not None:
            split_columns[col_split] = {
                "label": split_field,
                "dataType": "string",
                "operationType": "terms",
                "sourceField": split_field,
                "isBucketed": True,
                "scale": "ordinal",
                "params": {
                    "size": 10,
                    "orderBy": {
                        "type": "column",
                        "columnId": list(metric_columns.keys())[0],
                    },
                    "orderDirection": "desc",
                    "otherBucket": False,
                    "missingBucket": False,
                    "parentFormat": {"id": "terms"},
                },
            }
        return {
            "type": "lens",
            "gridData": {},
            "panelIndex": panel_index,
            "embeddableConfig": {
                "attributes": {
                    "title": title,
                    "visualizationType": "lnsXY",
                    "type": "lens",
                    "references": [
                        {
                            "type": "index-pattern",
                            "id": index,
                            "name": f"indexpattern-datasource-layer-{layer_id}",
                        }
                    ],
                    "state": {
                        "visualization": {
                            "legend": {"isVisible": True, "position": "right"},
                            "preferredSeriesType": "line",
                            "layers": [
                                {
                                    "layerId": layer_id,
                                    "layerType": "data",
                                    "seriesType": "line",
                                    "xAccessor": col_date,
                                    "accessors": list(metric_columns.keys()),
                                    **(
                                        {"splitAccessor": col_split}
                                        if split_field is not None
                                        else {}
                                    ),
                                }
                            ],
                        },
                        "query": {"query": "", "language": "kuery"},
                        "filters": [],
                        "datasourceStates": {
                            "formBased": {
                                "layers": {
                                    layer_id: {
                                        "columns": {
                                            col_date: {
                                                "label": "@timestamp",
                                                "dataType": "date",
                                                "operationType": "date_histogram",
                                                "sourceField": "@timestamp",
                                                "isBucketed": True,
                                                "scale": "interval",
                                                "params": {
                                                    "interval": "auto",
                                                    "includeEmptyRows": True,
                                                },
                                            },
                                            **split_columns,
                                            **metric_columns,
                                        },
                                        "columnOrder": list(split_columns.keys())
                                        + [col_date]
                                        + list(metric_columns.keys()),
                                        "incompleteColumns": {},
                                    }
                                }
                            }
                        },
                    },
                },
                "enhancements": {},
            },
        }

    def lens_pie_panel(self, panel_index, title, index, group_field):
        layer_id = f"layer-{panel_index}"
        col_group = f"col-{panel_index}-group"
        col_metric = f"col-{panel_index}-metric"
        return {
            "type": "lens",
            "gridData": {},
            "panelIndex": panel_index,
            "embeddableConfig": {
                "attributes": {
                    "title": title,
                    "visualizationType": "lnsPie",
                    "type": "lens",
                    "references": [
                        {
                            "type": "index-pattern",
                            "id": index,
                            "name": f"indexpattern-datasource-layer-{layer_id}",
                        }
                    ],
                    "state": {
                        "visualization": {
                            "shape": "donut",
                            "layers": [
                                {
                                    "layerId": layer_id,
                                    "layerType": "data",
                                    "primaryGroups": [col_group],
                                    "metrics": [col_metric],
                                    "numberDisplay": "value",
                                    "categoryDisplay": "default",
                                    "legendDisplay": "default",
                                }
                            ],
                        },
                        "query": {"query": "", "language": "kuery"},
                        "filters": [],
                        "datasourceStates": {
                            "formBased": {
                                "layers": {
                                    layer_id: {
                                        "columns": {
                                            col_group: {
                                                "label": group_field,
                                                "dataType": "string",
                                                "operationType": "terms",
                                                "sourceField": group_field,
                                                "isBucketed": True,
                                                "scale": "ordinal",
                                                "params": {
                                                    "size": 5,
                                                    "orderBy": {
                                                        "type": "column",
                                                        "columnId": col_metric,
                                                    },
                                                    "orderDirection": "desc",
                                                    "otherBucket": False,
                                                    "missingBucket": False,
                                                    "parentFormat": {"id": "terms"},
                                                },
                                            },
                                            col_metric: {
                                                "label": "Count",
                                                "dataType": "number",
                                                "operationType": "count",
                                                "sourceField": "___records___",
                                                "isBucketed": False,
                                                "scale": "ratio",
                                                "params": {"emptyAsNull": False},
                                            },
                                        },
                                        "columnOrder": [col_group, col_metric],
                                        "incompleteColumns": {},
                                    }
                                }
                            }
                        },
                    },
                },
                "enhancements": {},
            },
        }

    def markdown_panel(self, panel_index, markdown):
        return {
            "type": "visualization",
            "gridData": {},
            "panelIndex": panel_index,
            "embeddableConfig": {
                "savedVis": {
                    "title": "",
                    "description": "",
                    "type": "markdown",
                    "params": {
                        "markdown": markdown,
                        "openLinksInNewTab": False,
                        "fontSize": 12,
                    },
                    "uiState": {},
                    "data": {"aggs": [], "searchSource": {}},
                },
                "enhancements": {},
            },
        }

    def dashboard(self):
        panels = [
            self.lens_metric_panel(
                "p1",
                "Blocking errors (sum)",
                "megalinter-runs",
                "run.blockingErrors",
                palette=self.errors_palette(),
            ),
            self.lens_metric_panel(
                "p2",
                "Non-blocking errors (sum)",
                "megalinter-runs",
                "run.nonBlockingErrors",
                palette=self.warning_palette(),
            ),
            self.lens_metric_panel(
                "p3",
                "Errors auto-fixed (sum)",
                "megalinter-runs",
                "run.totalErrorsFixed",
            ),
            self.lens_metric_panel(
                "p4",
                "Runs analyzed",
                "megalinter-runs",
                "run.lintersCount",
                agg="count",
            ),
            self.lens_top_values_panel(
                "p5",
                "Errors by linter",
                "megalinter-linters",
                "linterKey.keyword",
                "data.numberErrorsFound",
            ),
            self.lens_top_values_panel(
                "p6",
                "Top rules",
                "megalinter-rules",
                "ruleId.keyword",
                "occurrences",
            ),
            self.lens_top_values_panel(
                "p7",
                "Top files",
                "megalinter-files",
                "file.keyword",
                "occurrences",
            ),
            self.lens_top_values_panel(
                "p8",
                "Errors by repository",
                "megalinter-linters",
                "gitRepoName.keyword",
                "data.numberErrorsFound",
            ),
            self.lens_date_histogram_panel(
                "p9",
                "Errors over time",
                "megalinter-runs",
                [
                    ("run.blockingErrors", "Blocking errors"),
                    ("run.nonBlockingErrors", "Non-blocking errors"),
                ],
            ),
            self.lens_pie_panel(
                "p10",
                "Quality gate distribution",
                "megalinter-runs",
                "run.qualityGateStatus.keyword",
            ),
            self.lens_top_values_panel(
                "p11",
                "Slowest linters (total elapsed s)",
                "megalinter-linters",
                "linterKey.keyword",
                "data.elapsedTime",
            ),
            self.lens_date_histogram_panel(
                "p12",
                "Errors auto-fixed over time",
                "megalinter-runs",
                [("run.totalErrorsFixed", "Errors auto-fixed")],
            ),
            self.lens_metric_panel(
                "p13",
                "Health score (avg)",
                "megalinter-runs",
                "run.healthScore",
                agg="average",
                palette=self.health_palette(),
            ),
            self.lens_date_histogram_panel(
                "p14",
                "Repository health score evolution",
                "megalinter-runs",
                [("run.healthScore", "Health score", "average")],
                split_field="gitRepoName.keyword",
            ),
            self.lens_date_histogram_panel(
                "p15",
                "Errors by language over time",
                "megalinter-linters",
                [("data.numberErrorsFound", "Errors", "sum")],
                split_field="descriptor.keyword",
            ),
            self.lens_date_histogram_panel(
                "p16",
                "Errors by linter over time",
                "megalinter-linters",
                [("data.numberErrorsFound", "Errors", "sum")],
                split_field="linterKey.keyword",
            ),
            self.markdown_panel(
                "p17",
                "## How the rating / health score is computed\\n\\nHealth score (0-100) = `100 x (linters in "
                "success + 0.5 x linters with non-blocking errors) / total linters`\\n\\nA >= 90 | B >= 80 | "
                "C >= 65 | D >= 50 | E < 50\\n\\nTo improve it: fix the linters in error first (full share "
                "each), then the warnings (half share each). Click any bar to filter the dashboard, or use "
                "the filter bar (e.g. `gitRepoName: myrepo`).",
            ),
            self.lens_metric_panel(
                "p18",
                "Linters in success (latest runs)",
                "megalinter-runs",
                "run.lintersSuccess",
                agg="max",
            ),
            self.lens_metric_panel(
                "p19",
                "Linters with warnings (0.5 share)",
                "megalinter-runs",
                "run.lintersWarning",
                agg="max",
                palette=self.warning_palette(),
            ),
            self.lens_metric_panel(
                "p20",
                "Linters in error (0 share)",
                "megalinter-runs",
                "run.lintersError",
                agg="max",
                palette=self.errors_palette(),
            ),
        ]
        grid = [
            {"x": 0, "y": 0, "w": 12, "h": 8, "i": "p1"},
            {"x": 12, "y": 0, "w": 12, "h": 8, "i": "p2"},
            {"x": 24, "y": 0, "w": 12, "h": 8, "i": "p3"},
            {"x": 36, "y": 0, "w": 12, "h": 8, "i": "p4"},
            {"x": 0, "y": 20, "w": 24, "h": 12, "i": "p5"},
            {"x": 24, "y": 20, "w": 24, "h": 12, "i": "p6"},
            {"x": 0, "y": 32, "w": 24, "h": 12, "i": "p7"},
            {"x": 24, "y": 32, "w": 24, "h": 12, "i": "p8"},
            {"x": 0, "y": 8, "w": 24, "h": 12, "i": "p9"},
            {"x": 24, "y": 8, "w": 12, "h": 12, "i": "p10"},
            {"x": 0, "y": 44, "w": 24, "h": 12, "i": "p11"},
            {"x": 24, "y": 44, "w": 24, "h": 12, "i": "p12"},
            {"x": 36, "y": 8, "w": 12, "h": 12, "i": "p13"},
            {"x": 0, "y": 56, "w": 48, "h": 12, "i": "p14"},
            {"x": 0, "y": 68, "w": 24, "h": 12, "i": "p15"},
            {"x": 24, "y": 68, "w": 24, "h": 12, "i": "p16"},
            {"x": 0, "y": 80, "w": 24, "h": 10, "i": "p17"},
            {"x": 24, "y": 80, "w": 8, "h": 10, "i": "p18"},
            {"x": 32, "y": 80, "w": 8, "h": 10, "i": "p19"},
            {"x": 40, "y": 80, "w": 8, "h": 10, "i": "p20"},
        ]
        for panel, grid_data in zip(panels, grid):
            panel["gridData"] = grid_data
        references = []
        for panel in panels:
            attributes = panel["embeddableConfig"].get("attributes", {})
            for ref in attributes.get("references", []):
                references.append(
                    {
                        "type": "index-pattern",
                        "id": ref["id"],
                        "name": f"{panel['panelIndex']}:{ref['name']}",
                    }
                )
        return {
            "id": "megalinter-overview",
            "type": "dashboard",
            "attributes": {
                "title": "MegaLinter - Overview",
                "description": (
                    "MegaLinter results: errors, linters, top rules and files. "
                    f"Generated from MegaLinter payload v{PAYLOAD_VERSION}."
                ),
                "timeRestore": True,
                "timeFrom": "now-30d",
                "timeTo": "now",
                "refreshInterval": {"pause": True, "value": 60000},
                "panelsJSON": json.dumps(panels),
                "optionsJSON": json.dumps(
                    {
                        "useMargins": True,
                        "syncColors": False,
                        "hidePanelTitles": False,
                    }
                ),
                "kibanaSavedObjectMeta": {
                    "searchSourceJSON": json.dumps(
                        {"query": {"query": "", "language": "kuery"}, "filter": []}
                    )
                },
            },
            "references": references,
            "managed": False,
            "coreMigrationVersion": "8.8.0",
            "typeMigrationVersion": "10.2.0",
        }
