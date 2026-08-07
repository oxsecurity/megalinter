#!/usr/bin/env python3
"""
Generate MegaLinter observability dashboards (docs/dashboards/) from the
ApiReporter v2 metrics & logs contract, using one DashboardBuilder class
per provider (.automation/dashboard_builders/).

Usage:
    python .automation/build_dashboards.py            # (re)generate dashboards
    python .automation/build_dashboards.py --check    # fail if out of sync
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dashboard_builders import BUILDER_CLASSES  # noqa: E402
from dashboard_builders.contract import (  # noqa: E402
    BASE_LABELS,
    DD_LINTER_PREFIX,
    DD_RUN_PREFIX,
    LINTER_LABELS,
    LINTER_METRIC_FIELDS,
    NR_LINTER_PREFIX,
    NR_RUN_PREFIX,
    PAYLOAD_VERSION,
    PROM_LINTER_PREFIX,
    PROM_RUN_PREFIX,
    RECORD_TYPES,
    RUN_LABELS,
    RUN_METRIC_FIELDS,
)

REPO_HOME = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
OUTPUT_DIR = os.path.join(REPO_HOME, "docs", "dashboards")


def build_manifest(manifest_entries):
    return {
        "payloadVersion": PAYLOAD_VERSION,
        "generator": ".automation/build_dashboards.py",
        "metrics": {
            "prometheus": (
                [PROM_RUN_PREFIX + field for field in RUN_METRIC_FIELDS]
                + [PROM_LINTER_PREFIX + field for field in LINTER_METRIC_FIELDS]
            ),
            "datadog": (
                [DD_RUN_PREFIX + field for field in RUN_METRIC_FIELDS]
                + [DD_LINTER_PREFIX + field for field in LINTER_METRIC_FIELDS]
            ),
            "newrelic": (
                [NR_RUN_PREFIX + field for field in RUN_METRIC_FIELDS]
                + [NR_LINTER_PREFIX + field for field in LINTER_METRIC_FIELDS]
            ),
        },
        "labels": {
            "base": BASE_LABELS,
            "run": RUN_LABELS,
            "linter": LINTER_LABELS,
            "recordTypes": RECORD_TYPES,
        },
        "dashboards": manifest_entries,
    }


def generate_all():
    outputs = {}
    manifest_entries = []
    for builder_class in BUILDER_CLASSES:
        builder = builder_class()
        outputs.update(builder.build())
        manifest_entries += builder.manifest_entries()
    outputs["manifest.json"] = (
        json.dumps(build_manifest(manifest_entries), indent=2, sort_keys=False) + "\n"
    )
    return outputs


def main():
    check_mode = "--check" in sys.argv
    outputs = generate_all()
    out_of_sync = []
    for rel_path, content in outputs.items():
        target = os.path.join(OUTPUT_DIR, rel_path.replace("/", os.sep))
        if check_mode:
            if not os.path.isfile(target):
                out_of_sync.append(rel_path + " (missing)")
                continue
            with open(target, "r", encoding="utf-8") as f:
                if f.read() != content:
                    out_of_sync.append(rel_path)
        else:
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "w", encoding="utf-8", newline="\n") as f:
                f.write(content)
            print(f"Generated {target}")
    if check_mode:
        if out_of_sync:
            print(
                "Dashboards are out of sync with the metrics contract, "
                "run: python .automation/build_dashboards.py"
            )
            for path in out_of_sync:
                print(f"  - {path}")
            sys.exit(1)
        print("Dashboards are in sync")


if __name__ == "__main__":
    main()
