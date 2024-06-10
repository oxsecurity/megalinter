import { default as glob } from "glob-promise";
import { default as fs } from "fs-extra";
import * as path from "path";
import { default as c } from 'chalk';
import prompts from "prompts";
import { OXSecuritySetup } from "./ox-setup.js";
import { asciiArt } from "./ascii.js";
import { DEFAULT_RELEASE } from "./config.js";

export class MegaLinterUpgrader {
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
    name: MegaLinter
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
    name: MegaLinter
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
      // V5 to V6 migration rules
      // GitHub actions
      {
        regex: /actions\/checkout@v2/gm,
        replacement: "actions/checkout@v3",
        test: "uses: actions/checkout@v2",
        testRes: "uses: actions/checkout@v3",
      },
      {
        regex: /actions\/checkout@v3/gm,
        replacement: "actions/checkout@v4",
        test: "uses: actions/checkout@v3",
        testRes: "uses: actions/checkout@v4",
      },
      // Documentation base URL
      {
        regex: /https:\/\/megalinter\.github\.io/gm,
        replacement: "https://oxsecurity.github.io/megalinter",
        test: "https://megalinter.github.io/configuration",
        testRes: "https://oxsecurity.github.io/megalinter/configuration",
      },
      // Github actions flavors
      {
        regex: /megalinter\/megalinter\/flavors\/([a-z]*)@v5\.(.*)/gm,
        replacement: `oxsecurity/megalinter/flavors/$1@${DEFAULT_RELEASE}`,
        test: "megalinter/megalinter/flavors/python@v5.1.2",
        testRes: `oxsecurity/megalinter/flavors/python@${DEFAULT_RELEASE}`,
      },
      {
        regex: /megalinter\/megalinter\/flavors\/([a-z]*)@v5/gm,
        replacement: `oxsecurity/megalinter/flavors/$1@${DEFAULT_RELEASE}`,
        test: "megalinter/megalinter/flavors/python@v5",
        testRes: `oxsecurity/megalinter/flavors/python@${DEFAULT_RELEASE}`,
      },
      {
        regex: /megalinter\/megalinter\/flavors\/([a-z]*)@([a-z]*)/gm,
        replacement: "oxsecurity/megalinter/flavors/$1@$2",
        test: "megalinter/megalinter/flavors/python@alpha",
        testRes: "oxsecurity/megalinter/flavors/python@alpha",
      },
      {
        regex: /megalinter\/megalinter\/flavors\/([a-z]*)/gm,
        replacement: "oxsecurity/megalinter/flavors/$1",
        test: "megalinter/megalinter/flavors/python",
        testRes: "oxsecurity/megalinter/flavors/python",
      },
      // GitHub Action report folder
      {
        regex: /Mega-Linter reports(.*)\n(.*)path:(.*)\n(.*)report(?!s)/gm,
        replacement: "Mega-Linter reports$1\n$2path:$3\n$4megalinter-reports",
        test: `      name: Mega-Linter reports
        path: |
          report`,
        testRes: `      name: Mega-Linter reports
        path: |
          megalinter-reports`,
      },
      // Docker image flavors
      {
        regex: /megalinter\/megalinter-([a-z]*):v5\.(.*)/gm,
        replacement: `oxsecurity/megalinter-$1:${DEFAULT_RELEASE}`,
        test: "megalinter/megalinter-python:v5.1.2",
        testRes: `oxsecurity/megalinter-python:${DEFAULT_RELEASE}`,
      },
      {
        regex: /megalinter\/megalinter-([a-z]*):v5/gm,
        replacement: `oxsecurity/megalinter-$1:${DEFAULT_RELEASE}`,
        test: "megalinter/megalinter-python:v5",
        testRes: `oxsecurity/megalinter-python:${DEFAULT_RELEASE}`,
      },
      {
        regex: /megalinter\/megalinter-([a-z]*):([a-z]*)/gm,
        replacement: "oxsecurity/megalinter-$1:$2",
        test: "megalinter/megalinter-python:alpha",
        testRes: "oxsecurity/megalinter-python:alpha",
      },
      {
        regex: /megalinter\/megalinter-([a-z]*)/gm,
        replacement: "oxsecurity/megalinter-$1",
        test: "megalinter/megalinter-python",
        testRes: "oxsecurity/megalinter-python",
      },
      // Github actions using main flavor
      {
        regex: /megalinter\/megalinter@v5\.(.*)/gm,
        replacement: `oxsecurity/megalinter@${DEFAULT_RELEASE}`,
        test: "megalinter/megalinter@v5.2.4",
        testRes: `oxsecurity/megalinter@${DEFAULT_RELEASE}`,
      },
      {
        regex: /megalinter\/megalinter@v5/gm,
        replacement: `oxsecurity/megalinter@${DEFAULT_RELEASE}`,
        test: "megalinter/megalinter@v5",
        testRes: `oxsecurity/megalinter@${DEFAULT_RELEASE}`,
      },
      {
        regex: /megalinter\/megalinter@([a-z]*)/gm,
        replacement: "oxsecurity/megalinter@$1",
        test: "megalinter/megalinter@alpha",
        testRes: "oxsecurity/megalinter@alpha",
      },
      // Docker images using main flavor
      {
        regex: /megalinter\/megalinter:v5\.(.*)/gm,
        replacement: `oxsecurity/megalinter:${DEFAULT_RELEASE}`,
        test: "megalinter/megalinter:v5.2.4",
        testRes: `oxsecurity/megalinter:${DEFAULT_RELEASE}`,
      },
      {
        regex: /megalinter\/megalinter:v5/gm,
        replacement: `oxsecurity/megalinter:${DEFAULT_RELEASE}`,
        test: "megalinter/megalinter:v5",
        testRes: `oxsecurity/megalinter:${DEFAULT_RELEASE}`,
      },
      {
        regex: /megalinter\/megalinter:([a-z]*)/gm,
        replacement: "oxsecurity/megalinter:$1",
        test: "megalinter/megalinter:alpha",
        testRes: "oxsecurity/megalinter:alpha",
      },
      // V6 to V7 migration rules
      // Documentation base URL
      {
        regex: /https:\/\/oxsecurity\.github\.io\/megalinter/gm,
        replacement: "https://megalinter.io",
        test: "https://oxsecurity.github.io/megalinter/configuration",
        testRes: "https://megalinter.io/configuration",
      },
      {
        regex: /https:\/\/megalinter.io\/configuration/gm,
        replacement: "https://megalinter.io/latest/config-file",
        test: "https://megalinter.io/configuration/",
        testRes: "https://megalinter.io/latest/config-file/",
      },
      {
        regex: /https:\/\/megalinter.io\/config-file/gm,
        replacement: "https://megalinter.io/latest/config-file",
        test: "https://megalinter.io/config-file/",
        testRes: "https://megalinter.io/latest/config-file/",
      },
      {
        regex: /https:\/\/megalinter.io\/flavors/gm,
        replacement: "https://megalinter.io/latest/flavors",
        test: "https://megalinter.io/flavors/",
        testRes: "https://megalinter.io/latest/flavors/",
      },
      // Github actions flavors
      {
        regex: /oxsecurity\/megalinter\/flavors\/([a-z]*)@v6\.(.*)/gm,
        replacement: `oxsecurity/megalinter/flavors/$1@${DEFAULT_RELEASE}`,
        test: "oxsecurity/megalinter/flavors/python@v6.1.2",
        testRes: `oxsecurity/megalinter/flavors/python@${DEFAULT_RELEASE}`,
      },
      {
        regex: /oxsecurity\/megalinter\/flavors\/([a-z]*)@v6/gm,
        replacement: `oxsecurity/megalinter/flavors/$1@${DEFAULT_RELEASE}`,
        test: "oxsecurity/megalinter/flavors/python@v6",
        testRes: `oxsecurity/megalinter/flavors/python@${DEFAULT_RELEASE}`,
      },
      // Docker image flavors
      {
        regex: /oxsecurity\/megalinter-([a-z]*):v6\.(.*)/gm,
        replacement: `oxsecurity/megalinter-$1:${DEFAULT_RELEASE}`,
        test: "oxsecurity/megalinter-python:v6.1.2",
        testRes: `oxsecurity/megalinter-python:${DEFAULT_RELEASE}`,
      },
      {
        regex: /oxsecurity\/megalinter-([a-z]*):v6/gm,
        replacement: `oxsecurity/megalinter-$1:${DEFAULT_RELEASE}`,
        test: "oxsecurity/megalinter-python:v6",
        testRes: `oxsecurity/megalinter-python:${DEFAULT_RELEASE}`,
      },
      // Github actions using main flavor
      {
        regex: /oxsecurity\/megalinter@v6\.(.*)/gm,
        replacement: `oxsecurity/megalinter@${DEFAULT_RELEASE}`,
        test: "oxsecurity/megalinter@v6.2.4",
        testRes: `oxsecurity/megalinter@${DEFAULT_RELEASE}`,
      },
      {
        regex: /oxsecurity\/megalinter@v6/gm,
        replacement: `oxsecurity/megalinter@${DEFAULT_RELEASE}`,
        test: "oxsecurity/megalinter@v6",
        testRes: `oxsecurity/megalinter@${DEFAULT_RELEASE}`,
      },
      // Docker images using main flavor
      {
        regex: /oxsecurity\/megalinter:v6\.(.*)/gm,
        replacement: `oxsecurity/megalinter:${DEFAULT_RELEASE}`,
        test: "oxsecurity/megalinter:v6.2.4",
        testRes: `oxsecurity/megalinter:${DEFAULT_RELEASE}`,
      },
      {
        regex: /oxsecurity\/megalinter:v6/gm,
        replacement: `oxsecurity/megalinter:${DEFAULT_RELEASE}`,
        test: "oxsecurity/megalinter:v6",
        testRes: `oxsecurity/megalinter:${DEFAULT_RELEASE}`,
      },
      // All remaining cases... cross fingers :)
      {
        regex: /megalinter\/megalinter/gm,
        replacement: "oxsecurity/megalinter",
        test: "wesh megalinter/megalinter",
        testRes: "wesh oxsecurity/megalinter",
      },
    ];
  }

  async run() {
    console.log(asciiArt());
    const promptsUpgradeRes = await prompts({
      name: "upgrade",
      message: c.blueBright(
        `This assistant will automatically upgrade your local files so you use MegaLinter ${DEFAULT_RELEASE}\nPlease confirm to proceed :)`
      ),
      type: "confirm",
      initial: true,
    });
    if (promptsUpgradeRes.upgrade === false) {
      console.log(
        `You should upgrade to ${DEFAULT_RELEASE} to benefit from latest versions of linters, and more features :)`
      );
      return;
    }
    // Update local files
    await this.applyReplacements();
    this.manageGitIgnore();
    console.log("");
    console.log(
      c.green("You MegaLinter local configuration files has been updated !")
    );
    console.log(
      c.grey(
        "Now stage and commit updated files then push to see latest version of MegaLinter in action !"
      )
    );
    console.log("");
    // Propose to try ox service
    const promptsOXRes = await prompts({
      name: "ox",
      message: c.blueBright(
        `MegaLinter is now part of ${c.green(
          "OX Security"
        )}. -> https://www.ox.security/?ref=megalinter\n\nDo you want to try OX Security to secure your software supply chain security ?`
      ),
      type: "confirm",
      initial: true,
    });
    if (promptsOXRes.ox === true) {
      new OXSecuritySetup().run();
    }
  }

  async applyReplacements() {
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

  // Create or update .gitignore files
  manageGitIgnore() {
    const gitIgnoreFile = path.join(process.cwd(), ".gitignore");
    let gitIgnoreTextLines = [];
    let doWrite = false;
    if (fs.existsSync(gitIgnoreFile)) {
      gitIgnoreTextLines = fs
        .readFileSync(gitIgnoreFile, "utf8")
        .split(/\r?\n/);
    }
    if (!gitIgnoreTextLines.includes("megalinter-reports/")) {
      gitIgnoreTextLines.push("megalinter-reports/");
      doWrite = true;
    }
    if (doWrite) {
      fs.writeFileSync(gitIgnoreFile, gitIgnoreTextLines.join("\n") + "\n");
      console.log(
        "Updated .gitignore file to exclude megalinter-reports from commits"
      );
    }
  }
}

