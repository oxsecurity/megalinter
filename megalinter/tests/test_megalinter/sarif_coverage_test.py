#!/usr/bin/env python3
"""
Every active linter must be able to output SARIF (only a disabled linter is exempt)
"""

import unittest

from megalinter import config, linter_factory


class SarifCoverageTest(unittest.TestCase):
    def test_every_active_linter_can_output_sarif(self):
        config.init_config("build")
        linters = linter_factory.list_linters_without_sarif({"request_id": "build"})
        self.assertEqual(
            [linter.name for linter in linters],
            [],
            "These linters can not output SARIF: declare can_output_sarif: true "
            "with cli_sarif_args, sarif_text_regex, sarif_unified_diff or "
            "sarif_whole_output in their descriptor",
        )


if __name__ == "__main__":
    unittest.main()
