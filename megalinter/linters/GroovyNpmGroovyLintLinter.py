#!/usr/bin/env python3
"""
Use npm-groovy-lint to lint Groovy,Jenkinsfile,Gradle and Nextflow files
https://github.com/nvuillam/npm-groovy-lint
"""

import os.path

from megalinter import Linter


class GroovyNpmGroovyLintLinter(Linter):

    # Build the CLI command to call to lint a file
    def build_lint_command(self, file=None):
        dir_name = os.path.dirname(file)
        file_name = os.path.basename(file)
        cmd = [self.cli_executable]
        # Add other lint cli arguments if defined
        cmd += self.cli_lint_extra_args
        # Add fix argument if defined
        if self.apply_fixes is True and self.cli_lint_fix_arg_name is not None:
            cmd += [self.cli_lint_fix_arg_name]
            self.try_fix = True
        # Add user-defined extra arguments if defined
        cmd += self.cli_lint_user_args
        cmd += ["--path ", dir_name, "--files ", f"**/{file_name}"]
        if self.config_file is not None:
            cmd += [self.cli_config_arg_name, self.config_file]
        return cmd
