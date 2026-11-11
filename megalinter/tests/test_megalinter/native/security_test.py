import os
import stat
import sys
import tempfile
import unittest
import zipfile
from unittest import mock

from megalinter import config, pre_post_factory
from megalinter.native import methods, selection
from megalinter.native.context import (
    NativeError,
    check_home_permissions,
    is_wsl_launcher,
)
from megalinter.native.lock import (
    check_lock_fresh,
    compute_spec_hash,
    load_lock,
    write_lock,
)
from megalinter.native.state import read_state, update_state
from megalinter.native.toolchain import Toolchain, build_subprocess_env


class FakeLinter:
    def __init__(self, name):
        self.name = name


class EnvironmentTest(unittest.TestCase):
    def test_host_secrets_are_not_given_to_linters(self):
        base = {
            "PATH": os.pathsep.join(["/usr/bin", "/bin"]),
            "HOME": "/home/user",
            "AWS_SECRET_ACCESS_KEY": "secret",
            "NPM_TOKEN": "secret",
            "SSH_AUTH_SOCK": "/tmp/agent",
            "GITHUB_TOKEN": "secret",
            "HTTPS_PROXY": "http://proxy",
        }
        env = build_subprocess_env(base, Toolchain(["/tools/bin"]), None)
        self.assertNotIn("AWS_SECRET_ACCESS_KEY", env)
        self.assertNotIn("NPM_TOKEN", env)
        self.assertNotIn("SSH_AUTH_SOCK", env)
        self.assertNotIn("GITHUB_TOKEN", env)
        self.assertEqual(env["HTTPS_PROXY"], "http://proxy")
        self.assertEqual(env["HOME"], "/home/user")

    def test_toolchain_directories_come_first_in_path(self):
        base = {"PATH": "/usr/bin"}
        env = build_subprocess_env(
            base, Toolchain(["/tools/bin", "/runtime/bin"]), None
        )
        self.assertEqual(
            env["PATH"].split(os.pathsep), ["/tools/bin", "/runtime/bin", "/usr/bin"]
        )

    def test_variables_explicitly_allowed_are_kept(self):
        base = {"PATH": "/usr/bin", "MY_TOKEN": "x"}
        with mock.patch.dict(os.environ, {"NATIVE_ENV_ALLOWLIST": "MY_TOKEN"}):
            config.refresh_env_snapshot()
            env = build_subprocess_env(base, Toolchain(), None)
        config.refresh_env_snapshot()
        self.assertEqual(env["MY_TOKEN"], "x")

    def test_toolchain_env_is_applied(self):
        env = build_subprocess_env(
            {"PATH": "/x"}, Toolchain([], {"JAVA_HOME": "/jdk"}), None
        )
        self.assertEqual(env["JAVA_HOME"], "/jdk")


class TrustTest(unittest.TestCase):
    def test_repository_is_untrusted_by_default_in_native_mode(self):
        with mock.patch.dict(os.environ, {"MEGALINTER_NATIVE": "true"}):
            os.environ.pop("NATIVE_TRUST_REPO_COMMANDS", None)
            self.assertTrue(config.native_repo_untrusted())

    def test_trust_comes_from_the_environment(self):
        with mock.patch.dict(
            os.environ,
            {"MEGALINTER_NATIVE": "true", "NATIVE_TRUST_REPO_COMMANDS": "true"},
        ):
            self.assertFalse(config.native_repo_untrusted())

    def test_docker_mode_is_not_affected(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("MEGALINTER_NATIVE", None)
            self.assertFalse(config.native_repo_untrusted())

    def test_repository_commands_are_skipped_when_untrusted(self):
        commands = [{"command": "touch /tmp/should-not-exist"}]
        with mock.patch.dict(os.environ, {"MEGALINTER_NATIVE": "true"}):
            os.environ.pop("NATIVE_TRUST_REPO_COMMANDS", None)
            with mock.patch.object(pre_post_factory, "run_command") as run_command:
                result = pre_post_factory.run_commands(commands, "[test]", None)
        run_command.assert_not_called()
        self.assertEqual(result, [])


class ContextTest(unittest.TestCase):
    @unittest.skipUnless(sys.platform == "win32", "Windows only")
    def test_wsl_launcher_is_not_git_bash(self):
        self.assertTrue(is_wsl_launcher(r"C:\Windows\System32\bash.exe"))
        self.assertFalse(is_wsl_launcher(r"C:\Program Files\Git\bin\bash.exe"))

    @unittest.skipUnless(os.name == "posix", "POSIX only")
    def test_group_writable_home_is_refused(self):
        home = tempfile.mkdtemp()
        os.chmod(home, 0o775)
        with self.assertRaises(NativeError):
            check_home_permissions(home)
        os.chmod(home, 0o700)
        check_home_permissions(home)


class SelectionTest(unittest.TestCase):
    def setUp(self):
        self.active = [FakeLinter("PYTHON_BLACK"), FakeLinter("JAVASCRIPT_ES")]
        self.known = {"PYTHON_BLACK", "JAVASCRIPT_ES", "CSS_STYLELINT"}

    def test_nothing_runs_natively_without_an_explicit_list(self):
        result = selection.select_native_linters(None, self.active, self.known, [])
        self.assertEqual(result.selected, [])
        self.assertEqual(len(result.not_listed), 2)

    def test_only_listed_linters_are_selected(self):
        result = selection.select_native_linters(
            None, self.active, self.known, ["PYTHON_BLACK"]
        )
        self.assertEqual([linter.name for linter in result.selected], ["PYTHON_BLACK"])
        self.assertEqual(
            [linter.name for linter in result.not_listed], ["JAVASCRIPT_ES"]
        )

    def test_listed_but_inactive_linters_are_reported(self):
        result = selection.select_native_linters(
            None, self.active, self.known, ["CSS_STYLELINT"]
        )
        self.assertEqual(result.listed_not_active, ["CSS_STYLELINT"])
        self.assertEqual(result.selected, [])

    def test_unknown_linter_is_an_error(self):
        with self.assertRaises(NativeError):
            selection.select_native_linters(None, self.active, self.known, ["NOPE"])

    def test_all_selects_everything_and_warns(self):
        with self.assertLogs(level="WARNING") as logs:
            result = selection.select_native_linters(
                None, self.active, self.known, ["all"]
            )
        self.assertTrue(result.wants_all)
        self.assertEqual(len(result.selected), 2)
        self.assertIn("discouraged", "\n".join(logs.output))


class LockAndStateTest(unittest.TestCase):
    def test_spec_hash_is_stable_and_detects_changes(self):
        first = compute_spec_hash({"method": "pip", "packages": ["a==1"]})
        self.assertEqual(
            first, compute_spec_hash({"packages": ["a==1"], "method": "pip"})
        )
        self.assertNotEqual(
            first, compute_spec_hash({"method": "pip", "packages": ["a==2"]})
        )

    def test_stale_lock_is_refused(self):
        folder = tempfile.mkdtemp()
        native = {"method": "pip", "packages": ["a==1"]}
        write_lock(
            "X",
            {"linter": "X", "method": "pip", "spec_hash": compute_spec_hash(native)},
            folder,
        )
        lock = load_lock("X", folder)
        check_lock_fresh("X", native, lock)
        with self.assertRaises(NativeError):
            check_lock_fresh("X", {"method": "pip", "packages": ["a==2"]}, lock)

    def test_missing_lock_is_refused(self):
        with self.assertRaises(NativeError):
            load_lock("MISSING", tempfile.mkdtemp())

    def test_state_roundtrip(self):
        home = tempfile.mkdtemp()
        update_state(home, "linters", "X", {"dir": "/d"})
        self.assertEqual(read_state(home)["linters"]["X"], {"dir": "/d"})
        update_state(home, "linters", "X", None)
        self.assertEqual(read_state(home)["linters"], {})


class BinaryInstallTest(unittest.TestCase):
    def test_binary_install_creates_executables_and_uses_verified_download(self):
        home = tempfile.mkdtemp()
        destination = os.path.join(home, "install")
        os.makedirs(destination)
        archive = os.path.join(home, "tool.zip")
        with zipfile.ZipFile(archive, "w") as bundle:
            info = zipfile.ZipInfo("tool-1/bin/tool")
            info.external_attr = (stat.S_IFREG | 0o755) << 16
            bundle.writestr(info, "#!/bin/sh\necho ok\n")
            bundle.writestr("tool-1/lib/tool.jar", "jar")
        context = methods.InstallContext(
            "X",
            {
                "executables": {
                    "tool": "bin/tool",
                    "launched": {
                        "launcher": "java",
                        "args": ["-jar", "{{NATIVE_INSTALL_DIR}}/lib/tool.jar"],
                    },
                }
            },
            {},
            {
                "assets": [
                    {
                        "url": "https://example.com/tool.zip",
                        "sha256": "a" * 64,
                        "size": 1,
                        "archive": "zip",
                        "strip_components": 1,
                    }
                ]
            },
            destination,
            home,
            {"PATH": ""},
            ["tool"],
            False,
        )
        with mock.patch.object(
            methods, "fetch_verified", return_value=archive
        ) as fetch:
            result = methods.install_binary(context)
        fetch.assert_called_once()
        self.assertTrue(os.path.isfile(os.path.join(destination, "bin", "tool")))
        self.assertIn(os.path.join(destination, "bin"), result.path_dirs)
        shim = os.path.join(destination, "shims", "launched")
        self.assertTrue(os.path.isfile(shim))
        with open(shim, "r", encoding="utf-8") as f:
            self.assertIn("lib/tool.jar", f.read().replace("\\", "/"))
