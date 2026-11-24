#!/usr/bin/env python3
"""
Unit tests for the tips and skipped linters kept by Megalinter for the JSON report

"""

import os
import unittest
import uuid

from megalinter import config, utilstest
from megalinter.removed_linters import REMOVED_LINTERS


class mega_linter_tips_test(unittest.TestCase):
    def before_start(self):
        config.delete()
        self.request_id = str(uuid.uuid1())
        utilstest.linter_test_setup(
            {
                "request_id": self.request_id,
                "sub_lint_root": f"{os.path.sep}.automation{os.path.sep}test{os.path.sep}sample_project",
            }
        )

    def test_removed_linter_reference_is_a_tip(self):
        # The references are checked while Megalinter initializes: the tips must exist by then
        self.before_start()
        removed_key = sorted(REMOVED_LINTERS)[0]
        mega_linter, _ = utilstest.call_mega_linter(
            {
                "MEGALINTER_PRERUN": "true",
                "ENABLE_LINTERS": "JAVASCRIPT_ES",
                "DISABLE_LINTERS": removed_key,
                "MULTI_STATUS": "false",
                "request_id": self.request_id,
            }
        )
        tips = [tip for tip in mega_linter.tips if tip["category"] == "deprecation"]
        self.assertTrue(
            any(removed_key in tip["message"] for tip in tips),
            f"{removed_key} should have a deprecation tip: {mega_linter.tips}",
        )

    def test_disabled_linters_are_skipped_with_their_reason(self):
        self.before_start()
        mega_linter, _ = utilstest.call_mega_linter(
            {
                "MEGALINTER_PRERUN": "true",
                "ENABLE_LINTERS": "JAVASCRIPT_ES",
                "MULTI_STATUS": "false",
                "request_id": self.request_id,
            }
        )
        self.assertIsInstance(mega_linter.skipped_linters_details, list)
        self.assertIsInstance(mega_linter.tips, list)
        for skipped in mega_linter.skipped_linters_details:
            self.assertEqual(sorted(skipped), ["key", "reason"])


if __name__ == "__main__":
    unittest.main()
