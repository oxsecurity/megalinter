import os
import shutil
import tempfile
import unittest
from unittest import mock

from megalinter import cli
from megalinter.native.installer import NativeInstaller


class NativePrerunTest(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.mkdtemp()
        os.chmod(self.home, 0o700)
        self.workspace = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.home, True)
        self.addCleanup(shutil.rmtree, self.workspace, True)
        with open(os.path.join(self.workspace, "a.py"), "w", encoding="utf-8") as file:
            file.write("x = 1\n")
        with open(
            os.path.join(self.workspace, "README.md"), "w", encoding="utf-8"
        ) as file:
            file.write("# Title\n")
        environment = mock.patch.dict(
            os.environ,
            {
                "MEGALINTER_NATIVE": "true",
                "MEGALINTER_HOME": self.home,
                "DEFAULT_WORKSPACE": self.workspace,
                "ENABLE_LINTERS": "PYTHON_BLACK,PYTHON_PYLINT,MARKDOWN_MARKDOWNLINT",
            },
        )
        environment.start()
        self.addCleanup(environment.stop)
        cli.config.refresh_env_snapshot()
        self.addCleanup(cli.config.refresh_env_snapshot)

    def test_prerun_suggests_the_native_linters_and_installs_nothing(self):
        with mock.patch.object(NativeInstaller, "install") as install:
            mega_linter = cli.run_native_prerun()
        install.assert_not_called()
        self.assertNotIn("MEGALINTER_PRERUN", os.environ)
        suggestions = {
            item["variable"]: item for item in mega_linter.prerun_report["suggestions"]
        }
        self.assertNotIn("MEGALINTER_FLAVOR", suggestions)
        native = suggestions["NATIVE_LINTERS"]
        self.assertIn("PYTHON_BLACK", native["values"])
        self.assertIn("MARKDOWN_MARKDOWNLINT", native["values"])
        self.assertNotIn("PYTHON_PYLINT", native["values"])
        rows = {row["key"]: row for row in native["details"]}
        self.assertFalse(rows["PYTHON_PYLINT"]["recommended"])
        self.assertEqual(os.listdir(self.home), [])


if __name__ == "__main__":
    unittest.main()
