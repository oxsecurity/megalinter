#!/usr/bin/env python3
"""
Use secretlint to find secrets in sources
https://github.com/secretlint/secretlint
"""

import logging
import os
import shutil
import tempfile

from megalinter import Linter, config, utils

# secretlint's built-in DEFAULT_IGNORE_PATTERNS contains "**/.secretlintignore*",
# so a file with this name is never scanned by secretlint itself
MEGALINTER_IGNORE_FILE_NAME = ".secretlintignore-megalinter"


class SecretLintLinter(Linter):
    def __init__(self, params=None, linter_config=None):
        self.megalinter_ignore_file = None
        self.ignore_tmp_folder = None
        super().__init__(params, linter_config)

    # The only run() override among the linters, because Linter.run() offers no
    # post-run hook to extend: it deletes remote_config_file_to_delete and
    # remote_ignore_file_to_delete inline. The alternatives do not work either:
    # process_linter() is called once per file in file lint mode, so cleaning up
    # there would strip the ignore patterns from every file after the first, and
    # before_lint_files() runs before the files rather than after. Wrapping run()
    # is the only point that runs exactly once, after every file, even when
    # process_linter raises.
    def run(
        self,
        run_commands_before_linters=None,
        run_commands_after_linters=None,
        skip_console_reporter=False,
    ):
        try:
            return super().run(
                run_commands_before_linters,
                run_commands_after_linters,
                skip_console_reporter,
            )
        finally:
            self.remove_ignore_tmp_folder()

    # Removes the temporary folder created by build_megalinter_ignore_file when
    # REPORT_OUTPUT_FOLDER is disabled.
    def remove_ignore_tmp_folder(self):
        if self.ignore_tmp_folder is None:
            return
        shutil.rmtree(self.ignore_tmp_folder, ignore_errors=True)
        self.ignore_tmp_folder = None

    def before_lint_files(self):
        self.megalinter_ignore_file = self.build_megalinter_ignore_file()

    # Generates the single ignore file secretlint will use, merging the user's
    # patterns with MegaLinter's report folder. Nothing else is added: narrowing a
    # secrets scanner further would hide credentials baked into build artifacts
    # (.terraform/modules/modules.json can hold basic-auth module URLs). It lives in
    # the report folder, not the workspace, so MegaLinter never creates or removes
    # files in the sources being scanned (#3979); with reports disabled it goes to a
    # temp folder instead, so a .secretlintignore in LINTER_RULES_PATH still applies.
    # secretlint resolves the value as path.join(cwd, value), so it must be relative.
    # This whole approach depends on secretlint resolving the patterns *inside* the
    # file against the cwd as well, which holds from v13 (the ripgrep-based walker)
    # and is why the descriptor pins NPM_SECRETLINT_VERSION to 13.x. Measured on
    # 11.3.1, patterns resolved against the ignore file's own directory instead, so
    # every line written here -- the user's patterns and the report folder exclusion
    # alike -- matched nothing, on a run that still reported success. Re-check this
    # before lowering the pin: the failure mode is a secrets scanner quietly
    # scanning a different set of files, not an error.
    def build_megalinter_ignore_file(self):
        reports_disabled = not utils.can_write_report_files(self.master)
        if reports_disabled:
            self.ignore_tmp_folder = tempfile.mkdtemp(prefix="megalinter-secretlint-")
            target_folder = self.ignore_tmp_folder
        else:
            target_folder = self.report_folder
        ignore_file_path = os.path.join(target_folder, MEGALINTER_IGNORE_FILE_NAME)
        try:
            relative_path = os.path.relpath(ignore_file_path, self.workspace)
            report_folder_pattern = (
                None
                if reports_disabled
                else os.path.relpath(self.report_folder, self.workspace)
            )
        except ValueError as e:
            logging.warning(
                f"[{self.linter_name}] Unable to build a workspace-relative path for "
                f"{ignore_file_path} ({str(e)}): MegaLinter reports will not be excluded"
            )
            return None
        lines = []
        source_ignore_file = self.get_source_ignore_file()
        if source_ignore_file is not None:
            # Only warn when reports being disabled actually put something at risk:
            # a run with no ignore file anywhere never had patterns to preserve
            if reports_disabled:
                logging.warning(
                    f"[{self.linter_name}] REPORT_OUTPUT_FOLDER is disabled: the "
                    f"patterns from {source_ignore_file} are written to a temporary "
                    "folder instead of the report folder"
                )
            # Nothing between here and megalinter/run.py catches exceptions, so an
            # unreadable ignore file must degrade rather than kill every other linter
            try:
                with open(source_ignore_file, "r", encoding="utf-8") as ignore_file:
                    lines += [
                        f"# Copied by MegaLinter from {source_ignore_file}",
                        ignore_file.read().rstrip("\n"),
                    ]
            except (OSError, UnicodeDecodeError) as e:
                logging.warning(
                    f"[{self.linter_name}] Unable to read {source_ignore_file} "
                    f"({str(e)}): its ignore patterns will not be applied"
                )
        # Appended last on purpose: gitignore semantics are last match wins, so this
        # stays authoritative over any user negation pattern. A report folder outside
        # the workspace yields a ".." relative path, which is not a valid gitignore
        # pattern, and such a folder is never scanned anyway.
        if report_folder_pattern is not None and not report_folder_pattern.startswith(
            ".."
        ):
            lines += ["# Added by MegaLinter: never lint MegaLinter's own output"]
            lines += [report_folder_pattern.replace(os.path.sep, "/")]
        try:
            os.makedirs(target_folder, exist_ok=True)
            with open(ignore_file_path, "w", encoding="utf-8") as ignore_file:
                ignore_file.write("\n".join(lines) + "\n")
        except OSError as e:
            logging.warning(
                f"[{self.linter_name}] Unable to write {ignore_file_path} "
                f"({e.strerror}): MegaLinter reports will not be excluded"
            )
            return None
        return relative_path.replace(os.path.sep, "/")

    # secretlint reads a single ignore file and keeps only the last --secretlintignore
    # value, so a user file that is not merged would stop being applied entirely.
    def get_source_ignore_file(self):
        user_ignore_file = self.get_user_ignore_file_arg()
        if user_ignore_file is not None:
            if not os.path.isabs(user_ignore_file):
                user_ignore_file = os.path.join(self.workspace, user_ignore_file)
            if os.path.isfile(user_ignore_file):
                return user_ignore_file
            # Falling back to .gitignore here would let a typo exclude exactly the
            # files a secrets scanner exists to find, with the run still green
            logging.warning(
                f"[{self.linter_name}] --secretlintignore {user_ignore_file} is not "
                "a file: its ignore patterns will not be applied, and no fallback "
                "ignore file is used in their place"
            )
            return None
        if self.ignore_file is not None and os.path.isfile(self.ignore_file):
            return self.ignore_file
        git_ignore_file = os.path.join(self.workspace, ".gitignore")
        if os.path.isfile(git_ignore_file):
            return git_ignore_file
        return None

    def get_user_ignore_file_arg(self):
        for index, arg in enumerate(self.cli_lint_user_args):
            if arg == "--secretlintignore" and index + 1 < len(self.cli_lint_user_args):
                return self.cli_lint_user_args[index + 1]
            if arg.startswith("--secretlintignore="):
                return arg.split("=", 1)[1]
        return None

    def get_ignore_arguments(self, cmd):
        if self.megalinter_ignore_file is not None:
            return ["--secretlintignore", self.megalinter_ignore_file]
        # Only reached when build_megalinter_ignore_file failed to build a relative
        # path or to write the file. The absolute path the base class builds never
        # resolves, so pass the base name: the walker then finds it at the workspace
        # root and applies its patterns from there.
        ignore_args = super().get_ignore_arguments(cmd)
        if len(ignore_args) >= 2 and ignore_args[0] == "--secretlintignore":
            ignore_args = [
                "--secretlintignore",
                os.path.basename(ignore_args[1]),
                *ignore_args[2:],
            ]
        # Use .gitignore as .secretlintignore
        # only if --secretlintignore is not defined and .secretlintignore not found
        if (
            len(ignore_args) == 0
            and "--secretlintignore" not in self.cli_lint_user_args
            and os.path.isfile(os.path.join(self.workspace, ".gitignore"))
            and not os.path.isfile(os.path.join(self.workspace, ".secretlintignore"))
        ):
            ignore_args = ["--secretlintignore", ".gitignore"]
        return ignore_args

    def pre_test(self, test_name):
        if test_name.endswith(("file_lint_mode", "list_of_files_lint_mode")):
            config.set_value(
                self.request_id, "REPOSITORY_SECRETLINT_FILE_EXTENSIONS", [".ini"]
            )
