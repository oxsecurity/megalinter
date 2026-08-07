#!/usr/bin/env python3
"""
Base class for provider dashboard builders.
Child classes (DashboardBuilderGrafana, DashboardBuilderDatadog,
DashboardBuilderElastic, DashboardBuilderNewRelic) generate the dashboard
definition files of docs/dashboards/ from the metrics contract.
"""

import json


class DashboardBuilder:
    provider: str = ""

    # Return {relative_path: file_content} for the files of this provider
    def build(self) -> dict:
        return {}

    # Return the manifest entries describing the generated dashboards
    def manifest_entries(self) -> list:
        return []

    def to_json(self, content) -> str:
        return json.dumps(content, indent=2, sort_keys=False) + "\n"
