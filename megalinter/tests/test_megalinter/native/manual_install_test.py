import unittest

from megalinter.native.catalog import load_native_specs
from megalinter.native.manual_install import manual_install_groups

SPECS = {spec.key: spec for spec in load_native_specs()}


def groups_of(key):
    return {
        tuple(group.platforms): "\n".join(group.lines)
        for group in manual_install_groups(SPECS[key])
    }


class ManualInstallTest(unittest.TestCase):
    def test_pip_splits_windows_from_posix(self):
        groups = groups_of("PYTHON_RUFF")
        self.assertEqual(len(groups), 2)
        posix = groups[("linux/amd64", "linux/arm64", "darwin/amd64", "darwin/arm64")]
        windows = groups[("windows/amd64",)]
        self.assertIn('"ruff==0.17.2"', posix)
        self.assertIn("$INSTALL_DIR/bin/python", posix)
        self.assertIn("$INSTALL_DIR/Scripts/python.exe", windows)

    def test_unsupported_platforms_have_no_tab(self):
        platforms = [
            p
            for group in manual_install_groups(SPECS["ANSIBLE_ANSIBLE_LINT"])
            for p in group.platforms
        ]
        self.assertEqual(platforms, ["linux/amd64", "linux/arm64", "darwin/arm64"])

    def test_single_group_methods(self):
        for key in (
            "MARKDOWN_MARKDOWNLINT",
            "RUBY_RUBOCOP",
            "REPOSITORY_DUSTILOCK",
            "CSHARP_CSHARPIER",
        ):
            self.assertEqual(len(manual_install_groups(SPECS[key])), 1, key)

    def test_binary_has_one_tab_per_platform_with_checksum(self):
        groups = groups_of("ACTION_ACTIONLINT")
        self.assertEqual(len(groups), 5)
        linux = groups[("linux/amd64",)]
        self.assertIn("actionlint_1.7.12_linux_amd64.tar.gz", linux)
        self.assertIn("sha256sum -c -", linux)
        self.assertIn("shasum -a 256 -c -", groups[("darwin/amd64",)])
        self.assertIn("unzip -q", groups[("windows/amd64",)])

    def test_binary_same_asset_merges_platforms_with_same_checker(self):
        groups = groups_of("JAVA_PMD")
        self.assertEqual(len(groups), 2)
        self.assertIn(
            'export PATH="$INSTALL_DIR/bin:$PATH"',
            groups[("linux/amd64", "linux/arm64", "windows/amd64")],
        )

    def test_runtime_provided_uses_suggestions_per_os(self):
        groups = groups_of("C_CPPCHECK")
        self.assertEqual(len(groups), 3)
        self.assertIn("brew install cppcheck", groups[("darwin/amd64", "darwin/arm64")])
        self.assertIn("winget install", groups[("windows/amd64",)])

    def test_runtime_provided_without_suggestion_names_the_runtime(self):
        groups = groups_of("RUST_CLIPPY")
        self.assertTrue(all("`rust`" in text for text in groups.values()))

    def test_every_linter_renders_without_placeholders(self):
        for key, spec in SPECS.items():
            if not spec.native_install:
                continue
            groups = manual_install_groups(spec)
            self.assertTrue(groups, key)
            for group in groups:
                text = "\n".join(group.lines)
                self.assertNotIn("${", text, key)
                self.assertNotIn("{{", text, key)
