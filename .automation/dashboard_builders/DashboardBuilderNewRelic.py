#!/usr/bin/env python3
"""
New Relic dashboard builder: one dashboard (NerdGraph DashboardInput format)
querying the Metric (megalinter.run.*, megalinter.linter.*) and Log
(recordType attribute) data sent by ApiProviderNewRelic.
The ${NEW_RELIC_ACCOUNT_ID} placeholder is replaced at upload time.
"""

from dashboard_builders.contract import (
    NR_LINTER_PREFIX,
    NR_RUN_PREFIX,
    PAYLOAD_VERSION,
)
from dashboard_builders.DashboardBuilder import DashboardBuilder


class DashboardBuilderNewRelic(DashboardBuilder):
    provider = "newrelic"

    def build(self) -> dict:
        return {
            "newrelic/megalinter-overview.json": self.to_json(self.overview_dashboard())
        }

    def manifest_entries(self) -> list:
        return [
            {
                "provider": "newrelic",
                "file": "newrelic/megalinter-overview.json",
                "title": "MegaLinter - Overview",
            }
        ]

    def widget(
        self,
        title,
        viz,
        query,
        row,
        column,
        width=4,
        height=3,
        repo_link=False,
        thresholds=None,
        series_colors=None,
    ):
        result = {
            "title": title,
            "layout": {"column": column, "row": row, "width": width, "height": height},
            "visualization": {"id": viz},
            "rawConfiguration": {
                "facet": {"showOtherSeries": False},
                "nrqlQueries": [
                    {"accountIds": ["${NEW_RELIC_ACCOUNT_ID}"], "query": query}
                ],
                "platformOptions": {"ignoreTimeRange": False},
            },
        }
        if repo_link:
            # Marker consumed at upload time: replaced by the guid of the
            # "Repository detail" page so that clicking a repository facet
            # opens the filtered detail page
            result["rawConfiguration"]["linkedEntityGuids"] = [
                "__REPOSITORY_DETAIL_PAGE_GUID__"
            ]
        if thresholds is not None:
            result["rawConfiguration"]["thresholds"] = thresholds
        if series_colors is not None:
            result["rawConfiguration"]["colors"] = {
                "seriesOverrides": [
                    {"seriesName": name, "color": color}
                    for name, color in series_colors
                ]
            }
        return result

    def overview_dashboard(self):
        run = NR_RUN_PREFIX
        linter = NR_LINTER_PREFIX
        return {
            "name": "MegaLinter - Overview",
            "description": (
                "MegaLinter results: quality gate, errors, linters and top rules. "
                f"Generated from MegaLinter payload v{PAYLOAD_VERSION}."
            ),
            "permissions": "PUBLIC_READ_WRITE",
            "variables": [
                {
                    "name": "gitRepoName",
                    "title": "Repository (Repository detail page)",
                    "type": "NRQL",
                    "isMultiSelection": False,
                    "replacementStrategy": "STRING",
                    "nrqlQuery": {
                        "accountIds": ["${NEW_RELIC_ACCOUNT_ID}"],
                        "query": (
                            "SELECT uniques(gitRepoName) FROM Metric "
                            "WHERE source = 'MegaLinter' SINCE 30 days ago"
                        ),
                    },
                    "defaultValues": [{"value": {"string": "%"}}],
                    "options": {"ignoreTimeRange": False},
                },
                {
                    "name": "gitBranchName",
                    "title": "Branch",
                    "type": "NRQL",
                    "isMultiSelection": False,
                    "replacementStrategy": "STRING",
                    "nrqlQuery": {
                        "accountIds": ["${NEW_RELIC_ACCOUNT_ID}"],
                        "query": (
                            "SELECT uniques(gitBranchName) FROM Metric "
                            "WHERE source = 'MegaLinter' SINCE 30 days ago"
                        ),
                    },
                    "defaultValues": [{"value": {"string": "%"}}],
                    "options": {"ignoreTimeRange": False},
                },
            ],
            "pages": [
                {
                    "name": "Overview",
                    "widgets": [
                        self.widget(
                            "Quality gate pass rate (%)",
                            "viz.billboard",
                            f"SELECT latest(`{run}qualityGate`) * 100 AS 'Pass rate %' "
                            "FROM Metric WHERE source = 'MegaLinter'"
                            " AND gitBranchName LIKE {{gitBranchName}} SINCE 30 days ago",
                            1,
                            1,
                        ),
                        self.widget(
                            "Blocking errors",
                            "viz.billboard",
                            f"SELECT latest(`{run}blockingErrors`) AS 'Blocking errors' "
                            "FROM Metric WHERE source = 'MegaLinter'"
                            " AND gitBranchName LIKE {{gitBranchName}} FACET gitRepoName SINCE 30 days ago",
                            1,
                            5,
                            repo_link=True,
                            thresholds=[
                                {"alertSeverity": "WARNING", "value": 1},
                                {"alertSeverity": "CRITICAL", "value": 10},
                            ],
                        ),
                        self.widget(
                            "Errors auto-fixed",
                            "viz.billboard",
                            f"SELECT latest(`{run}totalErrorsFixed`) AS 'Errors fixed' "
                            "FROM Metric WHERE source = 'MegaLinter'"
                            " AND gitBranchName LIKE {{gitBranchName}} FACET gitIdentifier SINCE 30 days ago",
                            1,
                            9,
                        ),
                        self.widget(
                            "Runs (period)",
                            "viz.billboard",
                            "SELECT count(*) AS 'Runs' FROM Log "
                            "WHERE recordType = 'run' AND gitBranchName LIKE {{gitBranchName}} SINCE 30 days ago",
                            11,
                            1,
                            width=2,
                        ),
                        self.widget(
                            "Time saved by auto-fixes (min)",
                            "viz.billboard",
                            f"SELECT sum(`{run}totalErrorsFixed`) * 5 AS 'Minutes saved' "
                            "FROM Metric WHERE source = 'MegaLinter'"
                            " AND gitBranchName LIKE {{gitBranchName}} SINCE 30 days ago",
                            11,
                            3,
                            width=2,
                        ),
                        self.widget(
                            "Blocking vs non-blocking errors",
                            "viz.line",
                            f"SELECT max(`{run}blockingErrors`) AS 'Blocking', "
                            f"max(`{run}nonBlockingErrors`) AS 'Non-blocking' FROM Metric "
                            "WHERE source = 'MegaLinter'"
                            " AND gitBranchName LIKE {{gitBranchName}} TIMESERIES SINCE 30 days ago",
                            11,
                            5,
                            width=4,
                            series_colors=[
                                ("Blocking", "#d62728"),
                                ("Non-blocking", "#ffbf00"),
                            ],
                        ),
                        self.widget(
                            "Errors auto-fixed by repository",
                            "viz.line",
                            f"SELECT max(`{run}totalErrorsFixed`) FROM Metric "
                            "WHERE source = 'MegaLinter'"
                            " AND gitBranchName LIKE {{gitBranchName}} FACET gitRepoName TIMESERIES SINCE 30 days ago",
                            11,
                            9,
                            width=4,
                        ),
                        self.widget(
                            "Slowest linters (s)",
                            "viz.bar",
                            f"SELECT max(`{linter}elapsedTime`) FROM Metric "
                            "WHERE source = 'MegaLinter'"
                            " AND gitBranchName LIKE {{gitBranchName}} FACET linterKey SINCE 30 days ago LIMIT 15",
                            14,
                            1,
                            width=4,
                            height=4,
                        ),
                        self.widget(
                            "Files analyzed by repository",
                            "viz.line",
                            f"SELECT max(`{run}filesAnalyzed`) FROM Metric "
                            "WHERE source = 'MegaLinter'"
                            " AND gitBranchName LIKE {{gitBranchName}} FACET gitRepoName TIMESERIES SINCE 30 days ago",
                            14,
                            5,
                            width=4,
                            height=4,
                        ),
                        self.widget(
                            "MegaLinter versions",
                            "viz.table",
                            "SELECT latest(`megalinter.megalinterVersion`) AS 'Version', "
                            "latest(`megalinter.megalinterFlavor`) AS 'Flavor' FROM Log "
                            "WHERE recordType = 'run'"
                            " AND gitBranchName LIKE {{gitBranchName}} FACET gitRepoName SINCE 30 days ago LIMIT 50",
                            14,
                            9,
                            width=4,
                            height=4,
                        ),
                        self.widget(
                            "Repository health score evolution",
                            "viz.line",
                            f"SELECT max(`{run}healthScore`) FROM Metric "
                            "WHERE source = 'MegaLinter'"
                            " AND gitBranchName LIKE {{gitBranchName}} FACET gitRepoName TIMESERIES SINCE 30 days ago",
                            4,
                            1,
                            width=6,
                            repo_link=True,
                        ),
                        self.widget(
                            "Total errors by repository",
                            "viz.line",
                            f"SELECT max(`{run}totalErrors`) FROM Metric "
                            "WHERE source = 'MegaLinter'"
                            " AND gitBranchName LIKE {{gitBranchName}} FACET gitRepoName TIMESERIES SINCE 30 days ago",
                            17,
                            1,
                            width=6,
                            repo_link=True,
                        ),
                        self.widget(
                            "Run duration by repository (s)",
                            "viz.line",
                            f"SELECT max(`{run}runDurationS`) FROM Metric "
                            "WHERE source = 'MegaLinter'"
                            " AND gitBranchName LIKE {{gitBranchName}} FACET gitRepoName TIMESERIES SINCE 30 days ago",
                            4,
                            7,
                            width=6,
                            repo_link=True,
                        ),
                        self.widget(
                            "Errors by linter",
                            "viz.bar",
                            f"SELECT max(`{linter}numberErrorsFound`) FROM Metric "
                            "WHERE source = 'MegaLinter'"
                            " AND gitBranchName LIKE {{gitBranchName}} FACET linterKey SINCE 30 days ago LIMIT 15",
                            7,
                            1,
                            width=4,
                            height=4,
                        ),
                        self.widget(
                            "Top rules",
                            "viz.table",
                            "SELECT sum(occurrences) AS 'Occurrences' FROM Log "
                            "WHERE recordType = 'rule'"
                            " AND gitBranchName LIKE {{gitBranchName}} "
                            "FACET ruleId, linterKey SINCE 30 days ago LIMIT 20",
                            7,
                            5,
                            width=4,
                            height=4,
                        ),
                        self.widget(
                            "Top files",
                            "viz.table",
                            "SELECT sum(occurrences) AS 'Occurrences' FROM Log "
                            "WHERE recordType = 'file'"
                            " AND gitBranchName LIKE {{gitBranchName}} "
                            "FACET file, linterKey SINCE 30 days ago LIMIT 20",
                            7,
                            9,
                            width=4,
                            height=4,
                        ),
                    ],
                },
                {
                    "name": "Repository detail",
                    "widgets": [
                        self.widget(
                            "Health score",
                            "viz.billboard",
                            f"SELECT latest(`{run}healthScore`) AS 'Health score' "
                            "FROM Metric WHERE source = 'MegaLinter' AND gitBranchName LIKE {{gitBranchName}} "
                            "AND gitRepoName LIKE {{gitRepoName}} SINCE 30 days ago",
                            1,
                            1,
                        ),
                        self.widget(
                            "Quality gate",
                            "viz.billboard",
                            f"SELECT latest(`{run}qualityGate`) AS 'Quality gate (1=pass)' "
                            "FROM Metric WHERE source = 'MegaLinter' AND gitBranchName LIKE {{gitBranchName}} "
                            "AND gitRepoName LIKE {{gitRepoName}} SINCE 30 days ago",
                            1,
                            5,
                        ),
                        self.widget(
                            "Errors auto-fixed",
                            "viz.billboard",
                            f"SELECT latest(`{run}totalErrorsFixed`) AS 'Errors fixed' "
                            "FROM Metric WHERE source = 'MegaLinter' AND gitBranchName LIKE {{gitBranchName}} "
                            "AND gitRepoName LIKE {{gitRepoName}} SINCE 30 days ago",
                            1,
                            9,
                        ),
                        self.widget(
                            "Health score evolution",
                            "viz.line",
                            f"SELECT max(`{run}healthScore`) FROM Metric "
                            "WHERE source = 'MegaLinter'"
                            " AND gitBranchName LIKE {{gitBranchName}} AND gitRepoName LIKE {{gitRepoName}} "
                            "FACET gitBranchName TIMESERIES SINCE 30 days ago",
                            4,
                            1,
                            width=6,
                        ),
                        self.widget(
                            "Blocking vs non-blocking errors",
                            "viz.line",
                            f"SELECT max(`{run}blockingErrors`) AS 'Blocking', "
                            f"max(`{run}nonBlockingErrors`) AS 'Non-blocking' FROM Metric "
                            "WHERE source = 'MegaLinter'"
                            " AND gitBranchName LIKE {{gitBranchName}} AND gitRepoName LIKE {{gitRepoName}} "
                            "TIMESERIES SINCE 30 days ago",
                            4,
                            7,
                            width=6,
                        ),
                        self.widget(
                            "Errors by linter over time",
                            "viz.area",
                            f"SELECT max(`{linter}numberErrorsFound`) FROM Metric "
                            "WHERE source = 'MegaLinter'"
                            " AND gitBranchName LIKE {{gitBranchName}} AND gitRepoName LIKE {{gitRepoName}} "
                            "FACET linterKey TIMESERIES SINCE 30 days ago",
                            7,
                            1,
                            width=6,
                        ),
                        self.widget(
                            "Errors by language over time",
                            "viz.area",
                            f"SELECT sum(`{linter}numberErrorsFound`) FROM Metric "
                            "WHERE source = 'MegaLinter'"
                            " AND gitBranchName LIKE {{gitBranchName}} AND gitRepoName LIKE {{gitRepoName}} "
                            "FACET descriptor TIMESERIES SINCE 30 days ago",
                            7,
                            7,
                            width=6,
                        ),
                        self.widget(
                            "Slowest linters (s)",
                            "viz.bar",
                            f"SELECT max(`{linter}elapsedTime`) FROM Metric "
                            "WHERE source = 'MegaLinter'"
                            " AND gitBranchName LIKE {{gitBranchName}} AND gitRepoName LIKE {{gitRepoName}} "
                            "FACET linterKey SINCE 30 days ago LIMIT 15",
                            10,
                            1,
                        ),
                        self.widget(
                            "Top rules",
                            "viz.table",
                            "SELECT sum(occurrences) AS 'Occurrences' FROM Log "
                            "WHERE recordType = 'rule'"
                            " AND gitBranchName LIKE {{gitBranchName}} AND gitRepoName LIKE {{gitRepoName}} "
                            "FACET ruleId, linterKey SINCE 30 days ago LIMIT 20",
                            10,
                            5,
                        ),
                        self.widget(
                            "Top files",
                            "viz.table",
                            "SELECT sum(occurrences) AS 'Occurrences' FROM Log "
                            "WHERE recordType = 'file'"
                            " AND gitBranchName LIKE {{gitBranchName}} AND gitRepoName LIKE {{gitRepoName}} "
                            "FACET file, linterKey SINCE 30 days ago LIMIT 20",
                            10,
                            9,
                        ),
                        self.widget(
                            "Run duration (s)",
                            "viz.line",
                            f"SELECT max(`{run}runDurationS`) FROM Metric "
                            "WHERE source = 'MegaLinter'"
                            " AND gitBranchName LIKE {{gitBranchName}} AND gitRepoName LIKE {{gitRepoName}} "
                            "TIMESERIES SINCE 30 days ago",
                            13,
                            1,
                            width=6,
                        ),
                        self.widget(
                            "Files analyzed",
                            "viz.line",
                            f"SELECT max(`{run}filesAnalyzed`) FROM Metric "
                            "WHERE source = 'MegaLinter'"
                            " AND gitBranchName LIKE {{gitBranchName}} AND gitRepoName LIKE {{gitRepoName}} "
                            "TIMESERIES SINCE 30 days ago",
                            13,
                            7,
                            width=6,
                        ),
                    ],
                },
            ],
        }
