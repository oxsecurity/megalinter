import unittest
from unittest import mock

from megalinter.native.catalog import load_native_specs
from megalinter.native.manual_install import manual_install_groups
from megalinter.native.resolve import NATIVE_PLATFORMS, NativeLinterSpec

POSIX = ("linux/amd64", "linux/arm64", "darwin/amd64", "darwin/arm64")
LINUX = ("linux/amd64", "linux/arm64")
DARWIN = ("darwin/amd64", "darwin/arm64")
WINDOWS = ("windows/amd64",)
ALL = tuple(NATIVE_PLATFORMS)
TOOL_URL = "https://example.com/v{{VERSION}}/tool_{{VERSION}}_linux_amd64.tar.gz"
ANY_URL = "https://example.com/{{VERSION}}/tool.zip"


def make_spec(native_install, install=None):
    linter = {
        "linter_name": "tool",
        "install": install or {},
        "native_install": {"platforms": list(NATIVE_PLATFORMS), **native_install},
    }
    return NativeLinterSpec("TEST", {}, linter, None)


def groups_of(spec, lock=None):
    with mock.patch(
        "megalinter.native.manual_install.load_fresh_lock", return_value=lock
    ):
        return {
            tuple(group.platforms): "\n".join(group.lines)
            for group in manual_install_groups(spec)
        }


def lock_for(url, sha256="ab" * 32):
    return {"platforms": {"linux/amd64": {"assets": [{"url": url, "sha256": sha256}]}}}


class ManualInstallTest(unittest.TestCase):
    def test_pip_splits_windows_from_posix(self):
        spec = make_spec(
            {"method": "pip", "requires": [{"runtime": "python", "version": ">=3.9"}]},
            {
                "dockerfile": ["ARG PIP_TOOL_VERSION=1.2.3"],
                "pip": ["tool==${PIP_TOOL_VERSION}"],
            },
        )
        groups = groups_of(spec)
        self.assertEqual(list(groups), [POSIX, WINDOWS])
        self.assertIn('uv venv "$INSTALL_DIR" --python ">=3.9"', groups[POSIX])
        self.assertIn('"tool==1.2.3"', groups[POSIX])
        self.assertIn("$INSTALL_DIR/bin/python", groups[POSIX])
        self.assertIn("$INSTALL_DIR/Scripts/python.exe", groups[WINDOWS])

    def test_unsupported_platforms_have_no_tab(self):
        spec = make_spec(
            {
                "method": "npm",
                "packages": ["tool@1.0.0"],
                "platforms": ["linux/amd64", "darwin/arm64"],
            }
        )
        self.assertEqual(list(groups_of(spec)), [("linux/amd64", "darwin/arm64")])

    def test_package_methods_have_a_single_group(self):
        for native_install in (
            {"method": "npm", "packages": ["tool@1.0.0"]},
            {"method": "gem", "packages": ["tool:1.0.0"]},
            {
                "method": "go",
                "version": "1.0.0",
                "packages": ["example.com/tool@v1.0.0"],
            },
            {"method": "dotnet_tool", "version": "1.0.0", "packages": ["tool"]},
        ):
            groups = groups_of(make_spec(native_install))
            self.assertEqual(list(groups), [ALL], native_install)

    def test_powershell_module_uses_windows_paths_on_windows(self):
        spec = make_spec(
            {"method": "powershell_module", "version": "1.0.0", "packages": ["Tool"]}
        )
        windows = groups_of(spec)[WINDOWS]
        self.assertIn(
            'export PSModulePath="$(cygpath -w "$INSTALL_DIR");$PSModulePath"', windows
        )

    def test_binary_checksum_stops_the_install_on_mismatch(self):
        spec = make_spec(
            {
                "method": "binary",
                "version": "2.0.0",
                "assets": {"linux/amd64": {"url": TOOL_URL, "archive": "tar.gz"}},
                "platforms": ["linux/amd64"],
            }
        )
        url = "https://example.com/v2.0.0/tool_2.0.0_linux_amd64.tar.gz"
        lines = groups_of(spec, lock_for(url))[("linux/amd64",)].splitlines()
        checksum = next(line for line in lines if "sha256sum -c -" in line)
        self.assertTrue(checksum.endswith(" &&"))
        self.assertTrue(
            lines[lines.index(checksum) + 1].lstrip().startswith("tar -xzf")
        )
        self.assertTrue(any(line.lstrip().startswith("export PATH=") for line in lines))

    def test_binary_without_fresh_lock_has_no_checksum(self):
        spec = make_spec(
            {
                "method": "binary",
                "version": "2.0.0",
                "assets": {"linux/amd64": {"url": TOOL_URL, "archive": "tar.gz"}},
                "platforms": ["linux/amd64"],
            }
        )
        self.assertNotIn("sha256sum", groups_of(spec)[("linux/amd64",)])

    def test_binary_same_asset_merges_platforms_with_same_checker(self):
        spec = make_spec(
            {
                "method": "binary",
                "version": "2.0.0",
                "assets": {
                    "any": {"url": ANY_URL, "archive": "zip", "strip_components": 1}
                },
                "executables": {"tool": "bin/tool"},
                "overrides": {
                    "windows/amd64": {"executables": {"tool": "bin/tool.bat"}}
                },
            }
        )
        groups = groups_of(spec, lock_for("https://example.com/2.0.0/tool.zip"))
        self.assertEqual(list(groups), [LINUX + WINDOWS, DARWIN])
        self.assertIn("shasum -a 256 -c -", groups[DARWIN])
        self.assertIn('export PATH="$INSTALL_DIR/bin:$PATH"', groups[LINUX + WINDOWS])

    def test_binary_gz_asset_is_named_and_executable(self):
        spec = make_spec(
            {
                "method": "binary",
                "version": "2.0.0",
                "assets": {
                    "any": {
                        "url": "https://example.com/tool_{{VERSION}}.gz",
                        "archive": "gz",
                        "name": "tool",
                    }
                },
                "platforms": ["linux/amd64"],
            }
        )
        text = groups_of(spec)[("linux/amd64",)]
        self.assertIn(
            'gunzip -c "$INSTALL_DIR/tool_2.0.0.gz" > "$INSTALL_DIR/tool"', text
        )
        self.assertIn('chmod +x "$INSTALL_DIR/tool"', text)

    def test_runtime_provided_suggestions_are_inline_code(self):
        spec = make_spec(
            {
                "method": "runtime_provided",
                "suggest": {
                    "linux": "Rscript -e \"install.packages('tool')\"",
                    "darwin": "brew install tool",
                    "windows": "winget install --id Tool.Tool -e (then restart)",
                },
            }
        )
        groups = groups_of(spec)
        self.assertEqual(list(groups), [LINUX, DARWIN, WINDOWS])
        self.assertEqual(groups[LINUX], "`Rscript -e \"install.packages('tool')\"`")
        self.assertEqual(
            groups[WINDOWS], "`winget install --id Tool.Tool -e (then restart)`"
        )

    def test_runtime_provided_without_suggestion_uses_the_runtime_catalog(self):
        spec = make_spec(
            {"method": "runtime_provided", "requires": [{"runtime": "rust"}]}
        )
        groups = groups_of(spec)
        self.assertEqual(list(groups), [LINUX, DARWIN, WINDOWS])
        self.assertIn(
            "Provided by the `rust` runtime, install it with:", groups[WINDOWS]
        )
        self.assertIn("`winget install", groups[WINDOWS])

    def test_every_linter_renders_without_placeholders(self):
        for spec in load_native_specs():
            if not spec.native_install:
                continue
            groups = manual_install_groups(spec)
            self.assertTrue(groups, spec.key)
            for group in groups:
                text = "\n".join(group.lines)
                self.assertNotIn("${", text, spec.key)
                self.assertNotIn("{{", text, spec.key)
