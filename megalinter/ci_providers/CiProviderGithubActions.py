#!/usr/bin/env python3
"""
GitHub Actions CI provider
"""

import json
import logging

from megalinter import config, utils
from megalinter.ci_providers.CiProvider import CiProvider


class CiProviderGithubActions(CiProvider):
    name = "GitHub Actions"

    @staticmethod
    def is_pr_context() -> bool:
        return utils.is_github_pr()

    # The event payload is read from a path provided by the runner: a missing,
    # unreadable or non Pull Request payload must not abort the run
    def get_pr_commit_shas(self):
        gh_event_path = config.get(self.request_id, "GITHUB_EVENT_PATH")
        if gh_event_path is None:
            return None, None
        try:
            with open(gh_event_path, encoding="utf-8") as gh_event_file:
                gh_event = json.load(gh_event_file)
            return (
                gh_event["pull_request"]["head"]["sha"],
                gh_event["pull_request"]["base"]["sha"],
            )
        except (OSError, ValueError, KeyError, TypeError):
            logging.warning(
                f"[{self.name}] Unable to read Pull Request commit SHAs from "
                f"event payload {gh_event_path}"
            )
            return None, None

    def get_pr_commit_shas_hint(self) -> str:
        return "check out the repository with `fetch-depth: 0`"
