import os
import shutil
import tempfile
import unittest

from megalinter import config


# Native mode configuration with a temporary MEGALINTER_HOME and workspace
class NativeHomeTestCase(unittest.TestCase):
    request_id = "test-native-home"

    def setUp(self):
        self.home = tempfile.mkdtemp()
        os.chmod(self.home, 0o700)
        self.workspace = tempfile.mkdtemp()
        config.set_config(
            self.request_id,
            {"MEGALINTER_NATIVE": "true", "MEGALINTER_HOME": self.home},
        )
        self.addCleanup(config.delete, self.request_id)
        self.addCleanup(shutil.rmtree, self.home, True)
        self.addCleanup(shutil.rmtree, self.workspace, True)
