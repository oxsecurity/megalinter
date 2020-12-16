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
