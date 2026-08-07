#!/usr/bin/env python3
"""
Metrics & logs contract of the ApiReporter v2 payload.
Keep in sync with megalinter/reporters/ApiReporter.py and
megalinter/api_providers/ (checked by build_dashboards.py --check + tests).
"""

PAYLOAD_VERSION = 2

RUN_METRIC_FIELDS = [
    "qualityGate",
    "healthScore",
    "blockingErrors",
    "nonBlockingErrors",
    "totalErrors",
    "totalErrorsFixed",
    "lintersCount",
    "lintersSuccess",
    "lintersWarning",
    "lintersError",
    "filesAnalyzed",
    "runDurationS",
]

LINTER_METRIC_FIELDS = [
    "numberErrorsFound",
    "blocking",
    "numberFilesFound",
    "numberErrorsFixed",
    "elapsedTime",
]

BASE_LABELS = [
    "source",
    "orgIdentifier",
    "gitIdentifier",
    "gitRepoName",
    "gitBranchName",
]

LINTER_LABELS = ["descriptor", "linter", "linterKey"]

# Extra tags on run-level metrics only (low cardinality)
RUN_LABELS = ["megalinterVersion", "megalinterFlavor"]

RECORD_TYPES = ["run", "linter", "rule", "file"]

PROM_RUN_PREFIX = "megalinter_run_"
PROM_LINTER_PREFIX = "megalinter_linter_run_"
DD_RUN_PREFIX = "megalinter.run."
DD_LINTER_PREFIX = "megalinter.linter."
NR_RUN_PREFIX = "megalinter.run."
NR_LINTER_PREFIX = "megalinter.linter."

LOKI_BASE = 'source="MegaLinter"'
