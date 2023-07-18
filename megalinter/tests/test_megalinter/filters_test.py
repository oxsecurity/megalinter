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
        self.assertFalse(
            file_contains_res, f"{file} should not be identified as generated"
        )

    def test_file_is_generated_false_2(self):
        repo_home = utils.REPO_HOME_DEFAULT
        file = f"{repo_home}/LICENSE"
        file_contains_res = utils.file_is_generated(file)
        self.assertFalse(
            file_contains_res, f"{file} should not be identified as generated"
        )

    def test_filter_files_with_ignored_files(self):
        all_files = [
            "src/foo.ext",
            "README.md",
            "target/foo.ext",
        ]
        for ignored_files, expected in [
            ([], all_files),
            (["hello"], all_files),
            (["target/foo.ext2"], all_files),
            (
                ["target/foo.ext"],
                ["src/foo.ext", "README.md"],
            ),
            (["target/**"], ["src/foo.ext", "README.md"]),
            (["foo.ext"], all_files),
        ]:
            filtered_files = utils.filter_files(
                all_files=all_files,
                filter_regex_include=None,
                filter_regex_exclude=[None],
                file_names_regex=[],
                file_extensions=["", ".md", ".ext"],
                ignored_files=ignored_files,
                ignore_generated_files=False,
            )
            self.assertListEqual(
                sorted(filtered_files), sorted(expected), f"check {ignored_files}"
            )

    def test_filter_files_with_file_extensions(self):
        all_files = [
            "src/foo.ext",
            "README.md",
            "LICENSE",
            "target/foo.ext",
        ]

        for file_extensions, expected in [
            ([], []),
            ([".md"], ["README.md"]),
            ([""], ["LICENSE"]),
            (["", ".md"], ["LICENSE", "README.md"]),
        ]:
            filtered_files = utils.filter_files(
                all_files=all_files,
                filter_regex_include=None,
                filter_regex_exclude=[],
                file_names_regex=[],
                file_extensions=file_extensions,
                ignored_files=[],
                ignore_generated_files=False,
            )
            self.assertListEqual(
                sorted(filtered_files), sorted(expected), f"check {file_extensions}"
            )

    def test_filter_regex_exclude_single_level(self):
        all_files = [
            "index.html",
            "target/index.html",
        ]
        filtered_files = utils.filter_files(
            all_files=all_files,
            filter_regex_include=None,
            filter_regex_exclude=["(^index.html)"],
            file_names_regex=[],
            file_extensions=["*"],
            ignored_files=[],
            ignore_generated_files=False,
        )
        self.assertListEqual(
            sorted(filtered_files),
            sorted(["target/index.html"]),
            "check regex_exclude_multilevel",
        )

    def test_filter_regex_exclude_multilevel(self):
        all_files = [
            "should/be/excluded/descriptor-level/test.md",
            "target/foo.md",
            "should/be/excluded/descriptor-level/test2.md",
            "should/be/excluded/linter-level/test.md",
            "should/be/excluded/linter-level/test2.md",
            "target/foo2.ext",
        ]
        filtered_files = utils.filter_files(
            all_files=all_files,
            filter_regex_include=None,
            filter_regex_exclude=["(descriptor-level)", "(linter-level)"],
            file_names_regex=[],
            file_extensions=[".md"],
            ignored_files=[],
            ignore_generated_files=False,
        )
        self.assertListEqual(
            sorted(filtered_files),
            sorted(["target/foo.md"]),
            "check regex_exclude_multilevel",
        )
