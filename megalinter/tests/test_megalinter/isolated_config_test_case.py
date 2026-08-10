#!/usr/bin/env python3

import os
import unittest
import uuid
from unittest.mock import patch

from megalinter import config


# init_config(request_id, workspace=None) copies os.environ wholesale into the
# config when no workspace is given, so ambient env vars would otherwise leak into
# tests that read configuration (see utils_test.py for the same fix applied inline).
class IsolatedConfigTestCase(unittest.TestCase):
    def setUp(self):
        self.request_id = str(uuid.uuid1())
        with patch.dict(os.environ, {}, clear=True):
            config.init_config(self.request_id)

    def tearDown(self):
        config.delete(self.request_id)
