import { asciiArt } from "../../lib/ascii.js";
import Generator from 'yeoman-generator';
import { simpleGit } from 'simple-git';
import c from 'chalk';
import fs from "fs"
import yaml from "js-yaml";

export default class GeneratorMegaLinter extends Generator {
  async prompting() {
    console.log(asciiArt());
    this.log(c.cyan(
      `Welcome to the MegaLinter Custom Flavor generator !
When you don't know what option to select, please use default values`
    ));

    // Verify that the repo name contains "megalinter-custom-flavor"
    const git = simpleGit();
    const remote = await git.getRemotes(true);
    if (!remote[0].refs.fetch.includes("megalinter-custom-flavor")) {
      const errorMessage = `
ERROR: This generator must be run in a repository whose name includes 'megalinter-custom-flavor'
Example: 'megalinter-custom-flavor-python-light'
`
      this.log(c.red(c.bold(errorMessage)));
      throw new Error(errorMessage);
    }
    // Fetch https://raw.githubusercontent.com/megalinter/megalinter/main/megalinter/descriptors/schemas/megalinter-configuration.jsonschema.json
    this.log("Fetching MegaLinter configuration schema...");
    const url = 'https://raw.githubusercontent.com/megalinter/megalinter/main/megalinter/descriptors/schemas/megalinter-configuration.jsonschema.json';
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Failed to fetch schema from ${url}`);
    }
    const schema = await response.json();
    const linterKeys = schema.definitions.enum_linter_keys.enum || [];

    let defaultFlavorLabel = "MyCustomFlavor";
    let defaultSelectedLinters = [];
    if (globalThis.customFlavorLinters) {
      // Check if linters are valid , and crash if there is an invalid linter key
      globalThis.customFlavorLinters.forEach((linter) => {
        if (!linterKeys.includes(linter)) {
          throw new Error(`Invalid linter key: ${linter}`);
        }
      });
      defaultSelectedLinters = globalThis.customFlavorLinters;
    }
    else {
      // Initialize data from existing configuration
      const customFlavorConfigPath = this.destinationPath('megalinter-custom-flavor.yml');
      if (fs.existsSync(customFlavorConfigPath)) {
        const customFlavorConfigContent = fs.readFileSync(customFlavorConfigPath, 'utf8');
        const customFlavorConfig = yaml.load(customFlavorConfigContent);
        if (customFlavorConfig.label) {
          defaultFlavorLabel = customFlavorConfig.label;
        }
        if (customFlavorConfig.linters) {
          defaultSelectedLinters = customFlavorConfig.linters.map((linter) => linter.replace(/^\s*-\s*/, '').trim());
        }
      }
    }

    const prompts = [
      {
        type: 'input',
        name: 'customFlavorLabel',
        message: 'What is the label of your custom flavor?',
        default: defaultFlavorLabel
      },
      {
        type: 'checkbox',
        name: 'selectedLinters',
        message: 'Please select the linters you want to include in your custom flavor:',
        choices: linterKeys,
        default: defaultSelectedLinters
      }
    ];

    return this.prompt(prompts).then(async (props) => {
      this.props = props;
      await this._computeValues();
    });
  }

  writing() {
    this._generateFlavorConfig();
    this._generateGitHubWorkflow();
    this._generateGitHubAction();
    this._generateReadme();
  }

  end() {
    this.log("You're all set !");
    this.log(c.green(
      "Now commit, push then create a GitHub Release to generate your custom flavor !")
    );
  }

  async _computeValues() {
    // Custom flavor label
    this.customFlavorLabel = this.props.customFlavorLabel;
    // Custom flavor selected linters
    this.selectedLinters = this.props.selectedLinters.map((linter) => `  - ${linter}`).join("\n");
    // Check at least one linter is selected
    if (this.selectedLinters.length === 0) {
      throw new Error("You must select at least one linter for your custom flavor");
    }
    this.selectedLintersWithLinks = this.props.selectedLinters.map((linter) => {
      const linterUrl = `https://megalinter.io/latest/descriptors/${linter.toLowerCase()}/`;
      return `  - [${linter}](${linterUrl})`;
    }).join("\n");
    // Custom flavor author is git username
    const git = simpleGit();
    const user = await git.getConfig('user.name');
    this.customFlavorAuthor = user.value;
    // Get remote repo
    const remote = await git.getRemotes(true);
    this.customFlavorRepo = remote[0].refs.fetch.replace('https://github.com/', '').replace('.git', '');
    this.customFlavorRepoUrl = remote[0].refs.fetch.replace('.git', '');
    // Custom flavor docker image version
    this.customFlavorDockerImageVersion = `ghcr.io/${this.customFlavorRepo}/megalinter-custom-flavor:latest`;
  }

  _generateFlavorConfig() {
    this.fs.copyTpl(
      this.templatePath("megalinter-custom-flavor.yml"),
      this.destinationPath(`megalinter-custom-flavor.yml`),
      {
        CUSTOM_FLAVOR_LABEL: this.customFlavorLabel,
        CUSTOM_FLAVOR_LINTERS: this.selectedLinters,
      }
    );
  }

  _generateGitHubWorkflow() {
    this.fs.copyTpl(
      this.templatePath("megalinter-custom-flavor-builder.yml"),
      this.destinationPath("./.github/workflows/megalinter-custom-flavor-builder.yml"),
      {}
    );
  }

  _generateGitHubAction() {
    this.fs.copyTpl(
      this.templatePath("action.yml"),
      this.destinationPath("action.yml"),
      {
        CUSTOM_FLAVOR_LABEL: this.customFlavorLabel,
        CUSTOM_FLAVOR_AUTHOR: this.customFlavorAuthor,
        DOCKER_IMAGE_VERSION: this.customFlavorDockerImageVersion,
      }
    );
  }

  _generateReadme() {
    this.fs.copyTpl(
      this.templatePath("README.md"),
      this.destinationPath("README.md"),
      {
        CUSTOM_FLAVOR_LABEL: this.customFlavorLabel,
        CUSTOM_FLAVOR_LINTERS_WITH_LINKS: this.selectedLintersWithLinks,
        DOCKER_IMAGE_VERSION: this.customFlavorDockerImageVersion,
        CUSTOM_FLAVOR_GITHUB_ACTION: this.customFlavorRepo,
        CUSTOM_FLAVOR_REPO_URL: this.customFlavorRepoUrl,
        CUSTOM_FLAVOR_AUTHOR: this.customFlavorAuthor,
      }
    );
  }

}
