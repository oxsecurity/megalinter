import os
import unittest
from unittest.mock import patch

from megalinter.Linter import Linter
from megalinter.linters.EslintLinter import EslintLinter
from megalinter.tests.test_megalinter.native.native_home import NativeHomeTestCase

CACHE_ARGUMENTS = ["--cache", "--cache-location", "/home/x/cache"]


class EslintNativeCacheTest(NativeHomeTestCase):
    request_id = "test-native-eslint-cache"

    def linter(self, config_content=None):
        linter = EslintLinter.__new__(EslintLinter)
        linter.request_id = self.request_id
        linter.name = "JAVASCRIPT_ES"
        linter.workspace = self.workspace
        linter.config_file = None
        if config_content is not None:
            with open(
                os.path.join(self.workspace, "eslint.config.js"), "w", encoding="utf-8"
            ) as file:
                file.write(config_content)
        return linter

    def cache_arguments(self, linter):
        with patch.object(
            Linter, "get_native_cache_arguments", return_value=CACHE_ARGUMENTS
        ):
            return linter.get_native_cache_arguments()

    def test_cache_used_without_type_aware_rules(self):
        linter = self.linter("export default [{ rules: { semi: 'error' } }];\n")
        self.assertEqual(self.cache_arguments(linter), CACHE_ARGUMENTS)

    def test_cache_used_without_configuration(self):
        self.assertEqual(self.cache_arguments(self.linter()), CACHE_ARGUMENTS)

    def test_no_cache_with_type_aware_rules(self):
        for content in (
            "export default [{ languageOptions: { parserOptions: { projectService: true } } }];",
            "export default [{ languageOptions: { parserOptions: { project: './tsconfig.json' } } }];",
            "export default typescriptEslint.config(typescriptEslint.configs.recommendedTypeChecked);",
        ):
            with self.subTest(content=content):
                self.assertEqual(self.cache_arguments(self.linter(content)), [])


if __name__ == "__main__":
    unittest.main()
