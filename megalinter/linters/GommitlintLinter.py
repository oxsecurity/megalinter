#!/usr/bin/env python3
"""
Use gommitlint to validate Git commit messages
"""

import logging
import os
import shutil
import subprocess
import tempfile
import uuid

from megalinter import Linter, config


class GommitlintLinter(Linter):
    # Build the lint command, passing explicit base branch if configured
    def build_lint_command(self, file=None):
        cmd = super().build_lint_command(file)

        # Explicit base branch override (gommitlint auto-detects on CI)
        base_branches = [
            branch.strip()
            for branch in config.get_list_args(
                self.request_id, "REPOSITORY_GOMMITLINT_BASE_BRANCH", []
            )
            if str(branch).strip()
        ]
        if len(base_branches) == 1 and base_branches[0].lower() == "none":
            # Keep the override in the subprocess environment MegaLinter reuses.
            subprocess_env = getattr(self, "_cached_subprocess_env", None)
            if subprocess_env is None:
                subprocess_env = {
                    **config.build_env(
                        self.request_id, True, self.unsecured_env_variables
                    ),
                    "FORCE_COLOR": "0",
                }
                self._cached_subprocess_env = subprocess_env
            subprocess_env["GOMMITLINT_NO_CI_DETECT"] = "1"
        elif base_branches:
            cmd += ["--base-branch", ",".join(base_branches)]

        return cmd

    # Set up a temporary git repo for tests since gommitlint validates git history
    def pre_test(self, test_name):
        if "success" in test_name:
            self.setup_test_git_repo(good=True)
        elif "failure" in test_name:
            self.setup_test_git_repo(good=False)

    # Create a temporary git repo with test commits for validation
    def setup_test_git_repo(self, good=True):
        test_git_dir = tempfile.mkdtemp(prefix="gommitlint_test_")
        config.set_value(self.request_id, "GOMMITLINT_TEST_GIT_DIR", test_git_dir)

        env = {
            **os.environ,
            "GIT_AUTHOR_NAME": "Test Author",
            "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "Test Author",
            "GIT_COMMITTER_EMAIL": "test@example.com",
            "GOMMITLINT_NO_CI_DETECT": "1",
        }
        run_opts = {"cwd": test_git_dir, "env": env, "capture_output": True}

        subprocess.run(["git", "init"], **run_opts, check=True)
        subprocess.run(["git", "checkout", "-b", "main"], **run_opts, check=True)

        if good:
            # Create well-formed conventional commits with sign-off
            signoff = "\n\nSigned-off-by: Test Author <test@example.com>"
            self.make_test_commit(
                test_git_dir, "feat: add initial feature" + signoff, env
            )
            self.make_test_commit(
                test_git_dir, "fix: correct validation logic" + signoff, env
            )
        else:
            # Create badly-formed commits that violate rules
            self.make_test_commit(
                test_git_dir, "WIP badly formed commit message ending.", env
            )

    # Create a dummy file and commit with the given message
    def make_test_commit(self, repo_dir, message, env):
        dummy = os.path.join(repo_dir, f"{uuid.uuid4().hex}.txt")
        with open(dummy, "w", encoding="utf-8") as f:
            f.write("test content\n")
        run_opts = {"cwd": repo_dir, "env": env, "capture_output": True}
        subprocess.run(["git", "add", "."], **run_opts, check=True)
        subprocess.run(["git", "commit", "-m", message], **run_opts, check=True)

    # Clean up the temporary git repo
    def post_test(self, test_name):
        try:
            test_git_dir = config.get(self.request_id, "GOMMITLINT_TEST_GIT_DIR", "")
            if test_git_dir and os.path.isdir(test_git_dir):
                shutil.rmtree(test_git_dir, ignore_errors=True)
        except Exception:
            logging.debug("[gommitlint] Could not clean up test git repo")

    # Run gommitlint in the temporary git repo during tests
    def execute_lint_command(self, command):
        test_git_dir = config.get(self.request_id, "GOMMITLINT_TEST_GIT_DIR", "")
        if test_git_dir and os.path.isdir(test_git_dir):
            # Copy the config file into the test repo with safe permissions
            config_file = os.path.join(self.workspace, ".gommitlint.yaml")
            if os.path.isfile(config_file):
                dest = os.path.join(test_git_dir, ".gommitlint.yaml")
                shutil.copy2(config_file, dest)
                os.chmod(dest, 0o644)
            # Strip --gommitconfig arg so gommitlint auto-discovers the
            # config in the test repo (avoids permission issues on the
            # original workspace file)
            if isinstance(command, list):
                cmd = list(command)
                if "--gommitconfig" in cmd:
                    idx = cmd.index("--gommitconfig")
                    del cmd[idx : idx + 2]
                command = cmd
            original_workspace = self.workspace
            self.workspace = test_git_dir
            try:
                return super().execute_lint_command(command)
            finally:
                self.workspace = original_workspace
        return super().execute_lint_command(command)
