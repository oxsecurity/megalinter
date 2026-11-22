import subprocess
import sys
import unittest

# Libraries used only by some reporters, CI providers, remote configurations or LLM
# and API providers: imported inside the functions using them, so that loading
# MegaLinter does not load them
LAZY_LIBRARIES = [
    "atlassian",
    "github",
    "gitlab",
    "jsonpickle",
    "pytablewriter",
    "redis",
    "requests",
]

IMPORT_EVERYTHING = """
import importlib, json, os, sys
import megalinter
from megalinter import MegaLinter, config, linter_factory, utils_reporter
reporters_dir = os.path.join(os.path.dirname(megalinter.__file__), "reporters")
for name in sorted(os.listdir(reporters_dir)):
    if name.endswith("Reporter.py"):
        importlib.import_module("megalinter.reporters." + name[:-3])
print(json.dumps(sorted(set(m.split(".")[0] for m in sys.modules))))
"""


class LazyImportsTest(unittest.TestCase):
    def test_heavy_libraries_are_not_loaded_at_startup(self):
        output = subprocess.run(
            [sys.executable, "-c", IMPORT_EVERYTHING],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        loaded = [library for library in LAZY_LIBRARIES if f'"{library}"' in output]
        self.assertEqual(loaded, [])


if __name__ == "__main__":
    unittest.main()
