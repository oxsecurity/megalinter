#!/usr/bin/env python3
"""
Datadog dashboard builder: one ordered dashboard querying the metrics
(megalinter.run.*, megalinter.linter.*) and the logs (record_type tags)
sent by ApiProviderDatadog.
"""

from dashboard_builders.contract import (
    DD_LINTER_PREFIX,
    DD_RUN_PREFIX,
    PAYLOAD_VERSION,
)
from dashboard_builders.DashboardBuilder import DashboardBuilder


class DashboardBuilderDatadog(DashboardBuilder):
    provider = "datadog"

    def build(self) -> dict:
        return {
            "datadog/megalinter-overview.json": self.to_json(self.overview_dashboard())
        }

    def manifest_entries(self) -> list:
        return [
            {
                "provider": "datadog",
                "file": "datadog/megalinter-overview.json",
                "title": "MegaLinter - Overview",
            }
        ]

    # __SELF_URL__ is replaced by the dashboard path at upload time
    def repo_links(self):
        return [
            {
                "label": "Focus on this repository",
                "link": "__SELF_URL__?tpl_var_git_repo_name={{git_repo_name.value}}",
            }
        ]

    def metric_query(self, name, query, aggregator=None):
        result = {"data_source": "metrics", "name": name, "query": query}
        if aggregator is not None:
            result["aggregator"] = aggregator
        return result

    # Palettes of value-conditional formats for query_value / toplist widgets
    def good_when_high(self, warning=50, good=90):
        return [
            {"comparator": ">=", "value": good, "palette": "white_on_green"},
            {"comparator": ">=", "value": warning, "palette": "white_on_yellow"},
            {"comparator": "<", "value": warning, "palette": "white_on_red"},
        ]

    def bad_when_any(self):
        return [
            {"comparator": ">", "value": 0, "palette": "white_on_red"},
            {"comparator": "<=", "value": 0, "palette": "white_on_green"},
        ]

    def warn_when_any(self):
        return [
            {"comparator": ">", "value": 0, "palette": "white_on_yellow"},
            {"comparator": "<=", "value": 0, "palette": "white_on_green"},
        ]

    def good_when_any(self):
        return [
            {"comparator": ">", "value": 0, "palette": "white_on_green"},
            {"comparator": "<=", "value": 0, "palette": "white_on_gray"},
        ]

    def query_value(self, title, query, precision=0, conditional_formats=None):
        request = {
            "queries": [self.metric_query("q1", query, "last")],
            "formulas": [{"formula": "q1"}],
            "response_format": "scalar",
        }
        if conditional_formats is not None:
            request["conditional_formats"] = conditional_formats
        return {
            "definition": {
                "title": title,
                "type": "query_value",
                "precision": precision,
                "autoscale": False,
                "requests": [request],
            }
        }

    def timeseries(self, title, query, display_type="line", links=None, palette=None):
        request = {
            "queries": [self.metric_query("q1", query)],
            "formulas": [{"formula": "q1"}],
            "response_format": "timeseries",
            "display_type": display_type,
        }
        if palette is not None:
            request["style"] = {"palette": palette}
        definition = {
            "title": title,
            "type": "timeseries",
            "requests": [request],
        }
        if links is not None:
            definition["custom_links"] = links
        return {"definition": definition}

    def timeseries_multi(self, title, named_queries, display_type="line"):
        return {
            "definition": {
                "title": title,
                "type": "timeseries",
                "requests": [
                    {
                        "queries": [
                            self.metric_query(name, query)
                            for name, query in named_queries
                        ],
                        "formulas": [
                            {"formula": name, "alias": name}
                            for name, _query in named_queries
                        ],
                        "response_format": "timeseries",
                        "display_type": display_type,
                    }
                ],
            }
        }

    def query_value_formula(self, title, query, formula, precision=0):
        return {
            "definition": {
                "title": title,
                "type": "query_value",
                "precision": precision,
                "autoscale": False,
                "requests": [
                    {
                        "queries": [self.metric_query("q1", query, "last")],
                        "formulas": [{"formula": formula}],
                        "response_format": "scalar",
                    }
                ],
            }
        }

    def query_value_logs_count(self, title, search):
        return {
            "definition": {
                "title": title,
                "type": "query_value",
                "precision": 0,
                "autoscale": False,
                "requests": [
                    {
                        "queries": [
                            {
                                "data_source": "logs",
                                "name": "q1",
                                "search": {"query": search},
                                "indexes": ["*"],
                                "group_by": [],
                                "compute": {"aggregation": "count"},
                                "storage": "hot",
                            }
                        ],
                        "formulas": [{"formula": "q1"}],
                        "response_format": "scalar",
                    }
                ],
            }
        }

    def toplist_metrics(self, title, query, links=None, conditional_formats=None):
        request = {
            "queries": [self.metric_query("q1", query, "last")],
            "formulas": [{"formula": "q1", "limit": {"count": 15, "order": "desc"}}],
            "response_format": "scalar",
        }
        if conditional_formats is not None:
            request["conditional_formats"] = conditional_formats
        definition = {
            "title": title,
            "type": "toplist",
            "requests": [request],
        }
        if links is not None:
            definition["custom_links"] = links
        return {"definition": definition}

    def toplist_logs(self, title, search, facet):
        return {
            "definition": {
                "title": title,
                "type": "toplist",
                "requests": [
                    {
                        "queries": [
                            {
                                "data_source": "logs",
                                "name": "q1",
                                "search": {"query": search},
                                "indexes": ["*"],
                                "group_by": [
                                    {
                                        "facet": facet,
                                        "limit": 15,
                                        "sort": {
                                            "aggregation": "sum",
                                            "metric": "@megalinter.occurrences",
                                            "order": "desc",
                                        },
                                    }
                                ],
                                "compute": {
                                    "aggregation": "sum",
                                    "metric": "@megalinter.occurrences",
                                },
                                "storage": "hot",
                            }
                        ],
                        "formulas": [
                            {"formula": "q1", "limit": {"count": 15, "order": "desc"}}
                        ],
                        "response_format": "scalar",
                    }
                ],
            }
        }

    def note(self, content):
        return {
            "definition": {
                "type": "note",
                "content": content,
                "background_color": "white",
                "font_size": "14",
                "text_align": "left",
                "show_tick": False,
            }
        }

    def group(self, title, widgets):
        return {
            "definition": {
                "type": "group",
                "layout_type": "ordered",
                "title": title,
                "widgets": widgets,
            }
        }

    def log_stream(self, title, query):
        return {
            "definition": {
                "title": title,
                "type": "log_stream",
                "query": query,
                "columns": ["core_host", "core_service"],
                "show_date_column": True,
                "show_message_column": True,
                "message_display": "expanded-md",
                "sort": {"column": "time", "order": "desc"},
            }
        }

    def overview_dashboard(self):
        return {
            "title": "MegaLinter - Overview",
            "description": (
                "MegaLinter results: quality gate, errors, linters and top rules. "
                f"Generated from MegaLinter payload v{PAYLOAD_VERSION}."
            ),
            "layout_type": "ordered",
            "reflow_type": "auto",
            "template_variables": [
                {
                    "name": "git_repo_name",
                    "prefix": "git_repo_name",
                    "available_values": [],
                    "default": "*",
                },
                {
                    "name": "git_branch_name",
                    "prefix": "git_branch_name",
                    "available_values": [],
                    "default": "*",
                },
            ],
            "widgets": [
                self.query_value(
                    "Quality gate pass rate (%)",
                    f"avg:{DD_RUN_PREFIX}qualityGate{{$git_repo_name,$git_branch_name}} * 100",
                    conditional_formats=self.good_when_high(),
                ),
                self.query_value(
                    "Health score (avg)",
                    f"avg:{DD_RUN_PREFIX}healthScore{{$git_repo_name,$git_branch_name}}",
                    conditional_formats=self.good_when_high(warning=50, good=80),
                ),
                self.query_value_formula(
                    "Repositories monitored",
                    f"max:{DD_RUN_PREFIX}lintersCount{{$git_repo_name,$git_branch_name}} by {{git_repo_name}}",
                    "count_nonzero(q1)",
                ),
                self.query_value_logs_count(
                    "Runs (period)",
                    "source:megalinter record_type:run $git_repo_name $git_branch_name",
                ),
                self.query_value(
                    "Blocking errors",
                    f"sum:{DD_RUN_PREFIX}blockingErrors{{$git_repo_name,$git_branch_name}}",
                    conditional_formats=self.bad_when_any(),
                ),
                self.query_value(
                    "Non-blocking errors",
                    f"sum:{DD_RUN_PREFIX}nonBlockingErrors{{$git_repo_name,$git_branch_name}}",
                    conditional_formats=self.warn_when_any(),
                ),
                self.query_value(
                    "Errors auto-fixed",
                    f"sum:{DD_RUN_PREFIX}totalErrorsFixed{{$git_repo_name,$git_branch_name}}",
                    conditional_formats=self.good_when_any(),
                ),
                self.query_value_formula(
                    "Estimated time saved by auto-fixes (min, 5 min/fix)",
                    f"sum:{DD_RUN_PREFIX}totalErrorsFixed{{$git_repo_name,$git_branch_name}}",
                    "q1 * 5",
                ),
                self.timeseries(
                    "Repository health score evolution",
                    f"max:{DD_RUN_PREFIX}healthScore{{$git_repo_name,$git_branch_name}} by {{git_repo_name}}",
                    links=self.repo_links(),
                    palette="cool",
                ),
                self.timeseries(
                    "Total errors by repository",
                    f"max:{DD_RUN_PREFIX}totalErrors{{$git_repo_name,$git_branch_name}} by {{git_repo_name}}",
                    links=self.repo_links(),
                    palette="warm",
                ),
                self.timeseries(
                    "Errors by linter over time",
                    f"max:{DD_LINTER_PREFIX}numberErrorsFound{{$git_repo_name,$git_branch_name}} by {{linter_key}}",
                    palette="warm",
                ),
                self.timeseries(
                    "Errors by language over time",
                    f"sum:{DD_LINTER_PREFIX}numberErrorsFound{{$git_repo_name,$git_branch_name}} by {{descriptor}}",
                    display_type="bars",
                    palette="orange",
                ),
                self.timeseries_multi(
                    "Blocking vs non-blocking errors",
                    [
                        (
                            "blocking",
                            f"sum:{DD_RUN_PREFIX}blockingErrors{{$git_repo_name,$git_branch_name}}",
                        ),
                        (
                            "nonblocking",
                            f"sum:{DD_RUN_PREFIX}nonBlockingErrors{{$git_repo_name,$git_branch_name}}",
                        ),
                    ],
                ),
                self.timeseries(
                    "Run duration by repository (s)",
                    f"max:{DD_RUN_PREFIX}runDurationS{{$git_repo_name,$git_branch_name}} by {{git_repo_name}}",
                    links=self.repo_links(),
                    palette="purple",
                ),
                self.timeseries(
                    "Errors auto-fixed by repository",
                    f"max:{DD_RUN_PREFIX}totalErrorsFixed{{$git_repo_name,$git_branch_name}} by {{git_repo_name}}",
                    display_type="bars",
                ),
                self.toplist_metrics(
                    "Errors by linter",
                    f"max:{DD_LINTER_PREFIX}numberErrorsFound{{$git_repo_name,$git_branch_name}} by {{linter_key}}",
                    conditional_formats=self.bad_when_any(),
                ),
                self.toplist_metrics(
                    "Slowest linters (s)",
                    f"max:{DD_LINTER_PREFIX}elapsedTime{{$git_repo_name,$git_branch_name}} by {{linter_key}}",
                    conditional_formats=[
                        {"comparator": ">", "value": 30, "palette": "white_on_yellow"},
                        {"comparator": "<=", "value": 30, "palette": "white_on_green"},
                    ],
                ),
                self.toplist_logs(
                    "Top rules",
                    "source:megalinter record_type:rule $git_repo_name $git_branch_name",
                    "@megalinter.ruleId",
                ),
                self.toplist_logs(
                    "Top files",
                    "source:megalinter record_type:file $git_repo_name $git_branch_name",
                    "@megalinter.file",
                ),
                self.group(
                    "Why this rating?",
                    [
                        self.note(
                            "**How the rating / health score is computed**\\n\\nHealth score (0-100) = `100 x "
                            "(linters in success + 0.5 x linters with non-blocking errors) / total "
                            "linters`\\n\\nA >= 90, B >= 80, C >= 65, D >= 50, E < 50.\\n\\nTo improve it: "
                            "fix the linters in error first (full share each), then the warnings (half share "
                            "each). Use the `git_repo_name` template variable to focus on one repository."
                        ),
                        self.query_value(
                            "Linters in success",
                            f"sum:{DD_RUN_PREFIX}lintersSuccess{{$git_repo_name,$git_branch_name}}",
                            conditional_formats=self.good_when_any(),
                        ),
                        self.query_value(
                            "Linters with warnings (0.5 share)",
                            f"sum:{DD_RUN_PREFIX}lintersWarning{{$git_repo_name,$git_branch_name}}",
                            conditional_formats=self.warn_when_any(),
                        ),
                        self.query_value(
                            "Linters in error (0 share)",
                            f"sum:{DD_RUN_PREFIX}lintersError{{$git_repo_name,$git_branch_name}}",
                            conditional_formats=self.bad_when_any(),
                        ),
                        self.toplist_metrics(
                            "Linters dragging the score down",
                            f"max:{DD_LINTER_PREFIX}numberErrorsFound{{$git_repo_name,$git_branch_name}} by "
                            f"{{linter_key}}",
                            conditional_formats=self.bad_when_any(),
                        ),
                    ],
                ),
                self.log_stream(
                    "MegaLinter runs & linters",
                    "source:megalinter (record_type:run OR record_type:linter) $git_repo_name $git_branch_name",
                ),
            ],
        }
