#!/usr/bin/env python3
"""Unit tests for the SPELL descriptor and its linters."""

# cspell:ignore activatable recieve

import os
import re
import tempfile
import unittest
import uuid

import yaml
from megalinter import config, linter_factory, utils

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


class SpellDescriptorTest(unittest.TestCase):
    def setUp(self):
        self.request_id = str(uuid.uuid1())
        config.init_config(self.request_id, None, {})

    def tearDown(self):
        config.delete(self.request_id)

    def _build_params(self, workspace, rules_dir):
        return {
            "default_linter_activation": True,
            "enable_descriptors": [],
            "enable_linters": [],
            "disable_descriptors": [],
            "disable_linters": [],
            "disable_errors_linters": [],
            "github_workspace": workspace,
            "workspace": workspace,
            "linter_rules_path": rules_dir,
            "default_rules_location": utils.get_default_rules_location(),
            "post_linter_status": True,
            "request_id": self.request_id,
        }

    def test_spell_proselint_deprecated_and_activatable_with_proselint_json(self):
        with tempfile.TemporaryDirectory() as tmp_workspace:
            rules_dir = os.path.join(tmp_workspace, ".github", "linters")
            os.makedirs(rules_dir, exist_ok=True)
            with open(
                os.path.join(rules_dir, "proselint.json"), "w", encoding="utf-8"
            ) as f:
                f.write('{"checks": {"airlinese": false}}\n')

            config.set_value(
                self.request_id, "SPELL_PROSELINT_CONFIG_FILE", "proselint.json"
            )
            proselint = linter_factory.build_linter(
                "SPELL", "proselint", self._build_params(tmp_workspace, rules_dir)
            )

            self.assertTrue(getattr(proselint, "deprecated", False))
            self.assertIsInstance(proselint.deprecated_description, str)
            self.assertTrue(len(proselint.deprecated_description.strip()) > 0)
            self.assertIn("SPELL_VALE", proselint.deprecated_description)
            self.assertIn("SPELL_TYPOS", proselint.deprecated_description)
            self.assertIn("cupcake", proselint.descriptor_flavors_exclude)
            self.assertTrue(proselint.is_active)

    def test_spell_proselint_activatable_with_proselintrc_json(self):
        with tempfile.TemporaryDirectory() as tmp_workspace:
            rules_dir = os.path.join(tmp_workspace, ".github", "linters")
            os.makedirs(rules_dir, exist_ok=True)
            with open(
                os.path.join(tmp_workspace, ".proselintrc.json"), "w", encoding="utf-8"
            ) as f:
                f.write('{"checks": {"airlinese": false}}\n')

            proselint = linter_factory.build_linter(
                "SPELL", "proselint", self._build_params(tmp_workspace, rules_dir)
            )

            self.assertTrue(getattr(proselint, "deprecated", False))
            self.assertTrue(proselint.is_active)

    def test_spell_descriptor_validates_against_schema_and_defines_typos(self):
        descriptor_path = os.path.join(
            REPO_ROOT, "megalinter", "descriptors", "spell.megalinter-descriptor.yml"
        )
        with open(descriptor_path, "r", encoding="utf-8") as f:
            descriptor = yaml.safe_load(f)

        self.assertEqual(descriptor["descriptor_id"], "SPELL")
        self.assertIsInstance(descriptor["linters"], list)

        typos_entries = [
            item for item in descriptor["linters"] if item.get("linter_name") == "typos"
        ]
        self.assertEqual(len(typos_entries), 1)
        typos = typos_entries[0]
        self.assertEqual(typos["name"], "SPELL_TYPOS")
        self.assertEqual(typos["class"], "TyposLinter")
        self.assertEqual(typos["test_folder"], "spell_typos")
        self.assertEqual(typos["linter_spdx_license"], "MIT OR Apache-2.0")
        self.assertEqual(typos["linter_speed"], 5)
        self.assertEqual(typos["config_file_name"], "typos.toml")
        self.assertEqual(typos["cli_config_arg_name"], "--config")
        self.assertEqual(typos["cli_lint_mode"], "list_of_files")
        self.assertEqual(
            typos["supported_cli_lint_modes"], ["file", "list_of_files", "project"]
        )
        self.assertEqual(typos["cli_lint_fix_arg_name"], "--write-changes")
        self.assertTrue(typos["is_formatter"])
        self.assertEqual(
            typos["test_format_fix_file_extensions"], [".md", ".py", ".txt"]
        )
        self.assertIn("--format", typos["cli_lint_extra_args"])
        self.assertIn("json", typos["cli_lint_extra_args"])
        self.assertIn("--force-exclude", typos["cli_lint_extra_args"])
        self.assertEqual(
            typos["supported_platforms"]["platform"], ["linux/amd64", "linux/arm64"]
        )
        dockerfile_block = "\n".join(typos["install"]["dockerfile"])
        self.assertIn(
            "# renovate: datasource=github-releases depName=crate-ci/typos",
            dockerfile_block,
        )
        self.assertIn("ARG SPELL_TYPOS_VERSION=1.52.0", dockerfile_block)

    def test_spell_typos_builds_cleanly(self):
        with tempfile.TemporaryDirectory() as tmp_workspace:
            rules_dir = os.path.join(tmp_workspace, ".github", "linters")
            os.makedirs(rules_dir, exist_ok=True)
            typos = linter_factory.build_linter(
                "SPELL", "typos", self._build_params(tmp_workspace, rules_dir)
            )

            self.assertEqual(typos.name, "SPELL_TYPOS")
            self.assertEqual(typos.linter_name, "typos")
            self.assertTrue(typos.is_active)
            self.assertFalse(typos.apply_fixes)
            self.assertTrue(typos.is_formatter)
            self.assertEqual(typos.cli_lint_fix_arg_name, "--write-changes")
            self.assertEqual(
                typos.supported_cli_lint_modes, ["file", "list_of_files", "project"]
            )
            self.assertEqual(typos.test_folder, "spell_typos")
            self.assertTrue(len(typos.test_format_fix_file_extensions) > 0)
            self.assertIn("--format", typos.cli_lint_extra_args)
            self.assertIn("json", typos.cli_lint_extra_args)
            self.assertIn("--force-exclude", typos.cli_lint_extra_args)
            self.assertEqual(typos.cli_lint_mode_project_extra_args_after, ["."])
            self.assertEqual(typos.cli_lint_mode_project_exclude_arg_name, "--exclude")
            self.assertEqual(
                typos.cli_lint_mode_project_exclude_arg_value, "**/{{DIR}}/**"
            )

    def test_spell_typos_regex_and_linter_text_conventions(self):
        descriptor_path = os.path.join(
            REPO_ROOT, "megalinter", "descriptors", "spell.megalinter-descriptor.yml"
        )
        with open(descriptor_path, "r", encoding="utf-8") as f:
            descriptor = yaml.safe_load(f)

        typos = next(
            item for item in descriptor["linters"] if item.get("linter_name") == "typos"
        )
        pattern = re.compile(typos["cli_lint_errors_regex"])
        sample_output = "\n".join(
            [
                '{"type":"binary_file","path":"./image.png"}',
                '{"type":"typo","path":"./a.py","line_num":1,"byte_offset":2,"typo":"teh","corrections":["the"]}',
                (
                    '{"type": "typo", "path": "./b.md", "line_num": 3, '
                    '"byte_offset": 0, "typo": "recieve", "corrections": ["receive"]}'
                ),
            ]
        )
        self.assertEqual(len(pattern.findall(sample_output)), 2)

        lines = typos["linter_text"].splitlines()
        for idx, line in enumerate(lines):
            if line.startswith("#") or line.strip() == "**Key Features:**":
                if idx + 1 < len(lines):
                    self.assertEqual(
                        lines[idx + 1],
                        "",
                        f"Expected blank line after {line!r} in linter_text",
                    )
            if (
                line.startswith("- ")
                and idx > 0
                and not lines[idx - 1].startswith("- ")
            ):
                self.assertEqual(
                    lines[idx - 1],
                    "",
                    "Expected blank line before bulleted list in linter_text",
                )

    def test_spell_proselint_linter_text_has_zensical_migration_guide(self):
        descriptor_path = os.path.join(
            REPO_ROOT, "megalinter", "descriptors", "spell.megalinter-descriptor.yml"
        )
        with open(descriptor_path, "r", encoding="utf-8") as f:
            descriptor = yaml.safe_load(f)

        proselint = next(
            item
            for item in descriptor["linters"]
            if item.get("linter_name") == "proselint"
        )
        linter_text = proselint["linter_text"]
        self.assertIn("Migration Guide", linter_text)
        self.assertIn(".proselintrc.json", linter_text)
        self.assertIn("SPELL_VALE", linter_text)
        self.assertIn(".vale.ini", linter_text)
        self.assertIn("SPELL_TYPOS", linter_text)
        self.assertIn("DISABLE_LINTERS", linter_text)
        self.assertIn("SPELL_PROSELINT", linter_text)

        lines = linter_text.splitlines()
        for idx, line in enumerate(lines):
            if line.startswith("#") and idx + 1 < len(lines):
                self.assertEqual(
                    lines[idx + 1],
                    "",
                    f"Expected blank line after heading {line!r} in SPELL_PROSELINT linter_text",
                )
            if (
                line.startswith("- ")
                and idx > 0
                and not lines[idx - 1].startswith("- ")
            ):
                self.assertEqual(
                    lines[idx - 1],
                    "",
                    "Expected blank line before bulleted list in SPELL_PROSELINT linter_text",
                )
            if (
                line.startswith("- ")
                and idx + 1 < len(lines)
                and not lines[idx + 1].startswith("- ")
                and not lines[idx + 1].startswith("  ")
            ):
                self.assertEqual(
                    lines[idx + 1],
                    "",
                    "Expected blank line after bulleted list in SPELL_PROSELINT linter_text",
                )
