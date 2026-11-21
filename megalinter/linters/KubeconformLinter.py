#!/usr/bin/env python3
"""
Use Kubeconform to lint json and yml files
"""

from megalinter import Linter, config, utils
from megalinter.sarif_builder import (
    LEVEL_ERROR,
    SarifBuilder,
    SarifResultBuilder,
    SarifRunBuilder,
    to_sarif_uri,
)


class KubeconformLinter(Linter):
    def convert_output_to_sarif(self, return_stdout):
        return kubeconform_json_to_sarif(return_stdout, self.workspace)

    def pre_test(self, test_name):
        if test_name == "test_success_project_lint_mode":
            config.set_value(
                self.request_id,
                "KUBERNETES_KUBECONFORM_ARGUMENTS",
                # Both separators: Windows paths use backslashes (native mode).
                # A list is not split by shlex, which would consume the backslashes
                ["-ignore-filename-pattern", ".*[/\\\\]bad[/\\\\].*"],
            )


# kubeconform gives no line: a resource is identified by its kind and name, and the
# invalid fields by a JSON pointer
def kubeconform_json_to_sarif(stdout, workspace=None):
    run = SarifRunBuilder().init_simple(
        "kubeconform", url="https://github.com/yannh/kubeconform"
    )
    for output in utils.find_json_values(
        stdout, dict, lambda value: isinstance(value.get("resources"), list)
    ):
        for resource in output["resources"]:
            status = resource.get("status")
            if status not in ("statusInvalid", "statusError"):
                continue
            label = f"{resource.get('kind') or ''}/{resource.get('name') or ''}"
            errors = resource.get("validationErrors") or [
                {"path": "", "msg": resource.get("msg")}
            ]
            for error in errors:
                run.add_result(
                    SarifResultBuilder().init_simple(
                        LEVEL_ERROR,
                        f"{label.strip('/')}: {error.get('path') or ''} "
                        f"{error.get('msg') or ''}".strip(),
                        (
                            "invalid-resource"
                            if status == "statusInvalid"
                            else "validation-error"
                        ),
                        file_uri=to_sarif_uri(resource.get("filename"), workspace),
                    )
                )
    return SarifBuilder().add_run(run)
