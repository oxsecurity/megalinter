import { asciiArt } from "../../lib/ascii.js";
import Generator from 'yeoman-generator';
import { simpleGit } from 'simple-git';
import { DEFAULT_RELEASE } from "../../lib/config.js";

export default class GeneratorMegaLinter extends Generator {
  async prompting() {
    console.log(asciiArt());
    this.log(
      `Welcome to the MegaLinter Custom Flavor generator !
When you don't know what option to select, please use default values`
    );

    // Fetch https://raw.githubusercontent.com/megalinter/megalinter/main/megalinter/descriptors/schemas/megalinter-configuration.jsonschema.json
    this.log("Fetching MegaLinter configuration schema...");
    const url = 'https://raw.githubusercontent.com/megalinter/megalinter/main/megalinter/descriptors/schemas/megalinter-configuration.jsonschema.json';
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Failed to fetch schema from ${url}`);
    }
    const schema = await response.json();
    const linterKeys = schema.definition.enum_linter_keys.enum || [];

    const prompts = [
      {
        type: 'input',
        name: 'customFlavorLabel',
        message: 'What is the label of your custom flavor?',
        default: 'my-custom-flavor'
      },
      {
        type: 'checkbox',
        name: 'selectedLinters',
        message: 'Please select the linters you want to include in your custom flavor:',
        choices: linterKeys
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
    this.log(
      "Now commit, push and create a pull request to see MegaLinter catching errors !"
    );
  }

  async _computeValues() {
    // Custom flavor label
    this.customFlavorLabel = this.props.customFlavorLabel;
    // Custom flavor selected linters
    this.selectedLinters = this.props.selectedLinters.map((linter) => `  - ${linter}`).join("\n");
    // Custom flavor author is git username
    const git = simpleGit();
    const user = await git.getConfig('user.name');
    this.customFlavorAuthor = user.value;
    // Get remote repo
    const remote = await git.getRemotes(true);
      this.customFlavorRepo = remote[0].refs.fetch;
    // Custom flavor docker image version
    this.customFlavorDockerImageVersion = `ghcr.io/${customFlavorRepo}/megalinter-custom-flavor:latest`;
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
      this.templatePath(".github/wokflows/megalinter-custom-flavor-builder.yml"),
      this.destinationPath("./.github/wokflows/megalinter-custom-flavor-builder.yml"),
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
        CUSTOM_FLAVOR_LINTERS: this.selectedLinters,
        DOCKER_IMAGE_VERSION: this.customFlavorDockerImageVersion,
      }
    );
  }

}
