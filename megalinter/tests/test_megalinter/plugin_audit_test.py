#!/usr/bin/env python3
import json
import os
import tempfile
import unittest

import yaml
from megalinter import plugin_audit
from megalinter.native.lock import LOCK_FORMAT_VERSION, compute_spec_hash
from megalinter.native.resolve import NativeLinterSpec, resolve_native_install

FIXTURES_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "..",
    "..",
    ".automation",
    "test",
    "plugin_audit",
)
BASE_URL = "https://raw.githubusercontent.com/owner/repo/main"
COMPLETE_URL = (
    f"{BASE_URL}/mega-linter-plugin-complete/complete.megalinter-descriptor.yml"
)
MINIMAL_URL = f"{BASE_URL}/mega-linter-plugin-minimal/minimal.megalinter-descriptor.yml"


def read_fixture(folder, file_name):
    with open(
        os.path.join(FIXTURES_DIR, folder, file_name), "r", encoding="utf-8"
    ) as f:
        return f.read()


def fake_get(responses):
    calls = []

    def get(url, retries=3):
        calls.append(url)
        return responses.get(url, (404, ""))

    get.calls = calls
    return get


def entry(name, url):
    return {
        "name": name,
        "description": "Test plugin",
        "docUrl": "https://example.com",
        "pluginUrl": url,
        "author": "[Someone](https://example.com)",
    }


def complete_lock(descriptor_text, spec_hash=None):
    descriptor = yaml.safe_load(descriptor_text)
    linter = descriptor["linters"][0]
    spec = NativeLinterSpec(descriptor["descriptor_id"], None, linter, None)
    return {
        "format": LOCK_FORMAT_VERSION,
        "linters": {
            spec.key: {
                "spec_hash": spec_hash
                or compute_spec_hash(resolve_native_install(spec))
            }
        },
    }


class plugin_audit_test(unittest.TestCase):
    def test_complete_plugin(self):
        text = read_fixture(
            "mega-linter-plugin-complete", "complete.megalinter-descriptor.yml"
        )
        result = plugin_audit.audit_plugin(
            entry("complete", COMPLETE_URL),
            get=fake_get({COMPLETE_URL: (200, text)}),
            checked_at="2026-01-01",
        )
        self.assertEqual(result["status"], "ok", result)
        self.assertEqual(result["errors"], [])
        self.assertEqual(plugin_audit.missing_requirements(result), [])
        linter = result["linters"]["AUDITTEST_AUDIT_LINT"]
        self.assertEqual(linter["native"]["status"], "ok")
        self.assertEqual(linter["sarif"], "text")
        self.assertEqual(linter["recommended_missing"], [])
        self.assertEqual(result["lock"], "none")
        self.assertEqual(
            plugin_audit.missing_recommendations(result), [(None, "native_lock")]
        )
        self.assertEqual(result["repository"], "owner/repo")
        self.assertEqual(result["last_success_at"], "2026-01-01")

    def test_minimal_plugin(self):
        text = read_fixture(
            "mega-linter-plugin-minimal", "minimal.megalinter-descriptor.yml"
        )
        result = plugin_audit.audit_plugin(
            entry("minimal", MINIMAL_URL), get=fake_get({MINIMAL_URL: (200, text)})
        )
        self.assertEqual(result["status"], "incomplete")
        linter = result["linters"]["MINIMALTEST_MINIMAL_LINT"]
        self.assertEqual(
            linter["required_missing"], ["native_install", "sarif", "cli_lint_mode"]
        )
        self.assertEqual(linter["native"]["status"], "missing")
        self.assertIn("linter_rules_url", linter["recommended_missing"])

    def test_core_collisions(self):
        descriptor = {
            "descriptor_id": "PYTHON",
            "descriptor_type": "language",
            "linters": [
                {
                    "linter_name": "black",
                    "linter_url": "https://example.com",
                    "examples": ["black ."],
                }
            ],
        }
        result = plugin_audit.audit_descriptor(
            descriptor,
            "python.megalinter-descriptor.yml",
            plugin_audit.core_inventory(),
        )
        self.assertIn("descriptor_file_unique", result["required_missing"])
        self.assertIn(
            "linter_key_unique", result["linters"]["PYTHON_BLACK"]["required_missing"]
        )

    def test_reused_core_descriptor_id_is_allowed(self):
        descriptor = {
            "descriptor_id": "PYTHON",
            "descriptor_type": "language",
            "linters": [
                {
                    "linter_name": "my-plugin-lint",
                    "linter_url": "https://example.com",
                    "examples": ["my-plugin-lint ."],
                }
            ],
        }
        result = plugin_audit.audit_descriptor(
            descriptor, "mine.megalinter-descriptor.yml", plugin_audit.core_inventory()
        )
        self.assertEqual(result["required_missing"], [])
        self.assertNotIn(
            "linter_key_unique",
            result["linters"]["PYTHON_MY_PLUGIN_LINT"]["required_missing"],
        )

    def test_schema_errors(self):
        text = read_fixture(
            "mega-linter-plugin-minimal", "minimal.megalinter-descriptor.yml"
        )
        text = text.replace("descriptor_type: format", "descriptor_type: not-a-type")
        result = plugin_audit.audit_plugin(
            entry("minimal", MINIMAL_URL), get=fake_get({MINIMAL_URL: (200, text)})
        )
        self.assertEqual(result["status"], "invalid")
        self.assertIn("schema", result["required_missing"])
        self.assertTrue(any("descriptor_type" in error for error in result["errors"]))

    def test_invalid_yaml(self):
        result = plugin_audit.audit_plugin(
            entry("minimal", MINIMAL_URL),
            get=fake_get({MINIMAL_URL: (200, "linters: [unclosed")}),
        )
        self.assertEqual(result["status"], "invalid")
        self.assertIn("schema", result["required_missing"])

    def test_invalid_native_install(self):
        text = read_fixture(
            "mega-linter-plugin-complete", "complete.megalinter-descriptor.yml"
        )
        text = text.replace("        - windows/amd64\n", "")
        result = plugin_audit.audit_plugin(
            entry("complete", COMPLETE_URL), get=fake_get({COMPLETE_URL: (200, text)})
        )
        linter = result["linters"]["AUDITTEST_AUDIT_LINT"]
        self.assertEqual(linter["native"]["status"], "invalid")
        self.assertIn("native_install", linter["required_missing"])
        self.assertTrue(
            any("windows/amd64" in error for error in linter["native"]["errors"])
        )

    def test_partial_native_platforms(self):
        text = read_fixture(
            "mega-linter-plugin-complete", "complete.megalinter-descriptor.yml"
        )
        text = text.replace(
            "        - windows/amd64\n",
            "      unsupported:\n        windows/amd64: No Windows build. Use Docker.\n",
        )
        result = plugin_audit.audit_plugin(
            entry("complete", COMPLETE_URL), get=fake_get({COMPLETE_URL: (200, text)})
        )
        linter = result["linters"]["AUDITTEST_AUDIT_LINT"]
        self.assertEqual(linter["native"]["status"], "partial")
        self.assertEqual(
            linter["native"]["unsupported"],
            {"windows/amd64": "No Windows build. Use Docker."},
        )
        self.assertEqual(result["status"], "ok")

    def test_fresh_and_stale_lock(self):
        text = read_fixture(
            "mega-linter-plugin-complete", "complete.megalinter-descriptor.yml"
        )
        lock_url = plugin_audit.plugin_lock_url(COMPLETE_URL)
        self.assertTrue(lock_url.endswith("/complete.megalinter-native-lock.json"))
        fresh = plugin_audit.audit_plugin(
            entry("complete", COMPLETE_URL),
            get=fake_get(
                {
                    COMPLETE_URL: (200, text),
                    lock_url: (200, json.dumps(complete_lock(text))),
                }
            ),
        )
        self.assertEqual(fresh["lock"], "fresh")
        self.assertEqual(plugin_audit.missing_recommendations(fresh), [])
        stale = plugin_audit.audit_plugin(
            entry("complete", COMPLETE_URL),
            get=fake_get(
                {
                    COMPLETE_URL: (200, text),
                    lock_url: (200, json.dumps(complete_lock(text, "0" * 64))),
                }
            ),
        )
        self.assertEqual(stale["lock"], "stale")
        self.assertEqual(stale["status"], "incomplete")
        self.assertIn(
            "native_lock_fresh",
            stale["linters"]["AUDITTEST_AUDIT_LINT"]["required_missing"],
        )

    def test_url_rules(self):
        url = "https://raw.githubusercontent.com/owner/repo/main/plugin/linter.yml"
        get = fake_get({})
        result = plugin_audit.audit_plugin(entry("bad", url), get=get)
        self.assertEqual(result["status"], "invalid")
        self.assertEqual(result["required_missing"], ["url"])
        self.assertEqual(len(result["errors"]), 2)
        self.assertEqual(get.calls, [])

    def test_blob_url(self):
        blob_url = "https://github.com/owner/repo/blob/main/mega-linter-plugin-x/x.megalinter-descriptor.yml"
        self.assertEqual(
            plugin_audit.raw_descriptor_url(blob_url),
            "https://raw.githubusercontent.com/owner/repo/main/mega-linter-plugin-x/x.megalinter-descriptor.yml",
        )
        self.assertEqual(plugin_audit.github_repository(blob_url), "owner/repo")
        self.assertIsNone(
            plugin_audit.github_repository("https://gitlab.com/owner/repo/-/raw/main/x")
        )

    def test_unreachable_keeps_previous_results(self):
        text = read_fixture(
            "mega-linter-plugin-minimal", "minimal.megalinter-descriptor.yml"
        )
        previous = plugin_audit.audit_plugin(
            entry("minimal", MINIMAL_URL),
            get=fake_get({MINIMAL_URL: (200, text)}),
            checked_at="2026-01-01",
        )
        result = plugin_audit.audit_plugin(
            entry("minimal", MINIMAL_URL),
            previous,
            get=fake_get({MINIMAL_URL: (503, "")}),
            checked_at="2026-01-02",
        )
        self.assertEqual(result["status"], "unreachable")
        self.assertIn("HTTP 503", result["fetch_error"])
        self.assertEqual(result["checked_at"], "2026-01-02")
        self.assertEqual(result["last_success_at"], "2026-01-01")
        self.assertEqual(result["linters"], previous["linters"])

    def test_unreachable_without_previous_results(self):
        result = plugin_audit.audit_plugin(
            entry("minimal", MINIMAL_URL), get=fake_get({MINIMAL_URL: (404, "")})
        )
        self.assertEqual(result["status"], "unreachable")
        self.assertEqual(result["linters"], {})
        self.assertEqual(plugin_audit.missing_requirements(result), [])

    def test_audit_file_round_trip(self):
        text = read_fixture(
            "mega-linter-plugin-minimal", "minimal.megalinter-descriptor.yml"
        )
        audit = plugin_audit.audit_catalog(
            [entry("minimal", MINIMAL_URL)], get=fake_get({MINIMAL_URL: (200, text)})
        )
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "plugins-audit.json")
            plugin_audit.write_audit_file(path, audit)
            with open(path, "r", encoding="utf-8") as f:
                document = json.load(f)
            self.assertEqual(document["@generated"], plugin_audit.AUDIT_FILE_HEADER)
            self.assertEqual(plugin_audit.load_audit_file(path), audit)
            self.assertEqual(plugin_audit.load_audit_file(path + ".missing"), {})

    def test_requirement_labels(self):
        for item in plugin_audit.REQUIRED_CHECKS:
            self.assertNotEqual(plugin_audit.requirement_label(item), item)
        for item in plugin_audit.RECOMMENDED_LINTER_PROPERTIES:
            self.assertNotEqual(plugin_audit.requirement_label(item), item)
        self.assertEqual(
            plugin_audit.plugin_slug("Docker Compose_Linter"), "docker-compose-linter"
        )
