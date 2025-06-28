# flake8: noqa: E203
import json
import logging
import os
import subprocess
import time
import urllib

from megalinter import config, utils
from megalinter.constants import (
    DEFAULT_RELEASE,
    ML_DOC_URL,
    ML_DOC_URL_DESCRIPTORS_ROOT,
    ML_REPO,
    ML_REPO_ISSUES_URL,
    OX_MARKDOWN_LINK,
)
from pytablewriter import Align, MarkdownTableWriter
from pytablewriter.style import Style
from redis import Redis


def build_markdown_summary(reporter_self, action_run_url=""):
    markdown_summary_type = config.get(
        reporter_self.master.request_id, "REPORTERS_MARKDOWN_SUMMARY_TYPE", "table"
    )
    if markdown_summary_type == "sections":
        return build_markdown_summary_sections(reporter_self, action_run_url)
    else:
        return build_markdown_summary_table(reporter_self, action_run_url)


def build_markdown_summary_table(reporter_self, action_run_url=""):
    table_header = ["Descriptor", "Linter", "Files", "Fixed", "Errors", "Warnings"]
    table_column_styles = [
        Style(align=Align.LEFT),
        Style(align=Align.LEFT),
        Style(align=Align.RIGHT),
        Style(align=Align.RIGHT),
        Style(align=Align.RIGHT),
        Style(align=Align.RIGHT),
    ]
    if reporter_self.master.show_elapsed_time is True:
        table_header += ["Elapsed time"]
        table_column_styles += [Style(align=Align.RIGHT)]

    table_data_raw = []
    for linter in reporter_self.master.linters:
        if linter.is_active is True:
            linter_data = get_linter_summary_data(linter, action_run_url)

            first_col = f"{linter_data['status']} {linter_data['descriptor_id']}"
            table_line = [
                first_col,
                linter_data["linter_link"],
                linter_data["found"],
                linter_data["nb_fixed_cell"],
                linter_data["errors_cell"],
                linter_data["warnings_cell"],
            ]
            if reporter_self.master.show_elapsed_time is True:
                table_line += [str(linter_data["elapsed_time"]) + "s"]
            table_data_raw += [table_line]

    # Build markdown table
    writer = MarkdownTableWriter(
        headers=table_header,
        column_styles=table_column_styles,
        value_matrix=table_data_raw,
    )
    table_content = str(writer)

    # Build complete message using helper functions
    p_r_msg = build_markdown_summary_header(reporter_self, action_run_url)
    p_r_msg += table_content + os.linesep
    p_r_msg += build_markdown_summary_footer(reporter_self, action_run_url)

    logging.debug("\n" + p_r_msg)
    return p_r_msg


def build_markdown_summary_sections(reporter_self, action_run_url=""):
    """Build markdown summary using HTML sections with summary/details tags for each linter"""

    # Build complete message using helper functions
    p_r_msg = build_markdown_summary_header(reporter_self, action_run_url)

    # Separate linters into two groups: those with issues and those that are OK
    linters_with_issues = []
    linters_ok = []

    for linter in reporter_self.master.linters:
        if linter.is_active is True:
            # Check if linter has errors or warnings (fixes alone are not considered issues)
            has_errors = linter.number_errors > 0
            has_warnings = linter.total_number_warnings > 0

            if has_errors or has_warnings:
                linters_with_issues.append(linter)
            else:
                linters_ok.append(linter)

    # Sort linters with issues: error icons (❌) first, then warning icons (⚠️)
    def sort_linters_by_icon_severity(linter):
        # Get the linter status icon to determine sorting priority
        linter_status_icon = (
            "✅"
            if linter.status == "success" and linter.return_code == 0
            else (
                "⚠️" if linter.status != "success" and linter.return_code == 0 else "❌"
            )
        )

        # Return tuple for sorting: (icon_priority, linter_name)
        # icon_priority: 0 for ❌ (error - highest priority), 1 for ⚠️ (warning), 2 for ✅ (success)
        icon_priority = (
            0 if linter_status_icon == "❌" else (1 if linter_status_icon == "⚠️" else 2)
        )
        return (icon_priority, linter.linter_name.lower())

    linters_with_issues.sort(key=sort_linters_by_icon_severity)

    # Calculate available space per linter based on total linters with issues
    max_total_chars = 40000
    total_linters_with_issues = len(linters_with_issues)
    max_chars_per_linter = max_total_chars // max(total_linters_with_issues, 1)

    # Build sections for linters with issues first
    for linter in linters_with_issues:
        linter_data = get_linter_summary_data(linter, action_run_url)

        # Build section header summary
        # Build concise single-line summary
        status_icon = linter_data["status"]
        descriptor = linter_data["descriptor_id"]
        linter_name = linter.linter_name

        # Start with basic info
        summary_text = f"{status_icon} {descriptor} / {linter_name}"

        # Add most critical info only (without hyperlinks for sections format)
        if linter.number_errors > 0:
            error_word = "error" if linter.total_number_errors == 1 else "errors"
            summary_text += f" - {linter.total_number_errors} {error_word}"
        elif linter.total_number_warnings > 0:
            warning_word = (
                "warning" if linter.total_number_warnings == 1 else "warnings"
            )
            summary_text += f" - {linter.total_number_warnings} {warning_word}"
        elif linter_data["nb_fixed_cell"] and linter_data["nb_fixed_cell"] != "":
            # For nb_fixed_cell, use the plain value without links
            fixed_count = (
                str(linter.number_fixed)
                if linter.try_fix is True and linter.cli_lint_mode != "project"
                else "yes"
            )
            summary_text += f" - {fixed_count} fixed"

        # Get linter text output for details section
        text_report_sub_folder = config.get(
            reporter_self.master.request_id, "TEXT_REPORTER_SUB_FOLDER", "linters_logs"
        )
        text_file_name = (
            f"{reporter_self.report_folder}{os.path.sep}"
            f"{text_report_sub_folder}{os.path.sep}"
            f"{linter.status.upper()}-{linter.name}.log"
        )

        linter_output = ""
        if os.path.isfile(text_file_name):
            try:
                with open(text_file_name, "r", encoding="utf-8") as text_file:
                    linter_output = text_file.read()
                    # Remove all lines until the first "Linter raw log:", including such line
                    separator_pos = linter_output.find("Linter raw log:")
                    if separator_pos != -1:
                        # Find the end of the line containing the separator
                        next_newline = linter_output.find("\n", separator_pos)
                        if next_newline != -1:
                            linter_output = linter_output[
                                next_newline + 1 :
                            ].strip()  # noqa: E203
                    # Truncate long output to 1000 characters
                    if len(linter_output) > max_chars_per_linter:
                        total_chars = len(linter_output)
                        linter_output = (
                            linter_output[:max_chars_per_linter]
                            + f"\n\n(Truncated to {max_chars_per_linter} characters out of {total_chars})"
                        )
                    if linter_output.strip():
                        # Escape any HTML in the output and wrap in code block
                        linter_output = f"```\n{linter_output.strip()}\n```"
                    else:
                        linter_output = "No output available"
            except Exception as e:
                linter_output = f"Error reading linter output: {str(e)}"
        else:
            linter_output = "Linter output file not found"

        # Build HTML section
        p_r_msg += f"<details>\n<summary>{summary_text}</summary>\n\n{linter_output}\n\n</details>\n\n"

    # Add summary section for OK linters
    if linters_ok:
        p_r_msg += "### ✅ Linters with no issues\n\n"
        ok_linter_names = []
        for linter in linters_ok:
            linter_data = get_linter_summary_data(linter, action_run_url)

            # Check if this linter has fixes
            has_fixes = linter.try_fix is True and (
                (linter.cli_lint_mode != "project" and linter.number_fixed > 0)
                or (linter.cli_lint_mode == "project" and linter.number_fixed > 0)
            )

            # Build linter name with fix info in parentheses
            linter_text = linter_data["linter_link"]

            if has_fixes:
                if linter.cli_lint_mode == "project":
                    linter_text += " (fixes applied)"
                else:
                    fix_word = "fix" if linter.number_fixed == 1 else "fixes"
                    linter_text += f" ({linter.number_fixed} {fix_word})"

            ok_linter_names.append((linter.linter_name, linter_text))

        # Sort alphabetically by linter name and extract the formatted text
        ok_linter_names.sort(key=lambda x: x[0])
        sorted_linter_texts = [text for _, text in ok_linter_names]

        p_r_msg += ", ".join(sorted_linter_texts) + "\n\n"

    # Add footer content
    p_r_msg += build_markdown_summary_footer(reporter_self, action_run_url)

    logging.debug("\n" + p_r_msg)
    return p_r_msg


def build_markdown_summary_header(reporter_self, action_run_url=""):
    """Build the common header for markdown summaries"""
    status = (
        "✅"
        if reporter_self.master.return_code == 0
        and reporter_self.master.status == "success"
        else "⚠️" if reporter_self.master.status == "warning" else "❌"
    )
    status_with_href = (
        status
        + " "
        + log_link(f"{reporter_self.master.status.upper()}", action_run_url)
    )
    return (
        f"## [\U0001f999 MegaLinter]({ML_DOC_URL}) status: {status_with_href}"
        + os.linesep
        + os.linesep
    )


def get_linter_summary_data(linter, action_run_url=""):
    """Extract common linter data used by both table and sections formats"""
    # Build linter status icon
    linter_status = (
        "✅"
        if linter.status == "success" and linter.return_code == 0
        else ("⚠️" if linter.status != "success" and linter.return_code == 0 else "❌")
    )

    # Build linter documentation link
    lang_lower = linter.descriptor_id.lower()
    linter_name_lower = linter.linter_name.lower().replace("-", "_")
    linter_doc_url = f"{ML_DOC_URL_DESCRIPTORS_ROOT}/{lang_lower}_{linter_name_lower}"
    linter_link = f"[{linter.linter_name}]({linter_doc_url})"

    # Calculate files/fixes/errors/warnings
    nb_fixed_cell = str(linter.number_fixed) if linter.try_fix is True else ""

    if linter.cli_lint_mode == "project":
        found = "yes"
        nb_fixed_cell = "yes" if nb_fixed_cell != "" else nb_fixed_cell
        errors_cell = (
            log_link(f"{linter.total_number_errors}", action_run_url)
            if linter.number_errors > 0
            else "no"
        )
        warnings_cell = (
            log_link(f"{linter.total_number_warnings}", action_run_url)
            if linter.total_number_warnings > 0
            else "no"
        )
    else:
        found = str(len(linter.files))
        errors_cell = (
            log_link(f"{linter.total_number_errors}", action_run_url)
            if linter.number_errors > 0
            else linter.number_errors
        )
        warnings_cell = (
            log_link(f"{linter.total_number_warnings}", action_run_url)
            if linter.total_number_warnings > 0
            else linter.total_number_warnings
        )

    return {
        "status": linter_status,
        "descriptor_id": linter.descriptor_id,
        "linter_link": linter_link,
        "found": found,
        "nb_fixed_cell": nb_fixed_cell,
        "errors_cell": errors_cell,
        "warnings_cell": warnings_cell,
        "elapsed_time": (
            round(linter.elapsed_time_s, 2) if hasattr(linter, "elapsed_time_s") else 0
        ),
    }


def build_markdown_summary_footer(reporter_self, action_run_url=""):
    """Build the common footer for markdown summaries"""
    footer = ""

    if reporter_self.master.result_message != "":
        footer += reporter_self.master.result_message + os.linesep

    if action_run_url != "":
        footer += (
            "See detailed report in [MegaLinter reports"
            f"]({action_run_url})" + os.linesep
        )
    else:
        footer += "See detailed report in MegaLinter reports" + os.linesep

    if reporter_self.master.validate_all_code_base is False:
        footer += (
            "_Set `VALIDATE_ALL_CODEBASE: true` in mega-linter.yml to validate "
            + "all sources, not only the diff_"
            + os.linesep
        )

    if reporter_self.master.flavor_suggestions is not None:
        if reporter_self.master.flavor_suggestions[0] == "new":
            footer += (
                os.linesep
                + "You could have same capabilities but better runtime performances"
                " if you request a new MegaLinter flavor.\n"
            )
            body = (
                "MegaLinter would run faster on my project if I had a flavor containing the following "
                "list of linters: \n\n - Add languages/linters list here\n\n"
                "Would it be possible to create one ? Thanks :relaxed:"
            )
            new_flavor_url = (
                f"{ML_REPO_ISSUES_URL}/new?assignees=&labels=enhancement&template=feature_request.md"
                f"&title={urllib.parse.quote('Request new MegaLinter flavor')}"
                f"&body={urllib.parse.quote(body)}"
            )
            footer += f"- [Click here to request the new flavor]({new_flavor_url})"
        else:
            footer += (
                os.linesep
                + "You could have the same capabilities but better runtime performances"
                " if you use a MegaLinter flavor:" + os.linesep
            )
            for suggestion in reporter_self.master.flavor_suggestions:
                build_version = config.get(None, "BUILD_VERSION", DEFAULT_RELEASE)
                action_version = (
                    DEFAULT_RELEASE if len(build_version) > 20 else build_version
                )
                action_path = (
                    f"{ML_REPO}/flavors/{suggestion['flavor']}@{action_version}"
                )
                footer += (
                    f"- [{action_path}]({ML_DOC_URL}/flavors/{suggestion['flavor']}/)"
                    f" ({suggestion['linters_number']} linters)" + os.linesep
                )
        footer += os.linesep

    # Link to ox
    if (
        config.get(
            reporter_self.master.request_id, "REPORTERS_MARKDOWN_TYPE", "advanced"
        )
        == "simple"
    ):
        footer += (
            os.linesep
            + "MegaLinter is graciously provided by [OX Security]"
            + "(https://www.ox.security/?ref=megalinter)"
        )
    else:
        footer += os.linesep + OX_MARKDOWN_LINK

    if config.exists(
        reporter_self.master.request_id, "JOB_SUMMARY_ADDITIONAL_MARKDOWN"
    ):
        footer += os.linesep + config.get(
            reporter_self.master.request_id, "JOB_SUMMARY_ADDITIONAL_MARKDOWN", ""
        )

    return footer


def log_link(label, url):
    if url == "":
        return label
    else:
        return f"[{label}]({url})"


def get_linter_doc_url(linter):
    lang_lower = linter.descriptor_id.lower()
    linter_name_lower = linter.linter_name.lower().replace("-", "_")
    linter_doc_url = f"{ML_DOC_URL_DESCRIPTORS_ROOT}/{lang_lower}_{linter_name_lower}"
    return linter_doc_url


def log_section_start(section_key: str, section_title: str):
    if (
        utils.is_ci()
        and config.get(None, "CONSOLE_REPORTER_SECTIONS", "true") == "true"
    ):
        if utils.is_github_actions():
            return f"::group::{section_title} (expand for details)"
        elif utils.is_gitlab_ci():
            return (
                f"\x1b[0Ksection_start:`{time.time_ns()}`:{section_key}"  # noqa: W605
                + f"[collapsed=true]\r\x1b[0K{section_title} (expand for details)"  # noqa: W605
            )
        elif utils.is_azure_pipelines():
            return f"##[group]{section_title} (expand for details)"
    return section_title


def log_section_end(section_key):
    if (
        utils.is_ci()
        and config.get(None, "CONSOLE_REPORTER_SECTIONS", "true") == "true"
    ):
        if utils.is_github_actions():
            return "::endgroup::"
        elif utils.is_gitlab_ci():
            return f"\x1b[0Ksection_end:`{time.time_ns()}`:{section_key}\r\x1b[0K"  # noqa: W605
        elif utils.is_azure_pipelines():
            return "##[endgroup]"
    return ""


# Convert SARIF into human readable text
def convert_sarif_to_human(sarif_in, request_id) -> str:
    sarif_fmt_command = "sarif-fmt"
    try:
        process = subprocess.run(
            sarif_fmt_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            input=sarif_in + "\n",
            env=config.build_env(request_id),
        )
        return_code = process.returncode
        output = utils.clean_string(process.stdout)
    except Exception as e:
        return_code = 1
        output = sarif_in
        logging.warning("Unable to call sarif-fmt: " + str(e))
    logging.debug("Sarif to human result: " + str(return_code) + "\n" + output)
    return output


def build_reporter_start_message(reporter, redis_stream=False) -> dict:
    result = {
        "messageType": "megalinterStart",
        "megaLinterStatus": "created",
        "linters": [],
        "requestId": reporter.master.request_id,
    }
    linterResults = []
    for linter in reporter.master.linters:
        if linter.is_active is True:
            linterResults += [get_linter_infos(linter)]
    result["linters"] = linterResults
    return manage_redis_stream(result, redis_stream)


def build_reporter_external_result(reporter, redis_stream=False) -> dict:
    result = {
        "messageType": "megalinterComplete",
        "megaLinterStatus": "completed",
        "requestId": reporter.master.request_id,
    }
    return manage_redis_stream(result, redis_stream)


def build_linter_reporter_start_message(reporter, redis_stream=False) -> dict:
    result = {"messageType": "linterStart", "linterStatus": "started"}
    result = result | get_linter_infos(reporter.master)
    return manage_redis_stream(result, redis_stream)


def build_linter_reporter_external_result(reporter, redis_stream=False) -> dict:
    success_msg = "No errors were found in the linting process"
    error_not_blocking = "Errors were detected but are considered not blocking"
    error_msg = f"Found {reporter.master.total_number_errors} errors"
    status_message = (
        success_msg
        if reporter.master.status == "success" and reporter.master.return_code == 0
        else (
            error_not_blocking
            if reporter.master.status == "error" and reporter.master.return_code == 0
            else error_msg
        )
    )
    result = {
        "messageType": "linterComplete",
        "linterStatus": "success" if reporter.master.return_code == 0 else "error",
        "linterErrorNumber": reporter.master.total_number_errors,
        "linterStatusMessage": status_message,
        "linterElapsedTime": round(reporter.master.elapsed_time_s, 2),
    }
    if len(reporter.master.lint_command_log) > 0:
        result["linterCliCommand"] = reporter.master.lint_command_log
    result = result | get_linter_infos(reporter.master)
    if (
        reporter.master.sarif_output_file is not None
        and os.path.isfile(reporter.master.sarif_output_file)
        and os.path.getsize(reporter.master.sarif_output_file) > 0
    ):
        with open(
            reporter.master.sarif_output_file, "r", encoding="utf-8"
        ) as linter_sarif_file:
            result["outputSarif"] = json.load(linter_sarif_file)
    else:
        text_report_sub_folder = config.get(
            reporter.master.request_id, "TEXT_REPORTER_SUB_FOLDER", "linters_logs"
        )
        text_file_name = (
            f"{reporter.report_folder}{os.path.sep}"
            f"{text_report_sub_folder}{os.path.sep}"
            f"{reporter.master.status.upper()}-{reporter.master.name}.log"
        )
        if os.path.isfile(text_file_name):
            with open(text_file_name, "r", encoding="utf-8") as text_file:
                result["outputText"] = text_file.read()
                json_in_stdout = utils.find_json_in_stdout(result["outputText"], False)
                if json_in_stdout != "":
                    result["outputJson"] = json.loads(json_in_stdout)
        else:
            logging.warning(
                "External Message: Unable to find linter output, "
                "there is a probably an error within MegaLinter Worker"
            )
            result["outputText"] = (
                f"Internal error: unable to find linter output in {text_file_name}"
            )
    return manage_redis_stream(result, redis_stream)


def get_linter_infos(linter):
    lang_lower = linter.descriptor_id.lower()
    linter_name_lower = linter.linter_name.lower().replace("-", "_")
    linter_doc_url = f"{ML_DOC_URL_DESCRIPTORS_ROOT}/{lang_lower}_{linter_name_lower}"
    linter_infos = {
        "descriptorId": linter.descriptor_id,
        "linterId": linter.linter_name,
        "linterKey": linter.name,
        "linterVersion": linter.get_linter_version(),
        "linterCliLintMode": linter.cli_lint_mode,
        "requestId": linter.master.request_id,
        "docUrl": linter_doc_url,
        "isFormatter": linter.is_formatter,
        "isSBOM": linter.is_sbom,
    }
    if linter.cli_lint_mode in ["file", "list_of_files"]:
        linter_infos["filesNumber"] = len(linter.files)
    if linter.linter_icon_png_url is not None:
        linter_infos["iconPngUrl"] = linter.linter_icon_png_url
    return linter_infos


def manage_redis_stream(result, redis_stream):
    # Redis does not accept certain types of values: convert them
    if redis_stream is True:
        for result_key, result_val in result.items():
            if isinstance(result_val, dict):
                result[result_key] = json.dumps(result_val)
            elif isinstance(result_val, bool):
                result[result_key] = int(result_val)
    return result


def send_redis_message(reporter_self, message_data):
    try:
        redis = Redis(
            host=reporter_self.redis_host, port=reporter_self.redis_port, db=0
        )
        logging.debug("REDIS Connection: " + str(redis.info()))
        if reporter_self.redis_method == "STREAM":
            resp = redis.xadd(reporter_self.stream_key, message_data)
        else:
            resp = redis.publish(reporter_self.pubsub_channel, json.dumps(message_data))
        logging.info("REDIS RESP" + str(resp))
    except ConnectionError as e:
        if reporter_self.scope == "linter":
            logging.warning(
                f"[Redis Linter Reporter] Error posting message for {reporter_self.master.descriptor_id}"
                f" with {reporter_self.master.linter_name}: Connection error {str(e)}"
            )
        else:
            logging.warning(
                f"[Redis Reporter] Error posting message for MegaLinter: Connection error {str(e)}"
            )
    except Exception as e:
        if reporter_self.scope == "linter":
            logging.warning(
                f"[Redis Linter Reporter] Error posting message for {reporter_self.master.descriptor_id}"
                f" with {reporter_self.master.linter_name}: Error {str(e)}"
            )
            logging.warning(
                "[Redis Linter Reporter] Redis Message data: " + str(message_data)
            )
        else:
            logging.warning(
                f"[Redis Reporter] Error posting message for MegaLinter: Error {str(e)}"
            )
            logging.warning("[Redis Reporter] Redis Message data: " + str(message_data))
