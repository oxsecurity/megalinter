#!/usr/bin/env python3
"""
Use Kubeconform to lint json and yml files
"""

from megalinter import Linter, config


class KubeconformLinter(Linter):
    def pre_test(self, test_name):
        if test_name == "test_success_project_lint_mode":
            config.set_value(
                self.request_id,
                "KUBERNETES_KUBECONFORM_ARGUMENTS",
                "-ignore-filename-pattern .*/bad/.*",
            )
