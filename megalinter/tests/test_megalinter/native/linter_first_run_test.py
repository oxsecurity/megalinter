import os
import tempfile
import unittest
from types import SimpleNamespace

from megalinter.Linter import Linter


class FirstRunMarkerTest(unittest.TestCase):
    def marker(self, toolchain):
        return Linter.native_first_run_marker(
            SimpleNamespace(native_toolchain=toolchain)
        )

    def test_marker_is_in_the_install_folder_of_an_installed_linter(self):
        with tempfile.TemporaryDirectory() as install_dir:
            toolchain = SimpleNamespace(install_dir=install_dir, host_tool=False)
            self.assertEqual(
                self.marker(toolchain),
                os.path.join(install_dir, ".megalinter-first-run"),
            )

    def test_no_marker_in_docker_or_for_a_tool_of_the_host(self):
        self.assertIsNone(self.marker(None))
        self.assertIsNone(
            self.marker(SimpleNamespace(install_dir="/x", host_tool=True))
        )
        self.assertIsNone(
            self.marker(SimpleNamespace(install_dir=None, host_tool=False))
        )


if __name__ == "__main__":
    unittest.main()
