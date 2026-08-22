#!/usr/bin/env python3
"""
Base class for CI/CD platform providers.

A CI provider knows how to extract from its platform the information MegaLinter
can not deduce from the repository alone, like the commit range of the current
Pull Request. Every method must degrade gracefully: providers run while linters
are being built, where an exception aborts the whole MegaLinter run.
"""


class CiProvider:
    name = "ci"

    def __init__(self, request_id, workspace):
        self.request_id = request_id
        self.workspace = workspace

    @staticmethod
    def is_pr_context() -> bool:
        return False

    # Returns (source_sha, target_sha) of the current Pull Request, using None
    # for any value the platform does not expose
    def get_pr_commit_shas(self):
        return None, None

    # Platform specific guidance displayed when the commit range is unavailable
    def get_pr_commit_shas_hint(self) -> str:
        return "this CI platform is not auto-detected: define the SHAs manually"
