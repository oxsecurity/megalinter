#! /usr/bin/env node
"use strict";
const glob = require("glob-promise");
const fs = require("fs-extra");
const c = require("chalk");

class MegaLinterUpgrader {
  constructor() {
    this.replacements = [
      // Documentation base URL
      {
        regex: /https:\/\/nvuillam\.github\.io\/mega-linter/gm,
        replacement: "https://megalinter.github.io",
        test: "https://nvuillam.github.io/mega-linter/configuration",
        testRes: "https://megalinter.github.io/configuration",
      },
      // Github actions flavors
      {
        regex: /nvuillam\/mega-linter\/flavors\/([a-z]*)@latest/gm,
        replacement: "megalinter/megalinter/flavors/$1@beta",
        test: "nvuillam/mega-linter/flavors/python@latest",
        testRes: "megalinter/megalinter/flavors/python@beta",
      },
      {
        regex: /nvuillam\/mega-linter\/flavors\/([a-z]*)@insiders/gm,
        replacement: "megalinter/megalinter/flavors/$1@beta",
        test: "nvuillam/mega-linter/flavors/python@insiders",
        testRes: "megalinter/megalinter/flavors/python@beta",
      },
      {
        regex: /nvuillam\/mega-linter\/flavors\/([a-z]*)@v4\.(.*)/gm,
        replacement: "megalinter/megalinter/flavors/$1@v5",
        test: "nvuillam/mega-linter/flavors/python@v4.1.2",
        testRes: "megalinter/megalinter/flavors/python@v5",
      },
      {
        regex: /nvuillam\/mega-linter\/flavors\/([a-z]*)@v4/gm,
        replacement: "megalinter/megalinter/flavors/$1@v5",
        test: "nvuillam/mega-linter/flavors/python@v4",
        testRes: "megalinter/megalinter/flavors/python@v5",
      },
      {
        regex: /nvuillam\/mega-linter\/flavors\/([a-z]*)@([a-z]*)/gm,
        replacement: "megalinter/megalinter/flavors/$1@$2",
        test: "nvuillam/mega-linter/flavors/python@alpha",
        testRes: "megalinter/megalinter/flavors/python@alpha",
      },
      {
        regex: /nvuillam\/mega-linter\/flavors\/([a-z]*)/gm,
        replacement: "megalinter/megalinter/flavors/$1",
        test: "nvuillam/mega-linter/flavors/python",
        testRes: "megalinter/megalinter/flavors/python",
      },
      // Docker image flavors
      {
        regex: /nvuillam\/mega-linter-([a-z]*):latest/gm,
        replacement: "megalinter/megalinter-$1:beta",
        test: "nvuillam/mega-linter-python:latest",
        testRes: "megalinter/megalinter-python:beta",
      },
      {
        regex: /nvuillam\/mega-linter-([a-z]*):insiders/gm,
        replacement: "megalinter/megalinter-$1:beta",
        test: "nvuillam/mega-linter-python:insiders",
        testRes: "megalinter/megalinter-python:beta",
      },
      {
        regex: /nvuillam\/mega-linter-([a-z]*):v4\.(.*)/gm,
        replacement: "megalinter/megalinter-$1:v5",
        test: "nvuillam/mega-linter-python:v4.1.2",
        testRes: "megalinter/megalinter-python:v5",
      },
      {
        regex: /nvuillam\/mega-linter-([a-z]*):v4/gm,
        replacement: "megalinter/megalinter-$1:v5",
        test: "nvuillam/mega-linter-python:v4",
        testRes: "megalinter/megalinter-python:v5",
      },
      {
        regex: /nvuillam\/mega-linter-([a-z]*):([a-z]*)/gm,
        replacement: "megalinter/megalinter-$1:$2",
        test: "nvuillam/mega-linter-python:alpha",
        testRes: "megalinter/megalinter-python:alpha",
      },
      {
        regex: /nvuillam\/mega-linter-([a-z]*)/gm,
        replacement: "megalinter/megalinter-$1",
        test: "nvuillam/mega-linter-python",
        testRes: "megalinter/megalinter-python",
      },
      // Github actions using main flavor
      {
        regex: /nvuillam\/mega-linter@insiders/gm,
        replacement: "megalinter/megalinter@beta",
        test: "nvuillam/mega-linter@insiders",
        testRes: "megalinter/megalinter@beta",
      },
      {
        regex: /nvuillam\/mega-linter@latest/gm,
        replacement: "megalinter/megalinter@beta",
        test: "nvuillam/mega-linter@latest",
        testRes: "megalinter/megalinter@beta",
      },
      {
        regex: /nvuillam\/mega-linter@v4\.(.*)/gm,
        replacement: "megalinter/megalinter@v5",
        test: "nvuillam/mega-linter@v4.2.4",
        testRes: "megalinter/megalinter@v5",
      },
      {
        regex: /nvuillam\/mega-linter@v4/gm,
        replacement: "megalinter/megalinter@v5",
        test: "nvuillam/mega-linter@v4",
        testRes: "megalinter/megalinter@v5",
      },
      {
        regex: /nvuillam\/mega-linter@([a-z]*)/gm,
        replacement: "megalinter/megalinter@$1",
        test: "nvuillam/mega-linter@alpha",
        testRes: "megalinter/megalinter@alpha",
      },
      // Docker images using main flavor
      {
        regex: /nvuillam\/mega-linter:insiders/gm,
        replacement: "megalinter/megalinter:beta",
        test: "nvuillam/mega-linter:insiders",
        testRes: "megalinter/megalinter:beta",
      },
      {
        regex: /nvuillam\/mega-linter:latest/gm,
        replacement: "megalinter/megalinter:beta",
        test: "nvuillam/mega-linter:latest",
        testRes: "megalinter/megalinter:beta",
      },
      {
        regex: /nvuillam\/mega-linter:v4\.(.*)/gm,
        replacement: "megalinter/megalinter:v5",
        test: "nvuillam/mega-linter:v4.2.4",
        testRes: "megalinter/megalinter:v5",
      },
      {
        regex: /nvuillam\/mega-linter:v4/gm,
        replacement: "megalinter/megalinter:v5",
        test: "nvuillam/mega-linter:v4",
        testRes: "megalinter/megalinter:v5",
      },
      {
        regex: /nvuillam\/mega-linter:([a-z]*)/gm,
        replacement: "megalinter/megalinter:$1",
        test: "nvuillam/mega-linter:alpha",
        testRes: "megalinter/megalinter:alpha",
      },
      // All remaining cases... cross fingers :)
      {
        regex: /nvuillam\/mega-linter/gm,
        replacement: "megalinter/megalinter",
        test: "wesh nvuillam/mega-linter",
        testRes: "wesh megalinter/megalinter",
      },
      // Cancellation of duplicate runs
      // Job "cancel_duplicate"
      {
        regex:
          /(?<prev_jobs>jobs\s*:(?:.|\n)*)\n(?<indent> *)cancel_duplicates\s*:(?:.|\n)*?\n(?<next_job_key>\k<indent>\S*\s*:)/gim,
        replacement: `concurrency:
  group: \${{ github.ref }}-\${{ github.workflow }}
  cancel-in-progress: true

$<prev_jobs>
$<next_job_key>`,
        test: `
jobs:
  preceding_job:
    # ..

  # Cancel duplicate jobs: https://github.com/fkirc/skip-duplicate-actions#option-3-cancellation-only
  cancel_duplicates:
    name: Cancel duplicate jobs
    runs-on: ubuntu-latest
    steps:
      - uses: fkirc/skip-duplicate-actions@master
        with:
          github_token: \${{ secrets.PAT || secrets.GITHUB_TOKEN }}
          cancel_others: true

  intermediate_job:
    # ..

  build:
    name: Mega-Linter
`,
        testRes: `
concurrency:
  group: \${{ github.ref }}-\${{ github.workflow }}
  cancel-in-progress: true

jobs:
  preceding_job:
    # ..

  # Cancel duplicate jobs: https://github.com/fkirc/skip-duplicate-actions#option-3-cancellation-only
  intermediate_job:
    # ..

  build:
    name: Mega-Linter
`,
      },
      // Comment "# Cancel duplicate jobs: https://github.com/fkirc/..."
      {
        regex: /^\s*#\s*cancel\s*duplicate.*\n/gim,
        replacement: "",
        test: `
jobs:
  # Cancel duplicate jobs: https://github.com/fkirc/skip-duplicate-actions#option-3-cancellation-only
  build:
`,
        testRes: `
jobs:
  build:
`,
      },
    ];
  }

  async run() {
    // List yaml and shell files
    const globPattern1 = process.cwd() + `/**/*.{yaml,yml,sh,bash}`;
    const files1 = await glob(globPattern1, { cwd: process.cwd(), dot: true });
    // List Jenkinsfile
    const globPattern2 = process.cwd() + `/**/Jenkinsfile`;
    const files2 = await glob(globPattern2, { cwd: process.cwd(), dot: true });

    // Analyze all files and make appropriate replacements
    const allFiles = files1.concat(files2);
    let appliedReplacements = 0;
    let updatedFiles = 0;
    for (const file of allFiles) {
      console.log(c.grey("Processing file " + file));
      const initialFileContent = await fs.readFile(file, "utf8");
      let updatedFileContent = initialFileContent.slice();
      for (const replacementItem of this.replacements) {
        const newFileContent = updatedFileContent.replace(
          replacementItem.regex,
          replacementItem.replacement
        );
        if (newFileContent !== updatedFileContent) {
          console.log(
            `- Updating ${file} with replacement ${replacementItem.regex} -> ${replacementItem.replacement} ...`
          );
          updatedFileContent = newFileContent;
          appliedReplacements++;
        }
      }
      if (updatedFileContent !== initialFileContent) {
        await fs.writeFile(file, updatedFileContent);
        console.log(c.cyan(`UPDATED: ${file}`));
        updatedFiles++;
      }
    }
    console.log(
      c.bold(
        `mega-linter-runner applied ${c.green(
          appliedReplacements
        )} replacements in ${c.green(updatedFiles)} files.`
      )
    );
  }
}

module.exports = { MegaLinterUpgrader };
