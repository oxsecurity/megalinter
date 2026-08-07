#!/usr/bin/env python3
"""
Grafana dashboard builder: 4 dashboards querying the Prometheus metrics
(megalinter_run_*, megalinter_linter_run_*) and the Loki streams
(recordType run/linter/rule/file) sent by ApiProviderGrafana.
"""

from dashboard_builders.contract import (
    LOKI_BASE,
    PROM_LINTER_PREFIX,
    PROM_RUN_PREFIX,
)
from dashboard_builders.DashboardBuilder import DashboardBuilder

GRAFANA_TAG = "megalinter"
# Shared LogQL suffix: unwrap occurrences, dropping malformed lines
LOKI_UNWRAP = '| json | unwrap occurrences | __error__=""'

DESC_HEALTH_SCORE = (
    "Health score of the latest run in the selected time range, aggregated with min "
    "(worst case) across the selected branches/repositories. "
    "Rating scale: A >= 90, B >= 80, C >= 65, D >= 50, else E."
)
DESC_QUALITY_GATE = (
    "Worst-case (min) quality gate of the latest run of each selected series: "
    "FAIL as soon as one selected branch failed its latest run."
)
DESC_BLOCKING_ERRORS = (
    "Sum of the blocking errors reported by the latest run of each selected "
    "repository/branch in the time range."
)
DESC_RATING = (
    "Rating derived from the latest-run, worst-branch health score: "
    "A >= 90, B >= 80, C >= 65, D >= 50, else E."
)
DESC_GATE_PASS_RATE = (
    "Share of all MegaLinter runs over the selected period that passed the "
    "quality gate."
)


class DashboardBuilderGrafana(DashboardBuilder):
    provider = "grafana"

    def __init__(self):
        self.panel_id = 0

    def build(self) -> dict:
        self.panel_id = 0
        return {
            "grafana/megalinter-org-overview.json": self.to_json(
                self.org_overview_dashboard()
            ),
            "grafana/megalinter-repository.json": self.to_json(
                self.repository_dashboard()
            ),
            "grafana/megalinter-linter-detail.json": self.to_json(
                self.linter_detail_dashboard()
            ),
            "grafana/megalinter-rules-files.json": self.to_json(
                self.rules_files_dashboard()
            ),
            "grafana/megalinter-rating.json": self.to_json(self.rating_dashboard()),
        }

    def manifest_entries(self) -> list:
        return [
            {
                "provider": "grafana",
                "file": "grafana/megalinter-org-overview.json",
                "uid": "megalinter-org-overview",
            },
            {
                "provider": "grafana",
                "file": "grafana/megalinter-repository.json",
                "uid": "megalinter-repository",
            },
            {
                "provider": "grafana",
                "file": "grafana/megalinter-linter-detail.json",
                "uid": "megalinter-linter-detail",
            },
            {
                "provider": "grafana",
                "file": "grafana/megalinter-rules-files.json",
                "uid": "megalinter-rules-files",
            },
            {
                "provider": "grafana",
                "file": "grafana/megalinter-rating.json",
                "uid": "megalinter-rating",
            },
        ]

    #####################
    # Panel helpers
    #####################

    def next_id(self):
        self.panel_id += 1
        return self.panel_id

    def ds_prom(self):
        return {"type": "prometheus", "uid": "${DS_PROMETHEUS}"}

    def ds_loki(self):
        return {"type": "loki", "uid": "${DS_LOKI}"}

    def prom_target(self, expr, ref_id="A", instant=False, legend=None, table=False):
        target = {"datasource": self.ds_prom(), "expr": expr, "refId": ref_id}
        if instant:
            target["instant"] = True
            target["range"] = False
        if table:
            target["format"] = "table"
        if legend is not None:
            target["legendFormat"] = legend
        return target

    def loki_target(self, expr, ref_id="A", instant=False, legend=None):
        target = {"datasource": self.ds_loki(), "expr": expr, "refId": ref_id}
        if instant:
            target["queryType"] = "instant"
        if legend is not None:
            target["legendFormat"] = legend
        return target

    def thresholds(self, steps):
        return {"mode": "absolute", "steps": steps}

    def green_only(self):
        return self.thresholds([{"color": "green", "value": None}])

    def red_if_any(self):
        return self.thresholds(
            [{"color": "green", "value": None}, {"color": "red", "value": 1}]
        )

    def gate_mapping(self):
        return [
            {
                "type": "value",
                "options": {
                    "0": {"text": "FAIL", "color": "red", "index": 1},
                    "1": {"text": "PASS", "color": "green", "index": 0},
                },
            }
        ]

    # A-E rating derived from the health score
    def grade_mappings(self):
        return [
            {
                "type": "range",
                "options": {
                    "from": 90,
                    "to": 101,
                    "result": {"text": "A", "color": "green", "index": 0},
                },
            },
            {
                "type": "range",
                "options": {
                    "from": 80,
                    "to": 90,
                    "result": {"text": "B", "color": "light-green", "index": 1},
                },
            },
            {
                "type": "range",
                "options": {
                    "from": 65,
                    "to": 80,
                    "result": {"text": "C", "color": "yellow", "index": 2},
                },
            },
            {
                "type": "range",
                "options": {
                    "from": 50,
                    "to": 65,
                    "result": {"text": "D", "color": "orange", "index": 3},
                },
            },
            {
                "type": "range",
                "options": {
                    "from": 0,
                    "to": 50,
                    "result": {"text": "E", "color": "red", "index": 4},
                },
            },
        ]

    def series_color_override(self, series_name, color):
        return {
            "matcher": {"id": "byName", "options": series_name},
            "properties": [
                {"id": "color", "value": {"mode": "fixed", "fixedColor": color}}
            ],
        }

    def cell_color_override(self, column, thresholds_def, mappings=None):
        properties = [
            {"id": "thresholds", "value": thresholds_def},
            {"id": "custom.cellOptions", "value": {"type": "color-background"}},
        ]
        if mappings is not None:
            properties.append({"id": "mappings", "value": mappings})
        return {
            "matcher": {"id": "byName", "options": column},
            "properties": properties,
        }

    def health_thresholds(self):
        return self.thresholds(
            [
                {"color": "red", "value": None},
                {"color": "yellow", "value": 50},
                {"color": "green", "value": 80},
            ]
        )

    def text_panel(self, content, grid, title=""):
        return {
            "id": self.next_id(),
            "type": "text",
            "title": title,
            "gridPos": grid,
            "options": {"mode": "markdown", "content": content},
            "fieldConfig": {"defaults": {}, "overrides": []},
        }

    def rating_link(self, repo_ref=None):
        # ${branch:queryparam} propagates the branch selection (incl. multi-values)
        url = (
            "/d/megalinter-rating/megalinter-rating"
            "?${__url_time_range}&${branch:queryparam}"
        )
        title = "Why this rating?"
        if repo_ref is not None:
            url += f"&var-repo={repo_ref}"
        else:
            title = "Rating explanation (pick a repository)"
        return {"title": title, "url": url}

    def repository_link(self, repo_ref):
        return {
            "title": "Open repository dashboard",
            "url": (
                "/d/megalinter-repository/megalinter-repository"
                f"?var-repo={repo_ref}"
                "&${__url_time_range}&${branch:queryparam}"
            ),
        }

    def linter_link(self, linter_ref, repo_ref="$repo"):
        return {
            "title": "Open linter detail dashboard",
            "url": (
                "/d/megalinter-linter-detail/megalinter-linter-detail"
                f"?var-repo={repo_ref}&var-linter={linter_ref}"
                "&${__url_time_range}&${branch:queryparam}"
            ),
        }

    # Churn-proof "latest value": the inner instant aggregation collapses
    # branch/version/flavor label churn at each subquery step, then
    # last_over_time keeps only the most recent step, so stale series
    # (deleted branch, pre-upgrade version) never leak their final value
    def latest_agg(self, inner_agg, metric, sel, by=None):
        by_clause = f" by ({by})" if by else ""
        return (
            f"last_over_time(({inner_agg}{by_clause} ({metric}{{{sel}}}))[$__range:])"
        )

    def stat_panel(
        self,
        title,
        expr,
        grid,
        unit=None,
        mappings=None,
        thresholds_def=None,
        links=None,
        color_mode="value",
        description=None,
    ):
        defaults = {
            "thresholds": thresholds_def or self.green_only(),
            "mappings": mappings or [],
        }
        if unit is not None:
            defaults["unit"] = unit
        if links is not None:
            defaults["links"] = links
        panel = {
            "id": self.next_id(),
            "type": "stat",
            "title": title,
            "datasource": self.ds_prom(),
            "gridPos": grid,
            "fieldConfig": {"defaults": defaults, "overrides": []},
            "options": {
                "reduceOptions": {
                    "calcs": ["lastNotNull"],
                    "fields": "",
                    "values": False,
                },
                "colorMode": color_mode,
                "graphMode": "none",
                "orientation": "auto",
                "textMode": "auto",
            },
            "targets": [self.prom_target(expr, instant=True)],
        }
        if description is not None:
            panel["description"] = description
        return panel

    def timeseries_panel(
        self,
        title,
        targets,
        grid,
        unit=None,
        stacking=False,
        links=None,
        overrides=None,
        thresholds_def=None,
        threshold_zones=False,
        min_val=None,
        max_val=None,
        legend_placement="right",
    ):
        defaults = {
            "custom": {
                "drawStyle": "line",
                "lineWidth": 2,
                "fillOpacity": 12,
                # Sparse point-in-time CI data: never bridge gaps between runs
                "spanNulls": False,
                "showPoints": "auto",
                "pointSize": 5,
            },
            "thresholds": self.green_only(),
            "mappings": [],
        }
        if stacking:
            defaults["custom"]["stacking"] = {"mode": "normal", "group": "A"}
            defaults["custom"]["fillOpacity"] = 35
        if unit is not None:
            defaults["unit"] = unit
        if links is not None:
            defaults["links"] = links
        if thresholds_def is not None:
            defaults["thresholds"] = thresholds_def
        if threshold_zones:
            defaults["custom"]["thresholdsStyle"] = {"mode": "area"}
        if min_val is not None:
            defaults["min"] = min_val
        if max_val is not None:
            defaults["max"] = max_val
        return {
            "id": self.next_id(),
            "type": "timeseries",
            "title": title,
            "datasource": targets[0]["datasource"],
            "gridPos": grid,
            "fieldConfig": {"defaults": defaults, "overrides": overrides or []},
            "options": {
                "legend": {
                    "displayMode": "table",
                    "placement": legend_placement,
                    "calcs": ["lastNotNull", "max"],
                },
                "tooltip": {"mode": "multi", "sort": "desc"},
            },
            "targets": targets,
        }

    def bargauge_panel(
        self, title, expr, grid, datasource=None, thresholds_def=None, links=None
    ):
        datasource = datasource or self.ds_prom()
        defaults = {
            "thresholds": thresholds_def or self.red_if_any(),
            "mappings": [],
            "color": {"mode": "continuous-GrYlRd"},
        }
        if links is not None:
            defaults["links"] = links
        return {
            "id": self.next_id(),
            "type": "bargauge",
            "title": title,
            "datasource": datasource,
            "gridPos": grid,
            "fieldConfig": {
                "defaults": defaults,
                "overrides": [],
            },
            "options": {
                "displayMode": "gradient",
                "orientation": "horizontal",
                "reduceOptions": {
                    "calcs": ["lastNotNull"],
                    "fields": "",
                    "values": False,
                },
                "showUnfilled": True,
            },
            "targets": [
                (
                    self.prom_target(expr, instant=True)
                    if datasource["type"] == "prometheus"
                    else self.loki_target(expr, instant=True)
                )
            ],
        }

    def table_panel(
        self,
        title,
        targets,
        grid,
        transformations=None,
        overrides=None,
        links=None,
        sort_column=None,
        sort_desc=True,
    ):
        defaults = {"thresholds": self.green_only(), "mappings": []}
        if links is not None:
            defaults["links"] = links
        return {
            "id": self.next_id(),
            "type": "table",
            "title": title,
            "datasource": targets[0]["datasource"],
            "gridPos": grid,
            "fieldConfig": {
                "defaults": defaults,
                "overrides": overrides or [],
            },
            "options": {
                "showHeader": True,
                "sortBy": (
                    [{"displayName": sort_column, "desc": sort_desc}]
                    if sort_column is not None
                    else []
                ),
            },
            "targets": targets,
            "transformations": transformations or [],
        }

    def state_timeline_panel(self, title, expr, grid, legend=None):
        return {
            "id": self.next_id(),
            "type": "state-timeline",
            "title": title,
            "datasource": self.ds_prom(),
            "gridPos": grid,
            "fieldConfig": {
                "defaults": {
                    "custom": {"lineWidth": 0, "fillOpacity": 70, "spanNulls": True},
                    "thresholds": self.thresholds(
                        [
                            {"color": "red", "value": None},
                            {"color": "green", "value": 1},
                        ]
                    ),
                    "mappings": self.gate_mapping(),
                    "color": {"mode": "thresholds"},
                    "max": 1,
                    "min": 0,
                },
                "overrides": [],
            },
            "options": {
                "showValue": "auto",
                "rowHeight": 0.85,
                "mergeValues": True,
                "legend": {"displayMode": "hidden"},
                "tooltip": {"mode": "single"},
            },
            "targets": [self.prom_target(expr, legend=legend)],
        }

    def logs_panel(self, title, expr, grid):
        return {
            "id": self.next_id(),
            "type": "logs",
            "title": title,
            "datasource": self.ds_loki(),
            "gridPos": grid,
            "options": {
                "showTime": True,
                "wrapLogMessage": True,
                "enableLogDetails": True,
                "sortOrder": "Descending",
                "dedupStrategy": "none",
                "prettifyLogMessage": True,
            },
            "targets": [self.loki_target(expr)],
        }

    # Auto-selected and hidden (sfdx-hardis v2 style); the regex keeps
    # Grafana Cloud internal datasources from being picked automatically
    DS_EXCLUDE_REGEX = "/^(?!.*(alert-state-history|usage-insights|ml-metrics)).*/"

    def datasource_variables(self, include_loki=True):
        variables = [
            {
                "name": "DS_PROMETHEUS",
                "label": "Metrics datasource",
                "type": "datasource",
                "query": "prometheus",
                "current": {},
                "hide": 2,
                "refresh": 1,
                "regex": self.DS_EXCLUDE_REGEX,
            }
        ]
        if include_loki:
            variables.append(
                {
                    "name": "DS_LOKI",
                    "label": "Logs datasource",
                    "type": "datasource",
                    "query": "loki",
                    "current": {},
                    "hide": 2,
                    "refresh": 1,
                    "regex": self.DS_EXCLUDE_REGEX,
                }
            )
        return variables

    # Marks each CI run on the (sparse) timeseries panels
    def loki_runs_annotation(self, extra_sel=""):
        return {
            "name": "MegaLinter runs",
            "datasource": self.ds_loki(),
            "enable": True,
            "hide": False,
            "iconColor": "blue",
            "expr": f'{{{LOKI_BASE},recordType="run"{extra_sel}}}',
        }

    def query_variable(self, name, label, query, multi=True, include_all=True):
        return {
            "name": name,
            "label": label,
            "type": "query",
            "datasource": self.ds_prom(),
            "query": {"query": query, "refId": name},
            "refresh": 2,
            "sort": 1,
            "multi": multi,
            "includeAll": include_all,
            "current": {},
            "options": [],
        }

    def dashboard_shell(
        self, title, uid, variables, panels, description, annotations=None
    ):
        return {
            "annotations": {"list": annotations or []},
            "description": description,
            "editable": True,
            "fiscalYearStartMonth": 0,
            "graphTooltip": 1,
            "id": None,
            "links": [
                # Single dropdown button listing every MegaLinter dashboard
                # (by tag), keeping the selected time range and variables
                {
                    "title": "MegaLinter dashboards",
                    "type": "dashboards",
                    "tags": [GRAFANA_TAG],
                    "asDropdown": True,
                    "keepTime": True,
                    "includeVars": True,
                    "icon": "dashboard",
                    "targetBlank": False,
                },
                {
                    "title": "Documentation",
                    "url": "https://megalinter.io/latest/observability/grafana/",
                    "type": "link",
                    "icon": "doc",
                    "targetBlank": True,
                },
            ],
            "panels": panels,
            "refresh": "5m",
            "schemaVersion": 41,
            "tags": [GRAFANA_TAG],
            "templating": {"list": variables},
            "time": {"from": "now-30d", "to": "now"},
            "timepicker": {},
            "timezone": "browser",
            "title": title,
            "uid": uid,
            "version": 1,
            "weekStart": "",
        }

    def join_by_field_transformations(self, field, renames, mode="outer"):
        return [
            {"id": "joinByField", "options": {"byField": field, "mode": mode}},
            # Joining several instant table frames leaves "Time", "Time 2", ...
            # columns behind: drop them all before renaming
            {
                "id": "filterFieldsByName",
                "options": {"exclude": {"pattern": "^Time.*$"}},
            },
            {
                "id": "organize",
                "options": {
                    "excludeByName": {"Time": True},
                    "renameByName": renames,
                },
            },
        ]

    #####################
    # Dashboards
    #####################

    def org_overview_dashboard(self):
        sel = 'orgIdentifier=~"$org",gitBranchName=~"$branch"'
        run_range = "[$__range]"
        panels = [
            self.stat_panel(
                "Repositories monitored",
                f"count(count by (gitRepoName) (last_over_time({PROM_RUN_PREFIX}lintersCount{{{sel}}}{run_range})))",
                {"h": 5, "w": 4, "x": 0, "y": 0},
            ),
            self.stat_panel(
                "Runs (selected period)",
                f"sum(count_over_time({PROM_RUN_PREFIX}qualityGate{{{sel}}}{run_range}))",
                {"h": 5, "w": 4, "x": 4, "y": 0},
                thresholds_def=self.thresholds([{"color": "blue", "value": None}]),
            ),
            self.stat_panel(
                "Quality gate pass rate",
                f"100 * sum(sum_over_time({PROM_RUN_PREFIX}qualityGate{{{sel}}}{run_range})) / "
                f"sum(count_over_time({PROM_RUN_PREFIX}qualityGate{{{sel}}}{run_range}))",
                {"h": 5, "w": 4, "x": 8, "y": 0},
                unit="percent",
                thresholds_def=self.thresholds(
                    [
                        {"color": "red", "value": None},
                        {"color": "yellow", "value": 50},
                        {"color": "green", "value": 90},
                    ]
                ),
                color_mode="background",
                description=DESC_GATE_PASS_RATE,
            ),
            self.stat_panel(
                "Blocking errors (latest runs)",
                f"sum({self.latest_agg('sum', f'{PROM_RUN_PREFIX}blockingErrors', sel, 'gitIdentifier')})",
                {"h": 5, "w": 4, "x": 12, "y": 0},
                thresholds_def=self.red_if_any(),
                color_mode="background",
                description=DESC_BLOCKING_ERRORS,
            ),
            self.stat_panel(
                "Non-blocking errors (latest runs)",
                f"sum({self.latest_agg('sum', f'{PROM_RUN_PREFIX}nonBlockingErrors', sel, 'gitIdentifier')})",
                {"h": 5, "w": 4, "x": 16, "y": 0},
                thresholds_def=self.thresholds(
                    [{"color": "green", "value": None}, {"color": "yellow", "value": 1}]
                ),
            ),
            self.stat_panel(
                "Errors auto-fixed (latest runs)",
                f"sum({self.latest_agg('sum', f'{PROM_RUN_PREFIX}totalErrorsFixed', sel, 'gitIdentifier')})",
                {"h": 5, "w": 4, "x": 20, "y": 0},
                thresholds_def=self.thresholds([{"color": "blue", "value": None}]),
            ),
            self.table_panel(
                "Repositories (latest run) - click a value to open the repository dashboard",
                [
                    self.prom_target(
                        self.latest_agg(
                            "min", f"{PROM_RUN_PREFIX}qualityGate", sel, "gitRepoName"
                        ),
                        "A",
                        instant=True,
                        table=True,
                    ),
                    self.prom_target(
                        self.latest_agg(
                            "min", f"{PROM_RUN_PREFIX}healthScore", sel, "gitRepoName"
                        ),
                        "B",
                        instant=True,
                        table=True,
                    ),
                    self.prom_target(
                        self.latest_agg(
                            "sum",
                            f"{PROM_RUN_PREFIX}blockingErrors",
                            sel,
                            "gitRepoName",
                        ),
                        "C",
                        instant=True,
                        table=True,
                    ),
                    self.prom_target(
                        self.latest_agg(
                            "sum",
                            f"{PROM_RUN_PREFIX}nonBlockingErrors",
                            sel,
                            "gitRepoName",
                        ),
                        "D",
                        instant=True,
                        table=True,
                    ),
                    self.prom_target(
                        self.latest_agg(
                            "sum", f"{PROM_RUN_PREFIX}lintersError", sel, "gitRepoName"
                        ),
                        "E",
                        instant=True,
                        table=True,
                    ),
                    self.prom_target(
                        self.latest_agg(
                            "max", f"{PROM_RUN_PREFIX}runDurationS", sel, "gitRepoName"
                        ),
                        "F",
                        instant=True,
                        table=True,
                    ),
                ],
                {"h": 10, "w": 12, "x": 0, "y": 5},
                transformations=self.join_by_field_transformations(
                    "gitRepoName",
                    {
                        "Value #A": "Quality gate",
                        "Value #B": "Health score",
                        "Value #C": "Blocking errors",
                        "Value #D": "Non-blocking errors",
                        "Value #E": "Linters in error",
                        "Value #F": "Duration (s)",
                        "gitRepoName": "Repository",
                    },
                ),
                overrides=[
                    self.cell_color_override(
                        "Quality gate",
                        self.thresholds(
                            [
                                {"color": "red", "value": None},
                                {"color": "green", "value": 1},
                            ]
                        ),
                        mappings=self.gate_mapping(),
                    ),
                    self.cell_color_override("Health score", self.health_thresholds()),
                    self.cell_color_override("Blocking errors", self.red_if_any()),
                    self.cell_color_override("Linters in error", self.red_if_any()),
                ],
                links=[
                    self.repository_link("${__data.fields.Repository:percentencode}"),
                ],
                sort_column="Blocking errors",
            ),
            self.bargauge_panel(
                "Top repositories by blocking errors",
                f"topk(10, {self.latest_agg('sum', f'{PROM_RUN_PREFIX}blockingErrors', sel, 'gitRepoName')})",
                {"h": 10, "w": 12, "x": 12, "y": 5},
                links=[
                    self.repository_link("${__field.labels.gitRepoName:percentencode}")
                ],
            ),
            self.timeseries_panel(
                "Repository health score evolution",
                [
                    self.prom_target(
                        f"bottomk(15, min by (gitRepoName) ({PROM_RUN_PREFIX}healthScore{{{sel}}}))",
                        legend="{{gitRepoName}}",
                    )
                ],
                {"h": 9, "w": 12, "x": 0, "y": 15},
                unit="percent",
                links=[
                    self.repository_link("${__field.labels.gitRepoName:percentencode}")
                ],
                thresholds_def=self.health_thresholds(),
                threshold_zones=True,
                min_val=0,
                max_val=100,
            ),
            self.timeseries_panel(
                "Total errors trend by repository",
                [
                    self.prom_target(
                        f"topk(15, sum by (gitRepoName) ({PROM_RUN_PREFIX}totalErrors{{{sel}}}))",
                        legend="{{gitRepoName}}",
                    )
                ],
                {"h": 9, "w": 12, "x": 12, "y": 15},
                links=[
                    self.repository_link("${__field.labels.gitRepoName:percentencode}")
                ],
            ),
            self.timeseries_panel(
                "Run duration by repository",
                [
                    self.prom_target(
                        f"topk(15, max by (gitRepoName) ({PROM_RUN_PREFIX}runDurationS{{{sel}}}))",
                        legend="{{gitRepoName}}",
                    )
                ],
                {"h": 9, "w": 12, "x": 0, "y": 32},
                unit="s",
                links=[
                    self.repository_link("${__field.labels.gitRepoName:percentencode}")
                ],
            ),
            self.stat_panel(
                "Average health score",
                f"avg({self.latest_agg('min', f'{PROM_RUN_PREFIX}healthScore', sel, 'gitRepoName')})",
                {"h": 9, "w": 4, "x": 12, "y": 32},
                unit="percent",
                thresholds_def=self.health_thresholds(),
                description=DESC_HEALTH_SCORE,
            ),
            self.stat_panel(
                "Org rating",
                f"avg({self.latest_agg('min', f'{PROM_RUN_PREFIX}healthScore', sel, 'gitRepoName')})",
                {"h": 9, "w": 4, "x": 16, "y": 32},
                mappings=self.grade_mappings(),
                thresholds_def=self.health_thresholds(),
                color_mode="background",
                links=[self.rating_link()],
                description=DESC_RATING,
            ),
            self.stat_panel(
                "Estimated time saved by auto-fixes (5 min/fix)",
                f"sum(sum_over_time({PROM_RUN_PREFIX}totalErrorsFixed{{{sel}}}{run_range})) * 5",
                {"h": 9, "w": 4, "x": 20, "y": 32},
                unit="m",
                thresholds_def=self.thresholds([{"color": "blue", "value": None}]),
            ),
            self.state_timeline_panel(
                "Quality gate history by repository",
                f"min by (gitIdentifier) ({PROM_RUN_PREFIX}qualityGate{{{sel}}})",
                {"h": 8, "w": 12, "x": 0, "y": 24},
                legend="{{gitIdentifier}}",
            ),
            self.timeseries_panel(
                "Errors auto-fixed by repository",
                [
                    self.prom_target(
                        f"topk(15, sum by (gitRepoName) ({PROM_RUN_PREFIX}totalErrorsFixed{{{sel}}}))",
                        legend="{{gitRepoName}}",
                    )
                ],
                {"h": 8, "w": 6, "x": 12, "y": 24},
                legend_placement="bottom",
            ),
            self.table_panel(
                "MegaLinter versions",
                [
                    self.prom_target(
                        f"max by (gitRepoName, megalinterVersion, megalinterFlavor) "
                        f"(last_over_time({PROM_RUN_PREFIX}qualityGate{{{sel}}}{run_range}))",
                        "A",
                        instant=True,
                        table=True,
                    )
                ],
                {"h": 8, "w": 6, "x": 18, "y": 24},
                transformations=[
                    {
                        "id": "organize",
                        "options": {
                            "excludeByName": {"Time": True, "Value #A": True},
                            "renameByName": {
                                "gitRepoName": "Repository",
                                "megalinterVersion": "Version",
                                "megalinterFlavor": "Flavor",
                            },
                        },
                    }
                ],
                sort_column="Repository",
                sort_desc=False,
            ),
        ]
        variables = self.datasource_variables(include_loki=False) + [
            self.query_variable(
                "org",
                "Organization",
                f"label_values({PROM_RUN_PREFIX}lintersCount, orgIdentifier)",
                multi=True,
            ),
            self.query_variable(
                "branch",
                "Branch",
                f'label_values({PROM_RUN_PREFIX}lintersCount{{orgIdentifier=~"$org"}}, gitBranchName)',
                multi=True,
            ),
        ]
        return self.dashboard_shell(
            "MegaLinter - 1. Org Overview",
            "megalinter-org-overview",
            variables,
            panels,
            "Portfolio view of MegaLinter results across all monitored repositories",
        )

    def repository_dashboard(self):
        sel = 'gitRepoName=~"$repo",gitBranchName=~"$branch"'
        run_range = "[$__range]"
        variables = self.datasource_variables() + [
            self.query_variable(
                "repo",
                "Repository",
                f"label_values({PROM_RUN_PREFIX}lintersCount, gitRepoName)",
                multi=False,
                include_all=False,
            ),
            self.query_variable(
                "branch",
                "Branch",
                f'label_values({PROM_RUN_PREFIX}lintersCount{{gitRepoName=~"$repo"}}, gitBranchName)',
                multi=True,
            ),
        ]
        fixed_latest = self.latest_agg("sum", f"{PROM_RUN_PREFIX}totalErrorsFixed", sel)
        errors_latest = self.latest_agg("sum", f"{PROM_RUN_PREFIX}totalErrors", sel)
        panels = [
            self.stat_panel(
                "Quality gate",
                self.latest_agg("min", f"{PROM_RUN_PREFIX}qualityGate", sel),
                {"h": 5, "w": 4, "x": 0, "y": 0},
                mappings=self.gate_mapping(),
                thresholds_def=self.thresholds(
                    [{"color": "red", "value": None}, {"color": "green", "value": 1}]
                ),
                color_mode="background",
                description=DESC_QUALITY_GATE,
            ),
            self.stat_panel(
                "Blocking errors",
                self.latest_agg("sum", f"{PROM_RUN_PREFIX}blockingErrors", sel),
                {"h": 5, "w": 4, "x": 4, "y": 0},
                thresholds_def=self.red_if_any(),
                color_mode="background",
                description=DESC_BLOCKING_ERRORS,
            ),
            self.stat_panel(
                "Non-blocking errors",
                self.latest_agg("sum", f"{PROM_RUN_PREFIX}nonBlockingErrors", sel),
                {"h": 5, "w": 4, "x": 8, "y": 0},
                thresholds_def=self.thresholds(
                    [{"color": "green", "value": None}, {"color": "yellow", "value": 1}]
                ),
            ),
            self.stat_panel(
                "Errors auto-fixed",
                fixed_latest,
                {"h": 5, "w": 4, "x": 12, "y": 0},
                thresholds_def=self.thresholds([{"color": "blue", "value": None}]),
            ),
            self.stat_panel(
                "Linters in error",
                self.latest_agg("sum", f"{PROM_RUN_PREFIX}lintersError", sel),
                {"h": 5, "w": 4, "x": 16, "y": 0},
                thresholds_def=self.red_if_any(),
            ),
            self.stat_panel(
                "Run duration",
                self.latest_agg("max", f"{PROM_RUN_PREFIX}runDurationS", sel),
                {"h": 5, "w": 4, "x": 20, "y": 0},
                unit="s",
            ),
            self.stat_panel(
                "Runs (selected period)",
                f"sum(count_over_time({PROM_RUN_PREFIX}qualityGate{{{sel}}}{run_range}))",
                {"h": 5, "w": 4, "x": 0, "y": 5},
                thresholds_def=self.thresholds([{"color": "blue", "value": None}]),
            ),
            self.stat_panel(
                "Fix rate",
                f"100 * {fixed_latest} / "
                f"clamp_min({fixed_latest} + {errors_latest}, 1)",
                {"h": 5, "w": 4, "x": 4, "y": 5},
                unit="percent",
                thresholds_def=self.thresholds([{"color": "blue", "value": None}]),
            ),
            self.stat_panel(
                "Health score",
                self.latest_agg("min", f"{PROM_RUN_PREFIX}healthScore", sel),
                {"h": 5, "w": 4, "x": 8, "y": 5},
                unit="percent",
                thresholds_def=self.health_thresholds(),
                color_mode="background",
                description=DESC_HEALTH_SCORE,
            ),
            self.stat_panel(
                "Rating",
                self.latest_agg("min", f"{PROM_RUN_PREFIX}healthScore", sel),
                {"h": 5, "w": 3, "x": 12, "y": 5},
                mappings=self.grade_mappings(),
                thresholds_def=self.health_thresholds(),
                color_mode="background",
                links=[self.rating_link("$repo")],
                description=DESC_RATING,
            ),
            self.state_timeline_panel(
                "Quality gate history",
                f"min by (gitBranchName) ({PROM_RUN_PREFIX}qualityGate{{{sel}}})",
                {"h": 5, "w": 9, "x": 15, "y": 5},
                legend="{{gitBranchName}}",
            ),
            self.timeseries_panel(
                "Errors trend",
                [
                    self.prom_target(
                        f"max({PROM_RUN_PREFIX}blockingErrors{{{sel}}})",
                        "A",
                        legend="Blocking",
                    ),
                    self.prom_target(
                        f"max({PROM_RUN_PREFIX}nonBlockingErrors{{{sel}}})",
                        "B",
                        legend="Non-blocking",
                    ),
                ],
                {"h": 9, "w": 12, "x": 0, "y": 10},
                overrides=[
                    self.series_color_override("Blocking", "red"),
                    self.series_color_override("Non-blocking", "yellow"),
                ],
            ),
            self.timeseries_panel(
                "Errors by linter - click a linter to open its dashboard",
                [
                    self.prom_target(
                        f"max by (linterKey) ({PROM_LINTER_PREFIX}numberErrorsFound{{{sel}}})",
                        legend="{{linterKey}}",
                    )
                ],
                {"h": 9, "w": 12, "x": 12, "y": 10},
                stacking=True,
                links=[self.linter_link("${__field.labels.linterKey:percentencode}")],
            ),
            self.table_panel(
                "Linters (latest run)",
                [
                    self.prom_target(
                        self.latest_agg(
                            "sum",
                            f"{PROM_LINTER_PREFIX}numberErrorsFound",
                            sel,
                            "linterKey",
                        ),
                        "A",
                        instant=True,
                        table=True,
                    ),
                    self.prom_target(
                        self.latest_agg(
                            "max", f"{PROM_LINTER_PREFIX}blocking", sel, "linterKey"
                        ),
                        "B",
                        instant=True,
                        table=True,
                    ),
                    self.prom_target(
                        self.latest_agg(
                            "max", f"{PROM_LINTER_PREFIX}elapsedTime", sel, "linterKey"
                        ),
                        "C",
                        instant=True,
                        table=True,
                    ),
                ],
                {"h": 10, "w": 12, "x": 0, "y": 19},
                transformations=self.join_by_field_transformations(
                    "linterKey",
                    {
                        "Value #A": "Errors",
                        "Value #B": "Blocking",
                        "Value #C": "Elapsed (s)",
                        "linterKey": "Linter",
                    },
                ),
                overrides=[
                    self.cell_color_override("Errors", self.red_if_any()),
                    self.cell_color_override(
                        "Blocking",
                        self.red_if_any(),
                        mappings=[
                            {
                                "type": "value",
                                "options": {
                                    "0": {"text": "NO", "color": "green", "index": 0},
                                    "1": {"text": "YES", "color": "red", "index": 1},
                                },
                            }
                        ],
                    ),
                ],
                links=[self.linter_link("${__data.fields.Linter:percentencode}")],
                sort_column="Errors",
            ),
            self.timeseries_panel(
                "Linters duration",
                [
                    self.prom_target(
                        f"max by (linterKey) ({PROM_LINTER_PREFIX}elapsedTime{{{sel}}})",
                        legend="{{linterKey}}",
                    )
                ],
                {"h": 10, "w": 12, "x": 12, "y": 19},
                unit="s",
            ),
            self.timeseries_panel(
                "Repository health score evolution",
                [
                    self.prom_target(
                        f"min({PROM_RUN_PREFIX}healthScore{{{sel}}})",
                        legend="Health score",
                    )
                ],
                {"h": 8, "w": 12, "x": 0, "y": 29},
                unit="percent",
                thresholds_def=self.health_thresholds(),
                threshold_zones=True,
                min_val=0,
                max_val=100,
            ),
            self.timeseries_panel(
                "Errors by language (descriptor)",
                [
                    self.prom_target(
                        f"sum by (descriptor) ({PROM_LINTER_PREFIX}numberErrorsFound{{{sel}}})",
                        legend="{{descriptor}}",
                    )
                ],
                {"h": 8, "w": 12, "x": 12, "y": 29},
                stacking=True,
            ),
            self.timeseries_panel(
                "Files analyzed",
                [
                    self.prom_target(
                        f"max({PROM_RUN_PREFIX}filesAnalyzed{{{sel}}})",
                        legend="Files analyzed",
                    )
                ],
                {"h": 8, "w": 12, "x": 0, "y": 37},
            ),
            self.timeseries_panel(
                "Errors auto-fixed",
                [
                    self.prom_target(
                        f"max({PROM_RUN_PREFIX}totalErrorsFixed{{{sel}}})",
                        legend="Errors auto-fixed",
                    )
                ],
                {"h": 8, "w": 12, "x": 12, "y": 37},
            ),
            self.logs_panel(
                "Latest linter outputs",
                f'{{{LOKI_BASE},recordType="linter",{sel}}}',
                {"h": 10, "w": 24, "x": 0, "y": 45},
            ),
        ]
        return self.dashboard_shell(
            "MegaLinter - 2. Repository",
            "megalinter-repository",
            variables,
            panels,
            "Quality gate, KPIs and trends for a single repository monitored by MegaLinter",
            annotations=[
                self.loki_runs_annotation(
                    ',gitRepoName=~"$repo",gitBranchName=~"$branch"'
                )
            ],
        )

    def linter_detail_dashboard(self):
        sel = 'gitRepoName=~"$repo",gitBranchName=~"$branch",linterKey=~"$linter"'
        variables = self.datasource_variables() + [
            self.query_variable(
                "repo",
                "Repository",
                f"label_values({PROM_RUN_PREFIX}lintersCount, gitRepoName)",
                multi=False,
                include_all=False,
            ),
            self.query_variable(
                "branch",
                "Branch",
                f'label_values({PROM_RUN_PREFIX}lintersCount{{gitRepoName=~"$repo"}}, gitBranchName)',
                multi=True,
            ),
            self.query_variable(
                "linter",
                "Linter",
                f'label_values({PROM_LINTER_PREFIX}numberErrorsFound{{gitRepoName=~"$repo"}}, linterKey)',
                multi=False,
                include_all=False,
            ),
        ]
        loki_rule_sel = f'{{{LOKI_BASE},recordType="rule",{sel}}}'
        loki_file_sel = f'{{{LOKI_BASE},recordType="file",{sel}}}'
        panels = [
            self.stat_panel(
                "Errors (latest run)",
                self.latest_agg("sum", f"{PROM_LINTER_PREFIX}numberErrorsFound", sel),
                {"h": 5, "w": 6, "x": 0, "y": 0},
                thresholds_def=self.red_if_any(),
            ),
            self.stat_panel(
                "Blocking",
                self.latest_agg("max", f"{PROM_LINTER_PREFIX}blocking", sel),
                {"h": 5, "w": 6, "x": 6, "y": 0},
                mappings=[
                    {
                        "type": "value",
                        "options": {
                            "0": {"text": "NO", "color": "green", "index": 0},
                            "1": {"text": "YES", "color": "red", "index": 1},
                        },
                    }
                ],
            ),
            self.stat_panel(
                "Files analyzed (latest run)",
                self.latest_agg("sum", f"{PROM_LINTER_PREFIX}numberFilesFound", sel),
                {"h": 5, "w": 6, "x": 12, "y": 0},
            ),
            self.stat_panel(
                "Elapsed time (latest run)",
                self.latest_agg("max", f"{PROM_LINTER_PREFIX}elapsedTime", sel),
                {"h": 5, "w": 6, "x": 18, "y": 0},
                unit="s",
            ),
            self.timeseries_panel(
                "Errors trend",
                [
                    self.prom_target(
                        f"max({PROM_LINTER_PREFIX}numberErrorsFound{{{sel}}})",
                        legend="Errors",
                    )
                ],
                {"h": 9, "w": 12, "x": 0, "y": 5},
            ),
            self.timeseries_panel(
                "Elapsed time trend",
                [
                    self.prom_target(
                        f"max({PROM_LINTER_PREFIX}elapsedTime{{{sel}}})",
                        legend="Elapsed (s)",
                    )
                ],
                {"h": 9, "w": 12, "x": 12, "y": 5},
                unit="s",
            ),
            self.bargauge_panel(
                "Top rules (selected period)",
                f"topk(20, sum by (ruleId) (sum_over_time({loki_rule_sel} {LOKI_UNWRAP} [$__range])))",
                {"h": 10, "w": 12, "x": 0, "y": 14},
                datasource=self.ds_loki(),
            ),
            self.bargauge_panel(
                "Top files (selected period)",
                f"topk(20, sum by (file) (sum_over_time({loki_file_sel} {LOKI_UNWRAP} [$__range])))",
                {"h": 10, "w": 12, "x": 12, "y": 14},
                datasource=self.ds_loki(),
            ),
            self.timeseries_panel(
                "Files analyzed trend",
                [
                    self.prom_target(
                        f"max({PROM_LINTER_PREFIX}numberFilesFound{{{sel}}})",
                        legend="Files analyzed",
                    )
                ],
                {"h": 8, "w": 12, "x": 0, "y": 24},
            ),
            self.timeseries_panel(
                "Errors auto-fixed trend",
                [
                    self.prom_target(
                        f"max({PROM_LINTER_PREFIX}numberErrorsFixed{{{sel}}})",
                        legend="Errors auto-fixed",
                    )
                ],
                {"h": 8, "w": 12, "x": 12, "y": 24},
            ),
            self.logs_panel(
                "Linter output",
                f'{{{LOKI_BASE},recordType="linter",{sel}}}',
                {"h": 10, "w": 24, "x": 0, "y": 32},
            ),
        ]
        return self.dashboard_shell(
            "MegaLinter - 3. Linter Detail",
            "megalinter-linter-detail",
            variables,
            panels,
            "Drill-down on a single linter: errors, duration, top rules and files",
            annotations=[
                self.loki_runs_annotation(
                    ',gitRepoName=~"$repo",gitBranchName=~"$branch"'
                )
            ],
        )

    def rating_dashboard(self):
        sel = 'gitRepoName=~"$repo",gitBranchName=~"$branch"'
        variables = self.datasource_variables(include_loki=False) + [
            self.query_variable(
                "repo",
                "Repository",
                f"label_values({PROM_RUN_PREFIX}lintersCount, gitRepoName)",
                multi=False,
                include_all=False,
            ),
            self.query_variable(
                "branch",
                "Branch",
                f'label_values({PROM_RUN_PREFIX}lintersCount{{gitRepoName=~"$repo"}}, gitBranchName)',
                multi=True,
            ),
        ]
        panels = [
            self.stat_panel(
                "Rating",
                self.latest_agg("min", f"{PROM_RUN_PREFIX}healthScore", sel),
                {"h": 6, "w": 4, "x": 0, "y": 0},
                mappings=self.grade_mappings(),
                thresholds_def=self.health_thresholds(),
                color_mode="background",
                description=DESC_RATING,
            ),
            self.stat_panel(
                "Health score",
                self.latest_agg("min", f"{PROM_RUN_PREFIX}healthScore", sel),
                {"h": 6, "w": 4, "x": 4, "y": 0},
                unit="percent",
                thresholds_def=self.health_thresholds(),
                color_mode="background",
                description=DESC_HEALTH_SCORE,
            ),
            self.text_panel(
                "## How the rating is computed\n\nThe **health score** (0-100) of a run is:\n\n`100 x "
                "(linters in success + 0.5 x linters with non-blocking errors) / total linters`\n\n| Rating | "
                "Health score |\n|--------|--------------|\n| A | >= 90 |\n| B | >= 80 |\n| C | >= 65 |\n| D "
                "| >= 50 |\n| E | < 50 |\n\n**To improve the rating**: fix the linters in error first (each "
                "one brings back a full share of the score), then reduce non-blocking warnings (each one "
                "brings back half a share). The table below lists the linters currently dragging the score "
                "down - click one to open its detail dashboard.",
                {"h": 18, "w": 16, "x": 8, "y": 0},
            ),
            self.stat_panel(
                "Linters in success",
                self.latest_agg("sum", f"{PROM_RUN_PREFIX}lintersSuccess", sel),
                {"h": 6, "w": 4, "x": 0, "y": 6},
                thresholds_def=self.thresholds([{"color": "green", "value": None}]),
                color_mode="background",
            ),
            self.stat_panel(
                "Linters with warnings (0.5 share each)",
                self.latest_agg("sum", f"{PROM_RUN_PREFIX}lintersWarning", sel),
                {"h": 6, "w": 4, "x": 4, "y": 6},
                thresholds_def=self.thresholds(
                    [
                        {"color": "green", "value": None},
                        {"color": "yellow", "value": 1},
                    ]
                ),
                color_mode="background",
            ),
            self.stat_panel(
                "Linters in error (0 share)",
                self.latest_agg("sum", f"{PROM_RUN_PREFIX}lintersError", sel),
                {"h": 6, "w": 4, "x": 0, "y": 12},
                thresholds_def=self.red_if_any(),
                color_mode="background",
            ),
            self.stat_panel(
                "Total linters",
                self.latest_agg("sum", f"{PROM_RUN_PREFIX}lintersCount", sel),
                {"h": 6, "w": 4, "x": 4, "y": 12},
            ),
            self.table_panel(
                "Linters dragging the score down - click one to open its dashboard",
                [
                    self.prom_target(
                        # > 0 keeps only failing linters in this frame; the inner
                        # join below then drops clean linters from the table
                        f"{self.latest_agg('sum', f'{PROM_LINTER_PREFIX}numberErrorsFound', sel, 'linterKey')} > 0",
                        "A",
                        instant=True,
                        table=True,
                    ),
                    self.prom_target(
                        self.latest_agg(
                            "max", f"{PROM_LINTER_PREFIX}blocking", sel, "linterKey"
                        ),
                        "B",
                        instant=True,
                        table=True,
                    ),
                ],
                {"h": 10, "w": 12, "x": 0, "y": 18},
                transformations=self.join_by_field_transformations(
                    "linterKey",
                    {
                        "Value #A": "Errors",
                        "Value #B": "Blocking",
                        "linterKey": "Linter",
                    },
                    mode="inner",
                ),
                overrides=[
                    self.cell_color_override("Errors", self.red_if_any()),
                    self.cell_color_override(
                        "Blocking",
                        self.red_if_any(),
                        mappings=[
                            {
                                "type": "value",
                                "options": {
                                    "0": {
                                        "text": "NO (warning)",
                                        "color": "yellow",
                                        "index": 0,
                                    },
                                    "1": {"text": "YES", "color": "red", "index": 1},
                                },
                            }
                        ],
                    ),
                ],
                links=[self.linter_link("${__data.fields.Linter:percentencode}")],
                sort_column="Errors",
            ),
            self.timeseries_panel(
                "Health score evolution",
                [
                    self.prom_target(
                        f"min({PROM_RUN_PREFIX}healthScore{{{sel}}})",
                        legend="Health score",
                    )
                ],
                {"h": 10, "w": 12, "x": 12, "y": 18},
                unit="percent",
                thresholds_def=self.health_thresholds(),
                threshold_zones=True,
                min_val=0,
                max_val=100,
            ),
        ]
        return self.dashboard_shell(
            "MegaLinter - 5. Why this rating?",
            "megalinter-rating",
            variables,
            panels,
            "Explanation of the repository rating: score formula, linters breakdown and improvement path",
        )

    def rules_files_dashboard(self):
        sel = 'gitRepoName=~"$repo",gitBranchName=~"$branch"'
        variables = self.datasource_variables() + [
            self.query_variable(
                "repo",
                "Repository",
                f"label_values({PROM_RUN_PREFIX}lintersCount, gitRepoName)",
                multi=True,
            ),
            self.query_variable(
                "branch",
                "Branch",
                f'label_values({PROM_RUN_PREFIX}lintersCount{{gitRepoName=~"$repo"}}, gitBranchName)',
                multi=True,
            ),
        ]
        loki_rule_sel = f'{{{LOKI_BASE},recordType="rule",{sel}}}'
        loki_file_sel = f'{{{LOKI_BASE},recordType="file",{sel}}}'
        panels = [
            self.bargauge_panel(
                "Top rules across repositories (selected period)",
                f"topk(20, sum by (ruleId) (sum_over_time({loki_rule_sel} {LOKI_UNWRAP} [$__range])))",
                {"h": 12, "w": 12, "x": 0, "y": 0},
                datasource=self.ds_loki(),
            ),
            self.bargauge_panel(
                "Top files across repositories (selected period)",
                f"topk(20, sum by (file) (sum_over_time({loki_file_sel} {LOKI_UNWRAP} [$__range])))",
                {"h": 12, "w": 12, "x": 12, "y": 0},
                datasource=self.ds_loki(),
            ),
            self.bargauge_panel(
                "Rule hits by linter (selected period)",
                f"topk(15, sum by (linterKey) (sum_over_time({loki_rule_sel} {LOKI_UNWRAP} [$__range])))",
                {"h": 10, "w": 12, "x": 0, "y": 12},
                datasource=self.ds_loki(),
            ),
            self.timeseries_panel(
                "Errors by descriptor",
                [
                    self.prom_target(
                        f"sum by (descriptor) ({PROM_LINTER_PREFIX}numberErrorsFound{{{sel}}})",
                        legend="{{descriptor}}",
                    )
                ],
                {"h": 10, "w": 12, "x": 12, "y": 12},
                stacking=True,
            ),
            self.timeseries_panel(
                "Rule hits trend",
                [
                    self.loki_target(
                        f"sum by (ruleId) (sum_over_time({loki_rule_sel} {LOKI_UNWRAP} [$__interval]))",
                        legend="{{ruleId}}",
                    )
                ],
                {"h": 10, "w": 12, "x": 0, "y": 22},
                stacking=True,
            ),
            self.table_panel(
                "Hotspot files (file x linter, selected period)",
                [
                    self.loki_target(
                        f"topk(15, sum by (file, linterKey) (sum_over_time("
                        f"{loki_file_sel} {LOKI_UNWRAP} [$__range])))",
                        instant=True,
                    )
                ],
                {"h": 10, "w": 12, "x": 12, "y": 22},
                transformations=[
                    {
                        "id": "organize",
                        "options": {
                            "excludeByName": {"Time": True},
                            "renameByName": {
                                "file": "File",
                                "linterKey": "Linter",
                                "Value #A": "Occurrences",
                            },
                        },
                    }
                ],
                sort_column="Occurrences",
            ),
        ]
        return self.dashboard_shell(
            "MegaLinter - 4. Top Rules & Files",
            "megalinter-rules-files",
            variables,
            panels,
            "Most frequent lint rules and most impacted files across repositories",
            annotations=[
                self.loki_runs_annotation(
                    ',gitRepoName=~"$repo",gitBranchName=~"$branch"'
                )
            ],
        )
