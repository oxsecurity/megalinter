import logging
import os
import urllib
from pytablewriter import MarkdownTableWriter
from megalinter import config
from megalinter.constants import (
    ML_DOC_URL,
    ML_DOC_URL_DESCRIPTORS_ROOT,
    ML_REPO,
    ML_REPO_ISSUES_URL,
)

mega_linter_version = config.get("BUILD_VERSION", "latest")
DOCS_URL_DESCRIPTORS_ROOT = f"{ML_DOC_URL}/{mega_linter_version}/descriptors"


def build_markdown_summary(reporter_self, action_run_url):
    table_header = ["Descriptor", "Linter", "Files", "Fixed", "Errors"]
    if reporter_self.master.show_elapsed_time is True:
        table_header += ["Elapsed time"]
    table_data_raw = [table_header]
    for linter in reporter_self.master.linters:
        if linter.is_active is True:
            status = (
                "✅"
                if linter.status == "success" and linter.return_code == 0
                else ":warning:"
                if linter.status != "success" and linter.return_code == 0
                else "❌"
            )
            first_col = f"{status} {linter.descriptor_id}"
            lang_lower = linter.descriptor_id.lower()
            linter_name_lower = linter.linter_name.lower().replace("-", "_")
            linter_doc_url = (
                f"{ML_DOC_URL_DESCRIPTORS_ROOT}/{lang_lower}_{linter_name_lower}"
            )
            linter_link = f"[{linter.linter_name}]({linter_doc_url})"
            nb_fixed_cell = str(linter.number_fixed) if linter.try_fix is True else ""
            if linter.cli_lint_mode == "project":
                found = "yes"
                nb_fixed_cell = "yes" if nb_fixed_cell != "" else nb_fixed_cell
                errors_cell = (
                    log_link(f"**{linter.total_number_errors}**", action_run_url)
                    if linter.number_errors > 0
                    else "no"
                )
            else:
                found = str(len(linter.files))
                errors_cell = (
                    log_link(f"**{linter.total_number_errors}**", action_run_url)
                    if linter.number_errors > 0
                    else linter.number_errors
                )
            table_line = [
                first_col,
                linter_link,
                found,
                nb_fixed_cell,
                errors_cell,
            ]
            if reporter_self.master.show_elapsed_time is True:
                table_line += [str(round(linter.elapsed_time_s, 2)) + "s"]
            table_data_raw += [table_line]
    # Build markdown table
    table_data_raw.pop(0)
    writer = MarkdownTableWriter(headers=table_header, value_matrix=table_data_raw)
    table_content = str(writer) + os.linesep if len(table_data_raw) > 1 else ""
    status = (
        "✅"
        if reporter_self.master.return_code == 0
        and reporter_self.master.status == "success"
        else ":warning:"
        if reporter_self.master.status == "warning"
        else "❌"
    )
    status_with_href = (
        status
        + " "
        + log_link(f"**{reporter_self.master.status.upper()}**", action_run_url)
    )
    p_r_msg = (
        f"## [Mega-Linter]({ML_DOC_URL}) status: {status_with_href}"
        + os.linesep
        + os.linesep
    )
    p_r_msg += table_content + os.linesep
    if action_run_url != "":
        p_r_msg += (
            "See errors details in [**artifact Mega-Linter reports** on "
            f"CI Job page]({action_run_url})" + os.linesep
        )
    else:
        p_r_msg += "See errors details in Mega-Linter reports" + os.linesep
    if reporter_self.master.validate_all_code_base is False:
        p_r_msg += (
            "_Set `VALIDATE_ALL_CODEBASE: true` in mega-linter.yml to validate "
            + "all sources, not only the diff_"
            + os.linesep
        )
    if reporter_self.master.flavor_suggestions is not None:
        if reporter_self.master.flavor_suggestions[0] == "new":
            p_r_msg += (
                os.linesep
                + "You could have same capabilities but better runtime performances"
                " if you request a new Mega-Linter flavor.\n"
            )
            body = (
                "Mega-Linter would run faster on my project if I had a flavor containing the following "
                "list of linters: \n\n - Add languages/linters list here\n\n"
                "Would it be possible to create one ? Thanks :relaxed:"
            )
            new_flavor_url = (
                f"{ML_REPO_ISSUES_URL}/new?assignees=&labels=enhancement&template=feature_request.md"
                f"&title={urllib.parse.quote('Request new Mega-Linter flavor')}"
                f"&body={urllib.parse.quote(body)}"
            )
            p_r_msg += f"- [**Click here to request the new flavor**]({new_flavor_url})"
        else:
            p_r_msg += (
                os.linesep
                + "You could have the same capabilities but better runtime performances"
                " if you use a Mega-Linter flavor:" + os.linesep
            )
            for suggestion in reporter_self.master.flavor_suggestions:
                build_version = os.environ.get("BUILD_VERSION", "v5")
                action_version = "v5" if len(build_version) > 20 else build_version
                action_path = (
                    f"{ML_REPO}/flavors/{suggestion['flavor']}@{action_version}"
                )
                p_r_msg += (
                    f"- [**{action_path}**]({ML_DOC_URL}/flavors/{suggestion['flavor']}/)"
                    f" ({suggestion['linters_number']} linters)"
                )
    logging.debug("\n" + p_r_msg)
    return p_r_msg


def log_link(label, url):
    if url == "":
        return label
    else:
        return f"[{label}]({url})"
