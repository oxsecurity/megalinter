import unittest

from megalinter.native.catalog import load_native_specs
from megalinter.native.resolve import (
    NativeLinterSpec,
    apply_native_overrides,
    platform_native_install,
    resolve_native_install,
    resolve_version_reference,
)
from megalinter.native.runtimes import satisfies, version_tuple
from megalinter.native.spec import validate_all

DOCKERFILE = [
    "# renovate: datasource=pypi depName=black\nARG PIP_BLACK_VERSION=26.10.1",
    "FROM hadolint/hadolint:v2.14.0 AS hadolint\nCOPY --from=hadolint /bin/hadolint /usr/bin/",
]


def make_spec(native_install, install=None):
    linter = {
        "linter_name": "black",
        "install": install
        or {"dockerfile": DOCKERFILE, "pip": ["black==${PIP_BLACK_VERSION}"]},
        "native_install": native_install,
    }
    return NativeLinterSpec("PYTHON", {}, linter, None)


class ResolveTest(unittest.TestCase):
    def test_arg_reference(self):
        spec = make_spec({"method": "pip"})
        self.assertEqual(
            resolve_version_reference("${PIP_BLACK_VERSION}", spec), "26.10.1"
        )

    def test_from_tag_reference_keeps_v_prefix(self):
        spec = make_spec({"method": "binary"})
        self.assertEqual(
            resolve_version_reference("${FROM_TAG:hadolint/hadolint}", spec), "v2.14.0"
        )

    def test_unknown_reference_is_an_error(self):
        with self.assertRaises(KeyError):
            resolve_version_reference("${NOPE_VERSION}", make_spec({"method": "pip"}))

    def test_packages_default_to_docker_install(self):
        resolved = resolve_native_install(make_spec({"method": "pip"}))
        self.assertEqual(resolved["packages"], ["black==26.10.1"])

    def test_platform_overrides_replace_keys(self):
        native = {
            "method": "binary",
            "executables": {"tool": "tool"},
            "overrides": {"windows/amd64": {"executables": {"tool": "tool.exe"}}},
        }
        self.assertEqual(
            platform_native_install(native, "linux/amd64")["executables"],
            {"tool": "tool"},
        )
        self.assertEqual(
            platform_native_install(native, "windows/amd64")["executables"],
            {"tool": "tool.exe"},
        )
        self.assertEqual(
            platform_native_install(native, "windows/arm64")["executables"],
            {"tool": "tool.exe"},
        )

    def test_linter_overrides_replace_install_dir_placeholder(self):
        descriptor = {
            "linter_name": "pmd",
            "native_install": {
                "method": "binary",
                "linter_overrides": {
                    "cli_executable": "{{NATIVE_INSTALL_DIR}}/bin/pmd"
                },
            },
        }
        result = apply_native_overrides(
            descriptor, "linux/amd64", "JAVA", {}, "/home/user/.megalinter"
        )
        self.assertIn(".megalinter", result["cli_executable"])
        self.assertNotIn("{{", result["cli_executable"])

    def test_no_override_leaves_the_descriptor_untouched(self):
        descriptor = {"linter_name": "x", "native_install": {"method": "pip"}}
        self.assertIs(
            apply_native_overrides(descriptor, "linux/amd64", "X", {}, "/h"), descriptor
        )


class VersionTest(unittest.TestCase):
    def test_constraints(self):
        self.assertTrue(satisfies("21.0.9", ">=21"))
        self.assertTrue(satisfies("22", ">=21"))
        self.assertFalse(satisfies("17.0.1", ">=21"))
        self.assertTrue(satisfies("3.12.1", ">=3.9,<4"))
        self.assertFalse(satisfies("4.0", ">=3.9,<4"))
        self.assertTrue(satisfies("1.2.3", None))

    def test_unsupported_constraint(self):
        with self.assertRaises(Exception):
            satisfies("1.0", "~=1.0")

    def test_version_tuple_ignores_build_metadata(self):
        self.assertEqual(version_tuple("21.0.13+9"), (21, 0, 13))


class DescriptorsTest(unittest.TestCase):
    def test_every_linter_declares_a_valid_native_install(self):
        specs, errors = validate_all()
        self.assertGreater(len(specs), 100)
        self.assertEqual(errors, [])

    def test_linter_keys_are_unique(self):
        keys = [spec.key for spec in load_native_specs()]
        self.assertEqual(len(keys), len(set(keys)))
