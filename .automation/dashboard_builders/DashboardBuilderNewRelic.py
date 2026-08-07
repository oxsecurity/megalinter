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
        link_to=None,
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
        # linkedEntityGuids must be a top-level sibling of rawConfiguration in
        # the NerdGraph widget schema. Markers are consumed at upload time:
        # replaced by the guid of the matching page so that clicking a facet
        # opens the filtered page
        if link_to == "repository":
            result["linkedEntityGuids"] = ["__REPOSITORY_DETAIL_PAGE_GUID__"]
        elif link_to == "rating":
            result["linkedEntityGuids"] = ["__RATING_PAGE_GUID__"]
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

    def markdown_widget(self, text, row, column, width=6, height=4):
        return {
            "title": "",
            "layout": {"column": column, "row": row, "width": width, "height": height},
            "visualization": {"id": "viz.markdown"},
            "rawConfiguration": {"text": text},
        }

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
                    "options": {"ignoreTimeRange": True},
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
                    "options": {"ignoreTimeRange": True},
                },
            ],
            "pages": [
                {
                    "name": "Overview",
                    "widgets": [
                        self.widget(
                            "Quality gate pass rate (%)",
                            "viz.billboard",
                            f"SELECT average(`{run}qualityGate`) * 100 AS 'Pass rate %' "
                            "FROM Metric WHERE source = 'MegaLinter'"
                            " AND gitBranchName LIKE {{gitBranchName}} SINCE 30 days ago",
                            1,
                            1,
                            width=3,
                        ),
                        self.widget(
                            "Quality gate failure rate (%)",
                            "viz.billboard",
                            f"SELECT (1 - average(`{run}qualityGate`)) * 100 AS 'Failure rate %' "
                            "FROM Metric WHERE source = 'MegaLinter'"
                            " AND gitBranchName LIKE {{gitBranchName}} SINCE 30 days ago",
                            1,
                            4,
                            width=3,
                            thresholds=[
                                {"alertSeverity": "WARNING", "value": 1},
                                {"alertSeverity": "CRITICAL", "value": 25},
                            ],
                        ),
                        self.widget(
                            "Blocking errors",
                            "viz.billboard",
                            f"SELECT latest(`{run}blockingErrors`) AS 'Blocking errors' "
                            "FROM Metric WHERE source = 'MegaLinter'"
                            " AND gitBranchName LIKE {{gitBranchName}} "
                            "FACET gitRepoName LIMIT 50 SINCE 30 days ago",
                            1,
                            7,
                            width=3,
                            link_to="repository",
                            thresholds=[
                                {"alertSeverity": "WARNING", "value": 1},
                                {"alertSeverity": "CRITICAL", "value": 10},
                            ],
                        ),
                        self.widget(
                            "Errors auto-fixed",
                            "viz.billboard",
                            f"SELECT sum(`{run}totalErrorsFixed`) AS 'Errors fixed' "
                            "FROM Metric WHERE source = 'MegaLinter'"
                            " AND gitBranchName LIKE {{gitBranchName}} "
                            "FACET gitRepoName LIMIT 50 SINCE 30 days ago",
                            1,
                            10,
                            width=3,
                            link_to="repository",
                        ),
                        self.widget(
                            "Repository health score evolution",
                            "viz.line",
                            f"SELECT max(`{run}healthScore`) FROM Metric "
                            "WHERE source = 'MegaLinter'"
                            " AND gitBranchName LIKE {{gitBranchName}} "
                            "FACET gitRepoName LIMIT 25 TIMESERIES 1 day SINCE 30 days ago",
                            4,
                            1,
                            width=6,
                            link_to="repository",
                        ),
                        self.widget(
                            "Run duration by repository (s)",
                            "viz.line",
                            f"SELECT max(`{run}runDurationS`) FROM Metric "
                            "WHERE source = 'MegaLinter'"
                            " AND gitBranchName LIKE {{gitBranchName}} "
                            "FACET gitRepoName LIMIT 25 TIMESERIES 1 day SINCE 30 days ago",
                            4,
                            7,
                            width=6,
                            link_to="repository",
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
                            "WHERE recordType = 'rule' AND source = 'MegaLinter'"
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
                            "WHERE recordType = 'file' AND source = 'MegaLinter'"
                            " AND gitBranchName LIKE {{gitBranchName}} "
                            "FACET file, linterKey SINCE 30 days ago LIMIT 20",
                            7,
                            9,
                            width=4,
                            height=4,
                        ),
                        self.widget(
                            "Runs (period)",
                            "viz.billboard",
                            "SELECT count(*) AS 'Runs' FROM Log "
                            "WHERE recordType = 'run' AND source = 'MegaLinter'"
                            " AND gitBranchName LIKE {{gitBranchName}} SINCE 30 days ago",
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
                            " AND gitBranchName LIKE {{gitBranchName}} TIMESERIES 1 day SINCE 30 days ago",
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
                            " AND gitBranchName LIKE {{gitBranchName}} "
                            "FACET gitRepoName LIMIT 25 TIMESERIES 1 day SINCE 30 days ago",
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
                            " AND gitBranchName LIKE {{gitBranchName}} "
                            "FACET gitRepoName LIMIT 25 TIMESERIES 1 day SINCE 30 days ago",
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
                            "WHERE recordType = 'run' AND source = 'MegaLinter'"
                            " AND gitBranchName LIKE {{gitBranchName}} FACET gitRepoName SINCE 30 days ago LIMIT 50",
                            14,
                            9,
                            width=4,
                            height=4,
                        ),
                        self.widget(
                            "Rating (A-E)",
                            "viz.pie",
                            f"SELECT count(*) FROM Metric WHERE metricName = '{run}healthScore' "
                            "AND source = 'MegaLinter'"
                            " AND gitRepoName LIKE {{gitRepoName}}"
                            " AND gitBranchName LIKE {{gitBranchName}} "
                            f"FACET cases(WHERE `{run}healthScore` >= 90 AS 'A', "
                            f"WHERE `{run}healthScore` >= 80 AS 'B', "
                            f"WHERE `{run}healthScore` >= 65 AS 'C', "
                            f"WHERE `{run}healthScore` >= 50 AS 'D', "
                            f"WHERE `{run}healthScore` < 50 AS 'E') SINCE 30 days ago",
                            18,
                            1,
                            width=4,
                            height=4,
                            link_to="rating",
                        ),
                        self.widget(
                            "Top auto-fixing linters",
                            "viz.bar",
                            f"SELECT sum(`{linter}numberErrorsFixed`) AS 'Errors fixed' "
                            "FROM Metric WHERE source = 'MegaLinter'"
                            " AND gitBranchName LIKE {{gitBranchName}} FACET linterKey SINCE 30 days ago LIMIT 15",
                            18,
                            5,
                            width=8,
                            height=4,
                        ),
                        self.widget(
                            "Total errors by repository",
                            "viz.line",
                            f"SELECT max(`{run}totalErrors`) FROM Metric "
                            "WHERE source = 'MegaLinter'"
                            " AND gitBranchName LIKE {{gitBranchName}} "
                            "FACET gitRepoName LIMIT 25 TIMESERIES 1 day SINCE 30 days ago",
                            22,
                            1,
                            width=12,
                            link_to="repository",
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
                            link_to="rating",
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
                            "FACET gitBranchName TIMESERIES 1 day SINCE 30 days ago",
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
                            "TIMESERIES 1 day SINCE 30 days ago",
                            4,
                            7,
                            width=6,
                            series_colors=[
                                ("Blocking", "#d62728"),
                                ("Non-blocking", "#ffbf00"),
                            ],
                        ),
                        self.widget(
                            "Errors by linter over time",
                            "viz.area",
                            f"SELECT max(`{linter}numberErrorsFound`) FROM Metric "
                            "WHERE source = 'MegaLinter'"
                            " AND gitBranchName LIKE {{gitBranchName}} AND gitRepoName LIKE {{gitRepoName}} "
                            "FACET linterKey TIMESERIES 1 day SINCE 30 days ago",
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
                            "FACET descriptor TIMESERIES 1 day SINCE 30 days ago",
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
                            "WHERE recordType = 'rule' AND source = 'MegaLinter'"
                            " AND gitBranchName LIKE {{gitBranchName}} AND gitRepoName LIKE {{gitRepoName}} "
                            "FACET ruleId, linterKey SINCE 30 days ago LIMIT 20",
                            10,
                            5,
                        ),
                        self.widget(
                            "Top files",
                            "viz.table",
                            "SELECT sum(occurrences) AS 'Occurrences' FROM Log "
                            "WHERE recordType = 'file' AND source = 'MegaLinter'"
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
                            "TIMESERIES 1 day SINCE 30 days ago",
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
                            "TIMESERIES 1 day SINCE 30 days ago",
                            13,
                            7,
                            width=6,
                        ),
                    ],
                },
                {
                    "name": "Why this rating?",
                    "widgets": [
                        self.markdown_widget(
                            "## How the rating / health score is computed\n\n"
                            "Health score (0-100) = `100 x (linters in success + 0.5 x "
                            "linters with non-blocking errors) / total linters`\n\n"
                            "| Rating | Health score |\n"
                            "|---|---|\n"
                            "| A | >= 90 |\n"
                            "| B | >= 80 |\n"
                            "| C | >= 65 |\n"
                            "| D | >= 50 |\n"
                            "| E | < 50 |\n\n"
                            "To improve it: fix the linters in error first (full share "
                            "each), then the warnings (half share each). "
                            "Use the Repository and Branch variables to focus this page.",
                            1,
                            1,
                            width=6,
                            height=4,
                        ),
                        self.widget(
                            "Health score",
                            "viz.billboard",
                            f"SELECT latest(`{run}healthScore`) AS 'Health score' "
                            "FROM Metric WHERE source = 'MegaLinter'"
                            " AND gitRepoName LIKE {{gitRepoName}}"
                            " AND gitBranchName LIKE {{gitBranchName}} SINCE 30 days ago",
                            1,
                            7,
                            width=3,
                        ),
                        self.widget(
                            "Total linters",
                            "viz.billboard",
                            f"SELECT latest(`{run}lintersCount`) AS 'Linters' "
                            "FROM Metric WHERE source = 'MegaLinter'"
                            " AND gitRepoName LIKE {{gitRepoName}}"
                            " AND gitBranchName LIKE {{gitBranchName}} SINCE 30 days ago",
                            1,
                            10,
                            width=3,
                        ),
                        self.widget(
                            "Linters in success",
                            "viz.billboard",
                            f"SELECT latest(`{run}lintersSuccess`) AS 'Success' "
                            "FROM Metric WHERE source = 'MegaLinter'"
                            " AND gitRepoName LIKE {{gitRepoName}}"
                            " AND gitBranchName LIKE {{gitBranchName}} SINCE 30 days ago",
                            5,
                            1,
                        ),
                        self.widget(
                            "Linters with warnings (0.5 share)",
                            "viz.billboard",
                            f"SELECT latest(`{run}lintersWarning`) AS 'Warnings' "
                            "FROM Metric WHERE source = 'MegaLinter'"
                            " AND gitRepoName LIKE {{gitRepoName}}"
                            " AND gitBranchName LIKE {{gitBranchName}} SINCE 30 days ago",
                            5,
                            5,
                            thresholds=[{"alertSeverity": "WARNING", "value": 1}],
                        ),
                        self.widget(
                            "Linters in error (0 share)",
                            "viz.billboard",
                            f"SELECT latest(`{run}lintersError`) AS 'Errors' "
                            "FROM Metric WHERE source = 'MegaLinter'"
                            " AND gitRepoName LIKE {{gitRepoName}}"
                            " AND gitBranchName LIKE {{gitBranchName}} SINCE 30 days ago",
                            5,
                            9,
                            thresholds=[{"alertSeverity": "CRITICAL", "value": 1}],
                        ),
                        self.widget(
                            "Linters dragging the score down",
                            "viz.table",
                            f"SELECT latest(`{linter}numberErrorsFound`) AS 'Errors', "
                            f"latest(`{linter}blocking`) AS 'Blocking' FROM Metric "
                            "WHERE source = 'MegaLinter'"
                            " AND gitRepoName LIKE {{gitRepoName}}"
                            " AND gitBranchName LIKE {{gitBranchName}} "
                            "FACET linterKey SINCE 30 days ago LIMIT 50",
                            8,
                            1,
                            width=12,
                            height=4,
                        ),
                    ],
                },
            ],
        }
