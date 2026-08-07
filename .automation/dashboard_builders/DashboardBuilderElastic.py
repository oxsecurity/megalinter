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
                # Wildcard so rollover/suffixed indices still match
                "title": f"{index_name}*",
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

    # Stops aligned on the rating bands: E < 50, D >= 50, C >= 65, B >= 80, A >= 90
    def health_palette(self):
        return self.metric_palette(
            [
                ("#cc5642", 0),
                ("#e7854d", 50),
                ("#d6bf57", 65),
                ("#8bc167", 80),
                ("#209280", 90),
            ],
            100,
        )

    def errors_palette(self):
        return self.metric_palette([("#209280", 0), ("#cc5642", 1)], 10000)

    def warning_palette(self):
        return self.metric_palette([("#209280", 0), ("#d6bf57", 1)], 10000)

    def lens_metric_panel(
        self,
        panel_index,
        title,
        index,
        field,
        agg="sum",
        palette=None,
        op_params=None,
        fmt=None,
    ):
        layer_id = f"layer-{panel_index}"
        column_id = f"col-{panel_index}"
        column_params = (
            dict(op_params) if op_params is not None else {"emptyAsNull": False}
        )
        if fmt is not None:
            column_params["format"] = fmt
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
                                                "params": column_params,
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

    # Lens formula column exported as formula + hidden aggregation (X0) and
    # math (X1) helper columns, per the Kibana saved-object format
    def lens_formula_metric_panel(
        self, panel_index, title, index, agg, field, multiplier, fmt=None
    ):
        layer_id = f"layer-{panel_index}"
        column_id = f"col-{panel_index}"
        col_x0 = f"{column_id}X0"
        col_x1 = f"{column_id}X1"
        formula = f"{agg}({field}) * {multiplier}"
        formula_params = {"formula": formula, "isFormulaBroken": False}
        if fmt is not None:
            formula_params["format"] = fmt
        columns = {
            col_x0: {
                "label": f"Part of {formula}",
                "dataType": "number",
                "operationType": agg,
                "sourceField": field,
                "isBucketed": False,
                "scale": "ratio",
                "params": {"emptyAsNull": False},
                "customLabel": True,
            },
            col_x1: {
                "label": f"Part of {formula}",
                "dataType": "number",
                "operationType": "math",
                "isBucketed": False,
                "scale": "ratio",
                "params": {
                    "tinymathAst": {
                        "type": "function",
                        "name": "multiply",
                        "args": [col_x0, multiplier],
                        "location": {"min": 0, "max": len(formula)},
                        "text": formula,
                    }
                },
                "references": [col_x0],
                "customLabel": True,
            },
            column_id: {
                "label": title,
                "dataType": "number",
                "operationType": "formula",
                "isBucketed": False,
                "scale": "ratio",
                "params": formula_params,
                "references": [col_x1],
                "customLabel": True,
            },
        }
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
                        "visualization": {
                            "layerId": layer_id,
                            "layerType": "data",
                            "metricAccessor": column_id,
                        },
                        "query": {"query": "", "language": "kuery"},
                        "filters": [],
                        "datasourceStates": {
                            "formBased": {
                                "layers": {
                                    layer_id: {
                                        "columns": columns,
                                        "columnOrder": [column_id, col_x0, col_x1],
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
        self,
        panel_index,
        title,
        index,
        group_field,
        metric_field,
        group_label=None,
        metric_agg="sum",
        metric_label=None,
        metric_format=None,
    ):
        layer_id = f"layer-{panel_index}"
        col_group = f"col-{panel_index}-group"
        col_metric = f"col-{panel_index}-metric"
        metric_params = {"emptyAsNull": False}
        if metric_format is not None:
            metric_params["format"] = metric_format
        group_column = {
            "label": group_label if group_label is not None else group_field,
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
        }
        if group_label is not None:
            group_column["customLabel"] = True
        metric_column = {
            "label": (
                metric_label if metric_label is not None else f"Sum of {metric_field}"
            ),
            "dataType": "number",
            "operationType": metric_agg,
            "sourceField": metric_field,
            "isBucketed": False,
            "scale": "ratio",
            "params": metric_params,
        }
        if metric_label is not None:
            metric_column["customLabel"] = True
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
                                            col_group: group_column,
                                            col_metric: metric_column,
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
        self, panel_index, title, index, fields, split_field=None, split_label=None
    ):
        layer_id = f"layer-{panel_index}"
        col_date = f"col-{panel_index}-date"
        metric_columns = {}
        for field_index, field_def in enumerate(fields):
            field, label = field_def[0], field_def[1]
            agg = field_def[2] if len(field_def) > 2 else "sum"
            metric_params = {"emptyAsNull": False}
            if len(field_def) > 3 and field_def[3] is not None:
                metric_params["format"] = field_def[3]
            metric_columns[f"col-{panel_index}-m{field_index}"] = {
                "label": label,
                "dataType": "number",
                "operationType": agg,
                "sourceField": field,
                "isBucketed": False,
                "scale": "ratio",
                "params": metric_params,
            }
        split_columns = {}
        col_split = f"col-{panel_index}-split"
        if split_field is not None:
            split_columns[col_split] = {
                "label": split_label if split_label is not None else split_field,
                "dataType": "string",
                "operationType": "terms",
                "sourceField": split_field,
                "isBucketed": True,
                "scale": "ordinal",
                **({"customLabel": True} if split_label is not None else {}),
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

    def lens_pie_panel(
        self, panel_index, title, index, group_field, color_mapping=None
    ):
        layer_id = f"layer-{panel_index}"
        col_group = f"col-{panel_index}-group"
        col_metric = f"col-{panel_index}-metric"
        layer = {
            "layerId": layer_id,
            "layerType": "data",
            "primaryGroups": [col_group],
            "metrics": [col_metric],
            "numberDisplay": "value",
            "categoryDisplay": "default",
            "legendDisplay": "default",
        }
        if color_mapping is not None:
            layer["colorMapping"] = color_mapping
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
                            "layers": [layer],
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

    # Pin semantic colors on terms values (Lens colorMapping for categorical data)
    def terms_color_mapping(self, value_colors):
        return {
            "assignments": [
                {
                    "rule": {"type": "matchExactly", "values": [value]},
                    "color": {"type": "colorCode", "colorCode": color},
                    "touched": True,
                }
                for value, color in value_colors
            ],
            "specialAssignments": [
                {
                    "rule": {"type": "other"},
                    "color": {"type": "loop"},
                    "touched": False,
                }
            ],
            "paletteId": "eui_amsterdam_color_blind",
            "colorMode": {"type": "categorical"},
        }

    def lens_datatable_panel(
        self,
        panel_index,
        title,
        index,
        groups,
        metric_field,
        metric_label,
        metric_agg="sum",
        query="",
    ):
        layer_id = f"layer-{panel_index}"
        col_metric = f"col-{panel_index}-metric"
        group_columns = {}
        for group_index, (field, label, size) in enumerate(groups):
            group_columns[f"col-{panel_index}-g{group_index}"] = {
                "label": label,
                "dataType": "string",
                "operationType": "terms",
                "sourceField": field,
                "isBucketed": True,
                "scale": "ordinal",
                "customLabel": True,
                "params": {
                    "size": size,
                    "orderBy": {
                        "type": "column",
                        "columnId": col_metric,
                    },
                    "orderDirection": "desc",
                    "otherBucket": False,
                    "missingBucket": False,
                    "parentFormat": {"id": "terms"},
                },
            }
        metric_column = {
            "label": metric_label,
            "dataType": "number",
            "operationType": metric_agg,
            "sourceField": metric_field,
            "isBucketed": False,
            "scale": "ratio",
            "customLabel": True,
            "params": {"emptyAsNull": False},
        }
        column_order = list(group_columns.keys()) + [col_metric]
        return {
            "type": "lens",
            "gridData": {},
            "panelIndex": panel_index,
            "embeddableConfig": {
                "attributes": {
                    "title": title,
                    "visualizationType": "lnsDatatable",
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
                            "layerId": layer_id,
                            "layerType": "data",
                            "columns": [
                                {"columnId": column_id} for column_id in column_order
                            ],
                        },
                        "query": {"query": query, "language": "kuery"},
                        "filters": [],
                        "datasourceStates": {
                            "formBased": {
                                "layers": {
                                    layer_id: {
                                        "columns": {
                                            **group_columns,
                                            col_metric: metric_column,
                                        },
                                        "columnOrder": column_order,
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
        last_value_params = {"sortField": "@timestamp", "showArrayValues": False}
        seconds_format = {"id": "number", "params": {"decimals": 1, "suffix": " s"}}
        score_format = {"id": "number", "params": {"decimals": 0}}
        panels = [
            self.markdown_panel(
                "p0",
                "**MegaLinter Observability** | "
                "[Documentation](https://megalinter.io/latest/observability/elastic/) | Click any bar to "
                "filter the dashboard, use the filter bar for KQL (e.g. `gitRepoName: myrepo` or "
                "`gitBranchName: main`), and scroll down to the *rating explanation* section to understand "
                "the health score.",
            ),
            self.lens_metric_panel(
                "p1",
                "Blocking errors (latest run)",
                "megalinter-runs",
                "run.blockingErrors",
                agg="last_value",
                palette=self.errors_palette(),
                op_params=last_value_params,
            ),
            self.lens_metric_panel(
                "p2",
                "Non-blocking errors (latest run)",
                "megalinter-runs",
                "run.nonBlockingErrors",
                agg="last_value",
                palette=self.warning_palette(),
                op_params=last_value_params,
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
                "___records___",
                agg="count",
            ),
            self.lens_formula_metric_panel(
                "p21",
                "Time saved by auto-fixes (min, 5 min/fix)",
                "megalinter-runs",
                "sum",
                "run.totalErrorsFixed",
                5,
                fmt=score_format,
            ),
            self.lens_metric_panel(
                "p23",
                "Files analyzed (latest run)",
                "megalinter-runs",
                "run.filesAnalyzed",
                agg="last_value",
                op_params=last_value_params,
            ),
            self.lens_top_values_panel(
                "p5",
                "Errors by linter",
                "megalinter-linters",
                "linterKey.keyword",
                "data.numberErrorsFound",
                group_label="Linter",
                metric_label="Errors",
            ),
            self.lens_top_values_panel(
                "p6",
                "Top rules",
                "megalinter-rules",
                "ruleId.keyword",
                "occurrences",
                group_label="Rule",
                metric_label="Occurrences",
            ),
            self.lens_top_values_panel(
                "p7",
                "Top files",
                "megalinter-files",
                "file.keyword",
                "occurrences",
                group_label="File",
                metric_label="Occurrences",
            ),
            self.lens_top_values_panel(
                "p8",
                "Errors by repository",
                "megalinter-linters",
                "gitRepoName.keyword",
                "data.numberErrorsFound",
                group_label="Repository",
                metric_label="Errors",
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
                color_mapping=self.terms_color_mapping(
                    [("pass", "#209280"), ("fail", "#cc5642")]
                ),
            ),
            self.lens_top_values_panel(
                "p11",
                "Slowest linters (avg s)",
                "megalinter-linters",
                "linterKey.keyword",
                "data.elapsedTime",
                group_label="Linter",
                metric_agg="average",
                metric_label="Avg elapsed time",
                metric_format=seconds_format,
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
                fmt=score_format,
            ),
            self.lens_date_histogram_panel(
                "p14",
                "Repository health score evolution",
                "megalinter-runs",
                [("run.healthScore", "Health score", "average", score_format)],
                split_field="gitRepoName.keyword",
                split_label="Repository",
            ),
            self.lens_date_histogram_panel(
                "p15",
                "Errors by language over time",
                "megalinter-linters",
                [("data.numberErrorsFound", "Errors", "sum")],
                split_field="descriptor.keyword",
                split_label="Language",
            ),
            self.lens_date_histogram_panel(
                "p16",
                "Errors by linter over time",
                "megalinter-linters",
                [("data.numberErrorsFound", "Errors", "sum")],
                split_field="linterKey.keyword",
                split_label="Linter",
            ),
            self.markdown_panel(
                "p17",
                "## How the rating / health score is computed\n\nHealth score (0-100) = `100 x (linters in "
                "success + 0.5 x linters with non-blocking errors) / total linters`\n\nA >= 90 | B >= 80 | "
                "C >= 65 | D >= 50 | E < 50\n\nTo improve it: fix the linters in error first (full share "
                "each), then the warnings (half share each). Click any bar to filter the dashboard, or use "
                "the filter bar (e.g. `gitRepoName: myrepo`).",
            ),
            self.lens_metric_panel(
                "p18",
                "Linters in success (latest run)",
                "megalinter-runs",
                "run.lintersSuccess",
                agg="last_value",
                op_params=last_value_params,
            ),
            self.lens_metric_panel(
                "p19",
                "Linters with warnings (0.5 share)",
                "megalinter-runs",
                "run.lintersWarning",
                agg="last_value",
                palette=self.warning_palette(),
                op_params=last_value_params,
            ),
            self.lens_metric_panel(
                "p20",
                "Linters in error (0 share)",
                "megalinter-runs",
                "run.lintersError",
                agg="last_value",
                palette=self.errors_palette(),
                op_params=last_value_params,
            ),
            self.lens_datatable_panel(
                "p22",
                "Linters dragging the score down",
                "megalinter-linters",
                [
                    ("linterKey.keyword", "Linter", 15),
                    ("data.severity.keyword", "Severity", 3),
                ],
                "data.numberErrorsFound",
                "Errors",
                query='data.severity: "error" or data.severity: "warning"',
            ),
            self.lens_datatable_panel(
                "p24",
                "MegaLinter versions in use",
                "megalinter-runs",
                [
                    ("megalinterVersion.keyword", "Version", 10),
                    ("megalinterFlavor.keyword", "Flavor", 10),
                ],
                "___records___",
                "Runs",
                metric_agg="count",
            ),
        ]
        grid = [
            {"x": 0, "y": 0, "w": 48, "h": 3, "i": "p0"},
            {"x": 0, "y": 3, "w": 8, "h": 8, "i": "p1"},
            {"x": 8, "y": 3, "w": 8, "h": 8, "i": "p2"},
            {"x": 16, "y": 3, "w": 8, "h": 8, "i": "p3"},
            {"x": 24, "y": 3, "w": 8, "h": 8, "i": "p4"},
            {"x": 32, "y": 3, "w": 8, "h": 8, "i": "p21"},
            {"x": 40, "y": 3, "w": 8, "h": 8, "i": "p23"},
            {"x": 0, "y": 23, "w": 24, "h": 12, "i": "p5"},
            {"x": 24, "y": 23, "w": 24, "h": 12, "i": "p6"},
            {"x": 0, "y": 35, "w": 24, "h": 12, "i": "p7"},
            {"x": 24, "y": 35, "w": 24, "h": 12, "i": "p8"},
            {"x": 0, "y": 11, "w": 24, "h": 12, "i": "p9"},
            {"x": 24, "y": 11, "w": 12, "h": 12, "i": "p10"},
            {"x": 0, "y": 47, "w": 24, "h": 12, "i": "p11"},
            {"x": 24, "y": 47, "w": 24, "h": 12, "i": "p12"},
            {"x": 36, "y": 11, "w": 12, "h": 12, "i": "p13"},
            {"x": 0, "y": 59, "w": 48, "h": 12, "i": "p14"},
            {"x": 0, "y": 71, "w": 24, "h": 12, "i": "p15"},
            {"x": 24, "y": 71, "w": 24, "h": 12, "i": "p16"},
            {"x": 0, "y": 83, "w": 24, "h": 10, "i": "p17"},
            {"x": 24, "y": 83, "w": 8, "h": 10, "i": "p18"},
            {"x": 32, "y": 83, "w": 8, "h": 10, "i": "p19"},
            {"x": 40, "y": 83, "w": 8, "h": 10, "i": "p20"},
            {"x": 0, "y": 93, "w": 24, "h": 12, "i": "p22"},
            {"x": 24, "y": 93, "w": 24, "h": 12, "i": "p24"},
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
