#!/usr/bin/env python3
"""
Unit tests for the generic SARIF converter driven by the descriptors (sarif_text_regex),
and for the converters of the linters whose output is JSON or structured text.
The regular expressions are read from the descriptors, so they are tested as shipped
"""

import json
import os
import unittest

import yaml

import megalinter
from megalinter import linter_factory, utils, utilstest
from megalinter.linters.ArmLinter import arm_ttk_json_to_sarif
from megalinter.linters.CljStyleLinter import cljstyle_diff_to_sarif
from megalinter.linters.CSpellLinter import remap_file_names_results
from megalinter.linters.GherkinLintLinter import gherkin_lint_json_to_sarif
from megalinter.linters.HelmLintLinter import helm_lint_to_sarif
from megalinter.linters.KubeconformLinter import kubeconform_json_to_sarif
from megalinter.linters.LycheeLinter import lychee_json_to_sarif
from megalinter.linters.MypyLinter import mypy_json_to_sarif
from megalinter.linters.NpmPackageJsonLintLinter import npm_package_json_lint_to_sarif
from megalinter.linters.PhpCsFixerLinter import php_cs_fixer_json_to_sarif
from megalinter.linters.ProselintLinter import proselint_json_to_sarif
from megalinter.linters.PyrightLinter import pyright_json_to_sarif
from megalinter.linters.RstLintLinter import rst_lint_json_to_sarif
from megalinter.linters.ScalafixLinter import scalafix_to_sarif
from megalinter.linters.SnakemakeLinter import snakemake_lint_to_sarif
from megalinter.linters.StyLuaLinter import stylua_json_to_sarif
from megalinter.linters.TektonLintLinter import tekton_lint_json_to_sarif
from megalinter.linters.TofuValidateLinter import tofu_validate_json_to_sarif
from megalinter.linters.V8rLinter import v8r_json_to_sarif
from megalinter.sarif_builder import (
    SarifBuilder,
    SarifResultBuilder,
    SarifRunBuilder,
    add_whole_output_result,
    file_uri_to_path,
    regex_output_to_sarif,
    to_one_based,
    unified_diff_to_results,
)

DESCRIPTORS_DIR = os.path.join(os.path.dirname(megalinter.__file__), "descriptors")
WORKSPACE = os.path.abspath("lint-workspace")
WORKSPACE_URI = WORKSPACE.replace("\\", "/")


def results_of(sarif_builder):
    sarif_content = sarif_builder.build_sarif_output()
    schema_errors = utilstest.list_sarif_schema_errors(sarif_content)
    assert schema_errors == [], schema_errors
    return sarif_content["runs"][0]["results"]


# (rule, level, file, line, column) of each result
def summary(sarif_builder):
    summaries = []
    for result in results_of(sarif_builder):
        locations = result.get("locations")
        physical = locations[0]["physicalLocation"] if locations else {}
        region = physical.get("region", {})
        summaries.append(
            (
                result["ruleId"],
                result["level"],
                physical.get("artifactLocation", {}).get("uri"),
                region.get("startLine"),
                region.get("startColumn"),
            )
        )
    return summaries


def descriptor_linter(file_name, linter_name):
    with open(
        os.path.join(DESCRIPTORS_DIR, file_name), "r", encoding="utf-8"
    ) as descriptor_file:
        descriptor = yaml.safe_load(descriptor_file)
    for linter in descriptor["linters"]:
        if "extends" in linter:
            linter = linter_factory.resolve_linter_extends(linter)
        if linter["linter_name"] == linter_name:
            return linter
    raise KeyError(linter_name)


def convert_with_descriptor(file_name, linter_name, stdout, return_code=1):
    linter = descriptor_linter(file_name, linter_name)
    sarif_builder = regex_output_to_sarif(
        stdout,
        WORKSPACE,
        linter_name,
        linter.get("sarif_text_regex"),
        linter.get("sarif_text_rule_id") or linter_name,
        linter.get("sarif_text_default_level", "error"),
        linter.get("sarif_text_levels"),
    )
    if linter.get("sarif_whole_output"):
        add_whole_output_result(
            sarif_builder, stdout, return_code, linter_name, "error"
        )
    return sarif_builder


def file_uri(path):
    return (
        f"file://{'' if WORKSPACE_URI.startswith('/') else '/'}{WORKSPACE_URI}/{path}"
    )


class DescriptorRegexTest(unittest.TestCase):
    def test_editorconfig_checker(self):
        stdout = (
            "src/a.js:3:0: error: trailing whitespace\n"
            "src/b.js:0:0: error: final newline expected\n\n2 errors found\n"
        )
        self.assertEqual(
            summary(
                convert_with_descriptor(
                    "editorconfig.megalinter-descriptor.yml",
                    "editorconfig-checker",
                    stdout,
                )
            ),
            [
                ("editorconfig-checker", "error", "src/a.js", 3, 1),
                ("editorconfig-checker", "error", "src/b.js", 1, 1),
            ],
        )

    def test_dotenv_linter_with_colors(self):
        stdout = (
            "Checking .env\n"
            "\x1b[1m.env:2\x1b[0m DuplicatedKey: The FOO key is duplicated\n\n"
            "Found 1 problem\n"
        )
        self.assertEqual(
            summary(
                convert_with_descriptor(
                    "env.megalinter-descriptor.yml", "dotenv-linter", stdout
                )
            ),
            [("DuplicatedKey", "error", ".env", 2, None)],
        )

    def test_standard_and_ts_standard(self):
        stdout = (
            "standard: Use JavaScript Standard Style (https://standardjs.com)\n"
            f"  {WORKSPACE_URI}/bad.js:1:5: 'x' is assigned a value but never used. (no-unused-vars)\n"
            f"  {WORKSPACE_URI}/bad.js:1:1: Unexpected var, use let or const instead. (no-var) (warning)\n"
            f"  {WORKSPACE_URI}/broken.js:2:1: Parsing error: Unexpected token (null)\n"
        )
        expected = [
            ("no-unused-vars", "error", "bad.js", 1, 5),
            ("no-var", "warning", "bad.js", 1, 1),
            ("null", "error", "broken.js", 2, 1),
        ]
        for file_name, linter_name in (
            ("javascript.megalinter-descriptor.yml", "standard"),
            ("typescript.megalinter-descriptor.yml", "ts-standard"),
        ):
            self.assertEqual(
                summary(convert_with_descriptor(file_name, linter_name, stdout)),
                expected,
            )

    def test_jsonlint(self):
        stdout = (
            "bad1.json: line 4, col 1, Trailing comma in object.\n"
            'dup.json: line 2, col 4, Duplicate key: "a".\n'
        )
        self.assertEqual(
            summary(
                convert_with_descriptor(
                    "json.megalinter-descriptor.yml", "jsonlint", stdout
                )
            ),
            [
                ("json-syntax", "error", "bad1.json", 4, 1),
                ("json-syntax", "error", "dup.json", 2, 4),
            ],
        )

    def test_chktex(self):
        stdout = (
            "doc.tex:5:7:Warning:1:Command terminated with space.\n"
            "doc.tex:9:1:Error:14:Could not find argument for command.\n"
            "doc.tex:11:2:Message:22:Comment displayed.\n"
        )
        self.assertEqual(
            summary(
                convert_with_descriptor(
                    "latex.megalinter-descriptor.yml", "chktex", stdout
                )
            ),
            [
                ("1", "warning", "doc.tex", 5, 7),
                ("14", "error", "doc.tex", 9, 1),
                ("22", "note", "doc.tex", 11, 2),
            ],
        )

    def test_luacheck(self):
        stdout = (
            "src/a.lua:3:7-9: (W211) unused variable 'x'\n"
            "src/a.lua:1:1: (E011) expected expression near ')'\n"
            "src/b.lua: I/O error (couldn't read: nope)\n"
        )
        results = summary(
            convert_with_descriptor("lua.megalinter-descriptor.yml", "luacheck", stdout)
        )
        self.assertEqual(
            results,
            [
                ("W211", "warning", "src/a.lua", 3, 7),
                ("E011", "error", "src/a.lua", 1, 1),
            ],
        )

    def test_perlcritic(self):
        stdout = (
            "lib/Foo.pm\t12\t5\t5\tSubroutines::ProhibitExplicitReturnUndef\t"
            '"return" statement with explicit "undef"\n'
            "lib/Foo.pm\t20\t1\t3\tNamingConventions::Capitalization\tPackage names\n"
            "lib/Foo.pm\t30\t1\t1\tCodeLayout::RequireTidyCode\tCode is not tidy\n"
            "lib/Bar.pm source OK\n"
        )
        self.assertEqual(
            summary(
                convert_with_descriptor(
                    "perl.megalinter-descriptor.yml", "perlcritic", stdout
                )
            ),
            [
                (
                    "Subroutines::ProhibitExplicitReturnUndef",
                    "error",
                    "lib/Foo.pm",
                    12,
                    5,
                ),
                ("NamingConventions::Capitalization", "warning", "lib/Foo.pm", 20, 1),
                ("CodeLayout::RequireTidyCode", "note", "lib/Foo.pm", 30, 1),
            ],
        )

    def test_raku(self):
        stdout = (
            f"===SORRY!=== Error while compiling {WORKSPACE_URI}/lib/bad.raku\n"
            "Variable '$x' is not declared.  Did you mean '$y'?\n"
            f"at {WORKSPACE_URI}/lib/bad.raku:3\n"
            "------> say <HERE>$x;\n"
        )
        sarif_builder = convert_with_descriptor(
            "raku.megalinter-descriptor.yml", "raku", stdout
        )
        self.assertEqual(
            summary(sarif_builder),
            [("raku-compile-error", "error", "lib/bad.raku", 3, None)],
        )
        self.assertTrue(
            results_of(sarif_builder)[0]["message"]["text"].startswith(
                "Variable '$x' is not declared."
            )
        )

    def test_git_diff_check(self):
        stdout = (
            "src/a.py:12: trailing whitespace.\n"
            "+x = 1   \n"
            "src/b.py:3: leftover conflict marker\n"
            "docs/c.md:40: new blank line at EOF.\n"
        )
        self.assertEqual(
            summary(
                convert_with_descriptor(
                    "repository.megalinter-descriptor.yml", "git_diff", stdout
                )
            ),
            [
                ("whitespace-error", "error", "src/a.py", 12, None),
                ("whitespace-error", "error", "src/b.py", 3, None),
                ("whitespace-error", "error", "docs/c.md", 40, None),
            ],
        )

    def test_ls_lint(self):
        stdout = "src/Foo_Bar.ts failed for `.ts` rules: kebab-case | regex:^[a-z]+$\n"
        sarif_builder = convert_with_descriptor(
            "repository.megalinter-descriptor.yml", "ls-lint", stdout
        )
        self.assertEqual(
            summary(sarif_builder), [("ls-lint", "error", "src/Foo_Bar.ts", None, None)]
        )
        self.assertIn("kebab-case", results_of(sarif_builder)[0]["message"]["text"])

    def test_rstcheck(self):
        stdout = (
            'docs/a.rst:7: (ERROR/3) Unknown directive type "foo".\n'
            "docs/a.rst:9: (WARNING/2) Title underline too short.\n"
            "docs/a.rst:15: (ERROR/3) (python) invalid syntax\n"
            "Error! Issues detected.\n"
        )
        self.assertEqual(
            summary(
                convert_with_descriptor(
                    "rst.megalinter-descriptor.yml", "rstcheck", stdout
                )
            ),
            [
                ("rstcheck", "error", "docs/a.rst", 7, None),
                ("rstcheck", "warning", "docs/a.rst", 9, None),
                ("rstcheck", "error", "docs/a.rst", 15, None),
            ],
        )

    def test_xmllint(self):
        stdout = (
            "bad.xml:4: parser error : Opening and ending tag mismatch: a line 2 and b\n"
            "</b>\n"
            "   ^\n"
            "f.xml:5: Schemas validity error : Element 'foo': This element is not expected.\n"
            "f.xml fails to validate\n"
        )
        results = summary(
            convert_with_descriptor("xml.megalinter-descriptor.yml", "xmllint", stdout)
        )
        self.assertEqual(
            results,
            [
                ("parser", "error", "bad.xml", 4, None),
                ("Schemas validity", "error", "f.xml", 5, None),
            ],
        )

    def test_clang_format_from_the_shared_definition(self):
        stdout = (
            "src/a.c:3:8: error: code should be clang-formatted [-Wclang-format-violations]\n"
            "int  x;\n"
            "       ^\n"
        )
        self.assertEqual(
            summary(
                convert_with_descriptor(
                    "c.megalinter-descriptor.yml", "clang-format", stdout
                )
            ),
            [("-Wclang-format-violations", "error", "src/a.c", 3, 8)],
        )

    def test_terragrunt(self):
        stdout = f"10:00:00.123 ERROR  File '{WORKSPACE_URI}/stack/terragrunt.hcl' needs formatting\n"
        self.assertEqual(
            summary(
                convert_with_descriptor(
                    "terraform.megalinter-descriptor.yml", "terragrunt", stdout
                )
            ),
            [("terragrunt-fmt", "error", "stack/terragrunt.hcl", None, None)],
        )

    def test_nbqa(self):
        stdout = (
            "nb/demo.ipynb:cell_2:3: error: Incompatible types in assignment  [assignment]\n"
            "nb/demo.ipynb:cell_2:3:5: note: See the docs\n"
        )
        sarif_builder = convert_with_descriptor(
            "python.megalinter-descriptor.yml", "nbqa", stdout
        )
        self.assertEqual(
            summary(sarif_builder),
            [
                ("assignment", "error", "nb/demo.ipynb", 3, None),
                ("nbqa", "note", "nb/demo.ipynb", 3, 5),
            ],
        )
        self.assertEqual(
            results_of(sarif_builder)[0]["message"]["text"],
            "cell 2: Incompatible types in assignment",
        )

    def test_cspell_with_context_and_suggestions(self):
        stdout = (
            "README.md:3:12     - Unknown word (exmaple)   -- This is an exmaple of\n"
            "\t Suggestions: [example*, examples]\n"
            "CSpell: Files checked: 1, Issues found: 1 in 1 file.\n"
        )
        sarif_builder = convert_with_descriptor(
            "spell.megalinter-descriptor.yml", "cspell", stdout
        )
        self.assertEqual(
            summary(sarif_builder), [("spelling", "error", "README.md", 3, 12)]
        )
        self.assertEqual(
            results_of(sarif_builder)[0]["message"]["text"], "Unknown word (exmaple)"
        )

    def test_bash_exec(self):
        stdout = "Error: File:[scripts/run.sh] is not executable\n"
        self.assertEqual(
            summary(
                convert_with_descriptor(
                    "bash.megalinter-descriptor.yml", "bash-exec", stdout
                )
            ),
            [("not-executable", "error", "scripts/run.sh", None, None)],
        )

    def test_failure_without_finding_gives_one_result_with_the_output(self):
        sarif_builder = convert_with_descriptor(
            "latex.megalinter-descriptor.yml", "chktex", "chktex: bad config\n", 1
        )
        self.assertEqual(
            summary(sarif_builder), [("chktex", "error", None, None, None)]
        )
        self.assertEqual(
            results_of(sarif_builder)[0]["message"]["text"], "chktex: bad config"
        )

    def test_success_without_finding_gives_no_result(self):
        sarif_builder = convert_with_descriptor(
            "latex.megalinter-descriptor.yml", "chktex", "", 0
        )
        self.assertEqual(results_of(sarif_builder), [])


class JsonConvertersTest(unittest.TestCase):
    def test_gherkin_lint_errors_with_string_lines(self):
        stdout = json.dumps(
            [
                {
                    "filePath": f"{WORKSPACE}/features/a.feature",
                    "errors": [
                        {
                            "message": "Wrong indentation",
                            "rule": "indentation",
                            "line": 7,
                        },
                        {
                            "message": "Multiple features",
                            "rule": "one-feature-per-file",
                            "line": "4",
                        },
                    ],
                },
                {"filePath": f"{WORKSPACE}/features/b.feature", "errors": []},
            ]
        )
        self.assertEqual(
            summary(gherkin_lint_json_to_sarif(stdout, WORKSPACE)),
            [
                ("indentation", "error", "features/a.feature", 7, None),
                ("one-feature-per-file", "error", "features/a.feature", 4, None),
            ],
        )

    def test_v8r_ignores_the_files_without_schema(self):
        stdout = "ℹ Processing ./a.yml\n" + json.dumps(
            {
                "results": [
                    {
                        "fileLocation": "bad.yml",
                        "documentIndex": None,
                        "valid": False,
                        "errors": [
                            {
                                "instancePath": "/num",
                                "keyword": "type",
                                "params": {"type": "integer"},
                                "message": "must be integer",
                            },
                            {
                                "instancePath": "",
                                "keyword": "additionalProperties",
                                "params": {"additionalProperty": "extra"},
                                "message": "must NOT have additional properties",
                            },
                        ],
                    },
                    {"fileLocation": "other.yml", "valid": None, "errors": []},
                    {"fileLocation": "good.yml", "valid": True, "errors": []},
                ]
            }
        )
        sarif_builder = v8r_json_to_sarif(stdout, WORKSPACE)
        self.assertEqual(
            summary(sarif_builder),
            [
                ("type", "error", "bad.yml", None, None),
                ("additionalProperties", "error", "bad.yml", None, None),
            ],
        )
        self.assertIn(
            "found additional property 'extra'",
            results_of(sarif_builder)[1]["message"]["text"],
        )

    def test_kubeconform(self):
        stdout = json.dumps(
            {
                "resources": [
                    {
                        "filename": "deploy.yaml",
                        "kind": "Deployment",
                        "name": "web",
                        "status": "statusInvalid",
                        "msg": "problem",
                        "validationErrors": [
                            {
                                "path": "/spec/replicas",
                                "msg": "got string, want integer",
                            }
                        ],
                    },
                    {
                        "filename": "svc.yaml",
                        "kind": "Service",
                        "name": "api",
                        "status": "statusError",
                        "msg": "could not find schema for Service",
                    },
                    {"filename": "ok.yaml", "status": "statusValid"},
                ],
                "summary": {"valid": 1, "invalid": 1, "errors": 1, "skipped": 0},
            }
        )
        sarif_builder = kubeconform_json_to_sarif(stdout, WORKSPACE)
        self.assertEqual(
            summary(sarif_builder),
            [
                ("invalid-resource", "error", "deploy.yaml", None, None),
                ("validation-error", "error", "svc.yaml", None, None),
            ],
        )
        self.assertEqual(
            results_of(sarif_builder)[0]["message"]["text"],
            "Deployment/web: /spec/replicas got string, want integer",
        )

    def test_php_cs_fixer(self):
        stdout = json.dumps(
            {
                "about": "PHP CS Fixer 3.95.29",
                "files": [
                    {
                        "name": "src/A.php",
                        "appliedFixers": ["no_unused_imports", "single_quote"],
                        "diff": "--- /ws/src/A.php\n+++ /ws/src/A.php\n@@ -3,7 +3,6 @@\n-use X;\n",
                    }
                ],
            }
        )
        self.assertEqual(
            summary(php_cs_fixer_json_to_sarif(stdout, WORKSPACE)),
            [
                ("no_unused_imports", "error", "src/A.php", 3, None),
                ("single_quote", "error", "src/A.php", 3, None),
            ],
        )

    def test_mypy_json_lines(self):
        stdout = (
            "Installing missing stub packages:\n"
            + json.dumps(
                {
                    "file": "src/a.py",
                    "line": 5,
                    "column": 0,
                    "end_line": 5,
                    "end_column": 6,
                    "message": 'Too many arguments for "foo"',
                    "hint": None,
                    "code": "call-arg",
                    "severity": "error",
                }
            )
            + "\n"
            + json.dumps(
                {
                    "file": "src/a.py",
                    "line": 9,
                    "column": -1,
                    "message": "Revealed type is 'int'",
                    "hint": "see docs",
                    "code": None,
                    "severity": "note",
                }
            )
            + "\n"
        )
        sarif_builder = mypy_json_to_sarif(stdout, WORKSPACE)
        self.assertEqual(
            summary(sarif_builder),
            [
                ("call-arg", "error", "src/a.py", 5, 1),
                ("mypy", "note", "src/a.py", 9, None),
            ],
        )
        region = results_of(sarif_builder)[0]["locations"][0]["physicalLocation"][
            "region"
        ]
        self.assertEqual(region["endColumn"], 7)
        self.assertTrue(
            results_of(sarif_builder)[1]["message"]["text"].endswith("see docs")
        )

    def test_pyright(self):
        stdout = json.dumps(
            {
                "version": "1.1.414",
                "generalDiagnostics": [
                    {
                        "file": f"{WORKSPACE}/a.py",
                        "severity": "error",
                        "message": "Argument missing",
                        "range": {
                            "start": {"line": 4, "character": 0},
                            "end": {"line": 4, "character": 6},
                        },
                        "rule": "reportCallIssue",
                    },
                    {
                        "file": f"{WORKSPACE}/a.py",
                        "severity": "information",
                        "message": "Hint",
                    },
                ],
                "summary": {"errorCount": 1},
            }
        )
        sarif_builder = pyright_json_to_sarif(stdout, WORKSPACE)
        self.assertEqual(
            summary(sarif_builder),
            [
                ("reportCallIssue", "error", "a.py", 5, 1),
                ("pyright", "note", "a.py", None, None),
            ],
        )

    def test_rst_lint_one_array_per_file(self):
        stdout = (
            json.dumps(
                [
                    {
                        "line": 2,
                        "source": "docs/a.rst",
                        "level": 2,
                        "type": "WARNING",
                        "message": "Title underline too short.",
                    }
                ]
            )
            + "\n"
            + json.dumps(
                [
                    {
                        "line": None,
                        "source": "docs/b.rst",
                        "level": 3,
                        "type": "ERROR",
                        "message": "Unknown directive",
                    }
                ]
            )
        )
        self.assertEqual(
            summary(rst_lint_json_to_sarif(stdout, WORKSPACE)),
            [
                ("rst-lint", "warning", "docs/a.rst", 2, None),
                ("rst-lint", "error", "docs/b.rst", None, None),
            ],
        )

    def test_tekton_lint_among_logs(self):
        stdout = '{"level":50,"msg":"a log line"}\n' + json.dumps(
            [
                {
                    "message": "Task 'build' is not referenced",
                    "rule": "no-unused-task",
                    "level": "warning",
                    "path": "tekton/task.yaml",
                    "loc": {
                        "range": [120, 135, 136],
                        "startLine": 7,
                        "startColumn": 11,
                        "endLine": 7,
                        "endColumn": 26,
                    },
                },
                {"message": "No name", "rule": "name", "level": "error"},
            ]
        )
        self.assertEqual(
            summary(tekton_lint_json_to_sarif(stdout, WORKSPACE)),
            [
                ("no-unused-task", "warning", "tekton/task.yaml", 7, 11),
                ("name", "error", None, None, None),
            ],
        )

    def test_proselint(self):
        stdout = json.dumps(
            {
                "result": {
                    file_uri("doc.md"): {
                        "diagnostics": [
                            {
                                "check_path": "typography.symbols.ellipsis",
                                "message": "'...' is an approximation",
                                "pos": [3, 14],
                                "span": [57, 60],
                                "replacements": None,
                            }
                        ]
                    },
                    file_uri("broken.md"): {
                        "error": {"code": -31998, "message": "unreadable"}
                    },
                }
            }
        )
        results = {
            rule: rest
            for rule, *rest in summary(proselint_json_to_sarif(stdout, WORKSPACE))
        }
        self.assertEqual(
            results["typography.symbols.ellipsis"], ["error", "doc.md", 3, 14]
        )
        self.assertEqual(results["proselint"], ["error", "broken.md", None, None])

    def test_lychee_errors_and_timeouts(self):
        stdout = json.dumps(
            {
                "total": 3,
                "error_map": {
                    "README.md": [
                        {
                            "url": "https://x/404",
                            "status": {"text": "404 Not Found", "code": 404},
                            "span": {"line": 12, "column": 5},
                        }
                    ]
                },
                "timeout_map": {
                    "docs/a.md": [
                        {
                            "url": "https://slow",
                            "status": {"text": "Timeout", "details": "t"},
                        }
                    ]
                },
            }
        )
        self.assertEqual(
            summary(lychee_json_to_sarif(stdout, WORKSPACE)),
            [
                ("broken-link", "error", "README.md", 12, 5),
                ("link-timeout", "error", "docs/a.md", None, None),
            ],
        )

    def test_tofu_validate_joins_the_module_directory(self):
        output = json.dumps(
            {
                "valid": False,
                "diagnostics": [
                    {
                        "severity": "error",
                        "summary": "Unsupported argument",
                        "detail": 'An argument named "foo" is not expected here.',
                        "range": {
                            "filename": "main.tf",
                            "start": {"line": 3, "column": 3},
                            "end": {"line": 3, "column": 6},
                        },
                    },
                    {"severity": "warning", "summary": "Deprecated"},
                ],
            }
        )
        sarif_builder = tofu_validate_json_to_sarif(
            [("modules/net", "Initializing...\n" + output), ("empty", "Success!")],
            WORKSPACE,
        )
        self.assertEqual(
            summary(sarif_builder),
            [
                ("tofu-validate", "error", "modules/net/main.tf", 3, 3),
                ("tofu-validate", "warning", None, None, None),
            ],
        )
        region = results_of(sarif_builder)[0]["locations"][0]["physicalLocation"][
            "region"
        ]
        self.assertEqual(region["endColumn"], 6)

    def test_arm_ttk(self):
        stdout = json.dumps(
            [
                {
                    "Name": "apiVersions Should Be Recent",
                    "Group": "deploymentTemplate",
                    "Passed": False,
                    "File": f"{WORKSPACE}/azuredeploy.json",
                    "Errors": [
                        {
                            "Message": "Api versions must be the latest",
                            "Id": "x",
                            "Line": 12,
                            "Column": 7,
                        }
                    ],
                    "Warnings": ["Consider a newer version"],
                },
                {
                    "Name": "IDs Should Be Derived",
                    "Passed": True,
                    "File": f"{WORKSPACE}/azuredeploy.json",
                    "Errors": [],
                    "Warnings": [],
                },
            ]
        )
        self.assertEqual(
            summary(arm_ttk_json_to_sarif(stdout, WORKSPACE)),
            [
                ("apiVersions Should Be Recent", "error", "azuredeploy.json", 12, 7),
                (
                    "apiVersions Should Be Recent",
                    "warning",
                    "azuredeploy.json",
                    None,
                    None,
                ),
            ],
        )

    def test_stylua_json_and_parse_errors(self):
        stdout = (
            json.dumps(
                {
                    "file": "src/a.lua",
                    "mismatches": [
                        {
                            "original_start_line": 3,
                            "original_end_line": 4,
                            "expected_start_line": 3,
                            "expected_end_line": 3,
                            "original": "local x  = 1\n",
                            "expected": "local x = 1\n",
                        }
                    ],
                }
            )
            + "\n"
            + json.dumps(
                [
                    {
                        "type": "parse_error",
                        "message": "unexpected token `)`",
                        "filename": "src/b.lua",
                        "location": {
                            "start_line": 2,
                            "start_column": 5,
                            "end_line": 2,
                            "end_column": 6,
                        },
                    }
                ]
            )
        )
        sarif_builder = stylua_json_to_sarif(stdout, WORKSPACE)
        self.assertEqual(
            summary(sarif_builder),
            [
                ("formatting", "error", "src/a.lua", 4, None),
                ("parse-error", "error", "src/b.lua", 2, 5),
            ],
        )


class TextConvertersTest(unittest.TestCase):
    def test_npm_package_json_lint(self):
        stdout = (
            "\n./pkgs/a/package.json\n"
            "ERROR name-format - node: name - name can no longer contain capital letters\n"
            "WARNING require-license - node: license - license is required\n"
            "1 error\n1 warning\n"
        )
        sarif_builder = npm_package_json_lint_to_sarif(stdout, WORKSPACE)
        self.assertEqual(
            summary(sarif_builder),
            [
                ("name-format", "error", "pkgs/a/package.json", None, None),
                ("require-license", "warning", "pkgs/a/package.json", None, None),
            ],
        )
        self.assertTrue(
            results_of(sarif_builder)[0]["message"]["text"].startswith("name: ")
        )

    def test_helm_lint_joins_the_chart(self):
        stdout = (
            "==> Linting charts/web\n"
            "[INFO] Chart.yaml: icon is recommended\n"
            "[ERROR] templates/deployment.yaml: unable to parse YAML: line 12\n"
            "[ERROR] templates/: template: web/templates/svc.yaml:5:12: executing failed\n"
            "\n1 chart(s) linted, 1 chart(s) failed\n"
        )
        self.assertEqual(
            summary(helm_lint_to_sarif(stdout, WORKSPACE)),
            [
                ("helm-lint", "note", "charts/web/Chart.yaml", None, None),
                (
                    "helm-lint",
                    "error",
                    "charts/web/templates/deployment.yaml",
                    None,
                    None,
                ),
                ("helm-lint", "error", "charts/web/templates/", 5, None),
            ],
        )

    def test_snakemake(self):
        stdout = (
            f"Lints for snakefile {WORKSPACE}/Snakefile:\n"
            "    * Tab usage in line 4.:\n"
            "      Use spaces for indentation.\n"
            f"Lints for rule bwa_map (line 12, {WORKSPACE}/Snakefile):\n"
            "    * No log directive defined:\n"
            "      Without a log directive, all output will be printed.\n"
            "      Also see:\n"
            "      https://snakemake.readthedocs.io/\n"
        )
        sarif_builder = snakemake_lint_to_sarif(stdout, WORKSPACE)
        self.assertEqual(
            summary(sarif_builder),
            [
                ("snakemake-lint", "warning", "Snakefile", 4, None),
                ("snakemake-lint", "warning", "Snakefile", 12, None),
            ],
        )
        self.assertEqual(
            results_of(sarif_builder)[1]["message"]["text"],
            "rule bwa_map: No log directive defined",
        )

    def test_scalafix_diff_and_diagnostics(self):
        stdout = (
            f"--- {WORKSPACE_URI}/src/Foo.scala\n"
            "+++ <expected fix>\n"
            "@@ -3,7 +3,6 @@\n"
            "-import a.b\n"
            f"{WORKSPACE_URI}/src/Bar.scala:5: error: [DisableSyntax.var] mutable state should be avoided\n"
            "  var x = 1\n"
            "  ^\n"
        )
        self.assertEqual(
            summary(scalafix_to_sarif(stdout, WORKSPACE)),
            [
                ("scalafix", "error", "src/Foo.scala", 3, None),
                ("DisableSyntax.var", "error", "src/Bar.scala", 5, None),
            ],
        )

    def test_cljstyle_diff_with_the_leading_slash_removed(self):
        stdout = (
            f"--- a/{WORKSPACE_URI.lstrip('/')}/src/core.clj\n"
            f"+++ b/{WORKSPACE_URI.lstrip('/')}/src/core.clj\n"
            "@@ -12,5 +12,5 @@\n"
            "-(defn  foo [])\n"
            "+(defn foo [])\n"
        )
        self.assertEqual(
            summary(cljstyle_diff_to_sarif(stdout, WORKSPACE)),
            [("cljstyle", "error", "src/core.clj", 12, None)],
        )

    def test_unified_diff_with_a_relative_path(self):
        results = unified_diff_to_results(
            "--- a/src/x.clj\n+++ b/src/x.clj\n@@ -1,2 +1,2 @@\n",
            WORKSPACE,
            "error",
            "m",
            "r",
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0].result["locations"][0]["physicalLocation"]["artifactLocation"][
                "uri"
            ],
            "src/x.clj",
        )


class SchemaValidationTest(unittest.TestCase):
    def test_a_log_that_breaks_the_schema_is_reported(self):
        sarif_content = {
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {"driver": {"name": "x"}},
                    "results": [
                        {
                            "ruleId": "r",
                            "level": "critical",
                            "message": {"text": "m"},
                        }
                    ],
                }
            ],
        }
        schema_errors = utilstest.list_sarif_schema_errors(sarif_content)
        self.assertEqual(len(schema_errors), 1)
        self.assertIn("critical", schema_errors[0])


class DiffPrefixTest(unittest.TestCase):
    def test_a_directory_named_a_is_kept_when_the_diff_has_no_git_prefixes(self):
        results = unified_diff_to_results(
            "--- a/src/Foo.scala\n+++ <expected fix>\n@@ -3,7 +3,6 @@\n",
            WORKSPACE,
            "error",
            "m",
            "r",
        )
        self.assertEqual(
            results[0].result["locations"][0]["physicalLocation"]["artifactLocation"][
                "uri"
            ],
            "a/src/Foo.scala",
        )


class CoreHelpersTest(unittest.TestCase):
    def test_find_json_values_returns_every_top_level_value(self):
        values = utils.find_json_values('log [1, 2]\n{"a": [3]}\nnoise [] {"b": 1}')
        self.assertEqual(values, [[1, 2], {"a": [3]}, [], {"b": 1}])

    def test_find_json_values_filters_by_type_and_predicate(self):
        self.assertEqual(
            utils.find_json_values('[1] {"a": 1} {"b": 2}', dict, lambda v: "b" in v),
            [{"b": 2}],
        )

    def test_to_one_based(self):
        self.assertEqual(to_one_based(0, zero_based=True), 1)
        self.assertIsNone(to_one_based(-2))
        self.assertIsNone(to_one_based(0))
        self.assertIsNone(to_one_based(None))
        self.assertIsNone(to_one_based(True))

    def test_file_uri_to_path(self):
        self.assertEqual(file_uri_to_path("file:///tmp/a%20b.md"), "/tmp/a b.md")
        self.assertEqual(file_uri_to_path("file:///C:/ws/a.md"), "C:/ws/a.md")

    def test_whole_output_result_is_not_added_when_a_finding_exists(self):
        run = SarifRunBuilder().init_simple("t")
        run.add_result(SarifResultBuilder().init_simple("error", "m", "R"))
        sarif_builder = SarifBuilder().add_run(run)
        add_whole_output_result(sarif_builder, "boom", 1, "R2")
        self.assertEqual(len(results_of(sarif_builder)), 1)

    def test_cspell_file_names_results_are_remapped(self):
        run = SarifRunBuilder().init_simple("cspell")
        for line in (2, 9):
            run.add_result(
                SarifResultBuilder().init_simple(
                    "error",
                    "Unknown word (exmaple)",
                    "spelling",
                    "abc-megalinter_file_names_cspell.txt",
                    line,
                    1,
                )
            )
        run.add_result(
            SarifResultBuilder().init_simple(
                "error", "m", "spelling", "README.md", 4, 1
            )
        )
        sarif_builder = SarifBuilder().add_run(run)
        remap_file_names_results(
            sarif_builder,
            "abc-megalinter_file_names_cspell.txt",
            [f"{WORKSPACE}/a_file.md", f"{WORKSPACE}/exmaple_file.md"],
            WORKSPACE,
        )
        self.assertEqual(
            [(r[2], r[3]) for r in summary(sarif_builder)],
            [
                ("exmaple_file.md", None),
                ("abc-megalinter_file_names_cspell.txt", 9),
                ("README.md", 4),
            ],
        )
        self.assertTrue(
            results_of(sarif_builder)[0]["message"]["text"].endswith(
                "(in the file name)"
            )
        )


if __name__ == "__main__":
    unittest.main()
