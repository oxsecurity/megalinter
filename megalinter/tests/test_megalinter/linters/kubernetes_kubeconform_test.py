# !/usr/bin/env python3
"""
Unit tests for KUBERNETES linter kubeconform
This class has been automatically @generated by .automation/build.py, please don't update it manually
"""

from unittest import TestCase

from megalinter.tests.test_megalinter.LinterTestRoot import LinterTestRoot


class kubernetes_kubeconform_test(TestCase, LinterTestRoot):
    descriptor_id = "KUBERNETES"
    linter_name = "kubeconform"