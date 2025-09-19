#!/usr/bin/env python3
"""
Use Kubescape to lint Kubernetes files
"""
from megalinter import Linter, config


class KubescapeLinter(Linter):
    def pre_test(self, test_name):
        if test_name == "test_report_sarif":
            config.set_value(
                self.request_id,
                "KUBERNETES_KUBESCAPE_ARGUMENTS",
                "--controls-config controls-inputs-bad.json",
            )
