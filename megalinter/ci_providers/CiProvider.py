#!/usr/bin/env python3
"""
Base class for CI/CD platform providers.

A CI provider knows what MegaLinter can not deduce from the repository alone:
which platform is running the build, how to reach its API, how to name the
current repository, branch and job, and which console commands fold log
sections. Every method must degrade gracefully, returning None or a neutral
value rather than raising: providers run while linters are being built, where
an exception aborts the whole MegaLinter run.

The base class doubles as the neutral provider returned when no platform is
recognized, so callers never have to handle a missing provider.
"""


class CiProvider:
    name = "ci"
    # Some platforms strip raw HTML from Pull Request comments
    markdown_supports_html_details = True

    def __init__(self, request_id, workspace=None):
        self.request_id = request_id
        self.workspace = workspace

    # Is this platform the one running the current build ?
    @staticmethod
    def is_current() -> bool:
        return False

    # Is the current build triggered by a Pull Request / Merge Request ?
    @staticmethod
    def is_pr_context() -> bool:
        return False

    # ----------------------------------------------------------------------
    # Pull Request commit range
    # ----------------------------------------------------------------------

    # Returns (source_sha, target_sha) of the current Pull Request, using None
    # for any value the platform does not expose
    def get_pr_commit_shas(self):
        return None, None

    # Platform specific guidance displayed when the commit range is unavailable
    def get_pr_commit_shas_hint(self) -> str:
        return "this CI platform is not auto-detected: define the SHAs manually"

    # ----------------------------------------------------------------------
    # Repository / branch / job context
    # ----------------------------------------------------------------------

    # Repository name, or None to let the caller fall back to the git remote
    def get_repo_name(self):
        return None

    # Branch name, or None to let the caller fall back to the git HEAD
    def get_branch_name(self):
        return None

    # URL of the running job/pipeline, or an empty string when unavailable
    def get_job_url(self) -> str:
        return ""

    # Keeps only the last segment of a slug or URL (owner/repo -> repo)
    @staticmethod
    def split_repo_name(repo_name):
        if repo_name is None:
            return None
        return repo_name.split("/")[-1]

    # ----------------------------------------------------------------------
    # Console log folding
    # ----------------------------------------------------------------------

    def log_section_start(self, section_key: str, section_title: str) -> str:
        return section_title

    def log_section_end(self, section_key: str) -> str:
        return ""

    # ----------------------------------------------------------------------
    # Job outputs
    # ----------------------------------------------------------------------

    # Publishes a key/value output consumable by the next steps of the job.
    # Returns True when the platform supports it
    def set_output(self, name: str, value) -> bool:
        return False

    # Publishes a markdown summary on the job page. Returns True when the
    # platform supports it
    def publish_job_summary(self, markdown: str) -> bool:
        return False
