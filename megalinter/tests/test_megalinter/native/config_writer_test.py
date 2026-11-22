import os
import tempfile
import unittest

import yaml

from megalinter.native.config_writer import (
    find_config_file,
    replace_native_linters,
    write_native_linters,
)
from megalinter.native.context import NativeError

KEYS = ["PYTHON_BLACK", "MARKDOWN_MARKDOWNLINT"]


class ConfigWriterTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.file = os.path.join(self.folder.name, ".mega-linter.yml")

    def write(self, content):
        with open(self.file, "w", encoding="utf-8", newline="") as file:
            file.write(content)

    def read(self):
        with open(self.file, "r", encoding="utf-8", newline="") as file:
            return file.read()

    def test_appends_to_a_configuration_without_the_key(self):
        self.write("# My config\nAPPLY_FIXES: all\n")
        write_native_linters(self.file, KEYS)
        content = self.read()
        self.assertTrue(content.startswith("# My config\nAPPLY_FIXES: all\n\n#"))
        self.assertEqual(yaml.safe_load(content)["NATIVE_LINTERS"], KEYS)
        self.assertEqual(yaml.safe_load(content)["APPLY_FIXES"], "all")
        self.assertTrue(content.endswith("\n"))

    def test_replaces_a_block_list_and_keeps_the_rest(self):
        self.write(
            "ENABLE:\n  - PYTHON\nNATIVE_LINTERS:\n  - SPELL_CSPELL\n  # old\n"
            "  - YAML_YAMLLINT\n\nDISABLE:\n  - COPYPASTE\n"
        )
        write_native_linters(self.file, KEYS)
        parsed = yaml.safe_load(self.read())
        self.assertEqual(parsed["NATIVE_LINTERS"], KEYS)
        self.assertEqual(parsed["ENABLE"], ["PYTHON"])
        self.assertEqual(parsed["DISABLE"], ["COPYPASTE"])
        self.assertNotIn("SPELL_CSPELL", self.read())

    def test_replaces_a_list_that_is_not_indented(self):
        self.write("NATIVE_LINTERS:\n- SPELL_CSPELL\nDISABLE:\n- COPYPASTE\n")
        write_native_linters(self.file, KEYS)
        parsed = yaml.safe_load(self.read())
        self.assertEqual(parsed["NATIVE_LINTERS"], KEYS)
        self.assertEqual(parsed["DISABLE"], ["COPYPASTE"])

    def test_replaces_a_flow_list_and_a_scalar(self):
        self.write("NATIVE_LINTERS: [SPELL_CSPELL]  # old\nAPPLY_FIXES: all\n")
        write_native_linters(self.file, KEYS)
        self.assertEqual(yaml.safe_load(self.read())["NATIVE_LINTERS"], KEYS)
        self.write("NATIVE_LINTERS: all\n")
        write_native_linters(self.file, KEYS)
        self.assertEqual(yaml.safe_load(self.read())["NATIVE_LINTERS"], KEYS)

    def test_keeps_windows_line_endings(self):
        self.write("APPLY_FIXES: all\r\nNATIVE_LINTERS:\r\n  - SPELL_CSPELL\r\n")
        write_native_linters(self.file, KEYS)
        content = self.read()
        self.assertNotIn("\n", content.replace("\r\n", ""))
        self.assertEqual(yaml.safe_load(content)["NATIVE_LINTERS"], KEYS)

    def test_creates_a_missing_file(self):
        self.assertFalse(os.path.exists(self.file))
        write_native_linters(self.file, KEYS)
        self.assertEqual(yaml.safe_load(self.read()), {"NATIVE_LINTERS": KEYS})

    def test_invalid_yaml_is_refused_and_left_untouched(self):
        self.write("APPLY_FIXES: [unclosed\n")
        with self.assertRaises(NativeError):
            write_native_linters(self.file, KEYS)
        self.assertEqual(self.read(), "APPLY_FIXES: [unclosed\n")

    def test_unsafe_edit_is_rolled_back(self):
        # Removing the anchor of the entry breaks the alias that uses it
        original = "NATIVE_LINTERS: &linters [SPELL_CSPELL]\nOTHER: *linters\n"
        self.write(original)
        with self.assertRaises(NativeError) as error:
            write_native_linters(self.file, KEYS)
        self.assertIn("  - PYTHON_BLACK", str(error.exception))
        self.assertEqual(self.read(), original)

    def test_replace_keeps_a_single_trailing_newline(self):
        updated = replace_native_linters("A: 1\nNATIVE_LINTERS:\n  - X\n", KEYS)
        self.assertEqual(updated.count("NATIVE_LINTERS"), 1)
        self.assertTrue(updated.endswith("MARKDOWN_MARKDOWNLINT\n"))

    def test_finds_the_configuration_file(self):
        self.assertEqual(find_config_file(self.folder.name), self.file)
        dot_config = os.path.join(self.folder.name, ".config")
        os.makedirs(dot_config)
        other = os.path.join(dot_config, "megalinter.yml")
        with open(other, "w", encoding="utf-8") as file:
            file.write("A: 1\n")
        self.assertEqual(
            os.path.normpath(find_config_file(self.folder.name)),
            os.path.normpath(other),
        )
        self.write("B: 2\n")
        self.assertEqual(find_config_file(self.folder.name), self.file)


if __name__ == "__main__":
    unittest.main()
