#!/usr/bin/env python3
"""
Unit tests for utils class

"""
import re
import unittest

from megalinter import utils


class utilsTest(unittest.TestCase):
    def test_file_contains_true(self):
        repo_home = utils.REPO_HOME_DEFAULT
        regex_list = ["#!/usr/bin/env perl", "#!/usr/bin/perl"]
        regex_object = re.compile("|".join(regex_list), flags=re.MULTILINE)
        file = f"{repo_home}/.automation/test/perl/perl_good_2"
        file_contains_res = utils.file_contains(file, regex_object)
        self.assertTrue(file_contains_res, f"{file} matching with {str(regex_list)}")

    def test_file_contains_false(self):
        repo_home = utils.REPO_HOME_DEFAULT
        regex_list = ["#!/usr/bin/env perl", "#!/usr/bin/perl"]
        regex_object = re.compile("|".join(regex_list), flags=re.MULTILINE)
        file = f"{repo_home}/.dockerignore"
        file_contains_res = utils.file_contains(file, regex_object)
        self.assertFalse(file_contains_res, f"{file} matching with {str(regex_list)}")


    def test_file_is_generated_true(self):
        repo_home = utils.REPO_HOME_DEFAULT
        file = f"{repo_home}/docs/index.md"
        file_contains_res = utils.file_is_generated(file)
        self.assertTrue(file_contains_res, f"{file} should be identified as generated")


    def test_file_is_generated_false(self):
        repo_home = utils.REPO_HOME_DEFAULT
        file = f"{repo_home}/Dockerfile"
        file_contains_res = utils.file_is_generated(file)
        self.assertFalse(file_contains_res, f"{file} should not be identified as generated")


    def test_file_is_generated_false_2(self):
        repo_home = utils.REPO_HOME_DEFAULT
        file = f"{repo_home}/LICENSE"
        file_contains_res = utils.file_is_generated(file)
        self.assertFalse(file_contains_res, f"{file} should not be identified as generated")
