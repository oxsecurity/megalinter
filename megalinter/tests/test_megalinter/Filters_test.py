#!/usr/bin/env python3
"""
Unit tests for utils class

"""
import unittest

from megalinter import utils


class utilsTest(unittest.TestCase):
    def test_file_contains_true(self):
        repo_home = utils.REPO_HOME_DEFAULT
        regex_list = ["#!/usr/bin/env perl", "#!/usr/bin/perl"]
        file = f"{repo_home}/.automation/test/perl/perl_good_2"
        file_contains_res = utils.file_contains(file, regex_list)
        self.assertTrue(file_contains_res, f"{file} matching with {str(regex_list)}")

    def test_file_contains_false(self):
        repo_home = utils.REPO_HOME_DEFAULT
        regex_list = ["#!/usr/bin/env perl", "#!/usr/bin/perl"]
        file = f"{repo_home}/.dockerignore"
        file_contains_res = utils.file_contains(file, regex_list)
        self.assertFalse(file_contains_res, f"{file} matching with {str(regex_list)}")
