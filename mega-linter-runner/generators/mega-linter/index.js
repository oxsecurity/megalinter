"use strict";
const Generator = require("yeoman-generator");
const chalk = require("chalk");
const yosay = require("yosay");

module.exports = class extends Generator {
  prompting() {
    // Have Yeoman greet the user.
    this.log(
      yosay(
        `Welcome to the ${chalk.red(
          "Mega-Linter"
        )} configuration generator !\n When you don't know, please use default values`
      )
    );

    const prompts = [
      {
        type: "list",
        name: "flavor",
        message: "What is your project type ?",
        default: "all",
        choices: [
          {
            value: "all",
            name: "Let Mega-Linter suggest to me later (recommended)",
          },
          { value: "dart", name: "Dart" },
          { value: "documentation", name: "Documentation" },
          { value: "dotnet", name: "C, C++, C# or Visual Basic.net" },
          { value: "go", name: "Go" },
          { value: "java", name: "Java / Groovy / Kotlin" },
          { value: "javascript", name: "Javascript / Typescript" },
          { value: "php", name: "PHP" },
          { value: "python", name: "Python" },
          { value: "ruby", name: "Ruby" },
          { value: "rust", name: "RUST" },
          { value: "salesforce", name: "Salesforce" },
          { value: "scala", name: "Scala" },
          { value: "swift", name: "Swift" },
          { value: "terraform", name: "Terraform" },
        ],
      },
      {
        type: "list",
        name: "ci",
        message: "What CI/CD system do you use ?",
        default: "gitHubActions",
        choices: [
          { name: "GitHub Actions", value: "gitHubActions" },
          { name: "Jenkins", value: "jenkins" },
          { name: "GitLab CI", value: "gitLabCI" },
          { name: "Azure Pipelines", value: "azure" },
          { name: "Other, I will install workflow manually", value: "other" },
        ],
      },
      {
        type: "confirm",
        name: "copyPaste",
        message: "Do you want to detect abusive copy-pastes ?",
        default: true,
      },
      {
        type: "confirm",
        name: "spellingMistakes",
        message: "Do you want to detect spelling mistakes ?",
        default: true,
      },
      {
        type: "list",
        name: "version",
        message: "Which Mega-Linter version do you want to use ?",
        default: "v5",
        choices: [
          { name: "v5 (Latest official release)", value: "v5" },
          {
            name: "Beta (main branch of Mega-Linter repository)",
            value: "beta",
          },
        ],
      },
      {
        type: "list",
        name: "defaultBranch",
        message: "What is the name of your repository default branch ?",
        default: "main",
        choices: [
          { name: "master", value: "master" },
          { name: "main", value: "main" },
        ],
      },
      {
        type: "list",
        name: "validateAllCodeBase",
        message:
          "Do you want Mega-Linter to validate all source code or only updated one ?",
        default: "all",
        choices: [
          { name: "Validate all sources", value: "all" },
          {
            name: "Validate only sources diff with master/main branch",
            value: "diff",
          },
        ],
      },
      {
        type: "confirm",
        name: "applyFixes",
        message:
          "Do you want to automatically apply formatting and auto-fixes (--fix option of linters) ?",
        default: true,
      },
      {
        type: "confirm",
        name: "fileIoReporter",
        message:
          "Do you want Mega-Linter to upload reports on file.io ? (report is deleted after being downloaded once)",
        default: false,
      },
      {
        type: "confirm",
        name: "elapsedTime",
        message: "Do you want to see elapsed time by linter in logs ?",
        default: true,
      },
    ];

    return this.prompt(prompts).then((props) => {
      this.props = props;
      this._computeValues();
    });
  }

  writing() {
    // Generate workflow config
    this._generateGitHubAction();
    this._generateJenkinsfile();
    this._generateGitLabCi();
    this._generateAzurePipelines();
    if (this.props.ci === "other") {
      this.log(
        "Please follow manual instructions to define CI job at https://megalinter.github.io/installation/"
      );
      this.log(
        "You may call `npx mega-linter-runner` to run Mega-Linter from any system (requires node.js & docker)"
      );
    }
    // Generate .mega-linter.yml config
    this._generateMegaLinterConfig();
    // Generate .cspell.json config
    this._generateCSpellConfig();
    // Generate .jscpd.json config
    this._generateJsCpdConfig();
  }

  end() {
    this.log("You're all set !");
    this.log(
      "Now commit, push and create a pull request to see Mega-Linter catching errors !"
    );
  }

  _computeValues() {
    // Flavor
    if (this.props.flavor === "all") {
      this.gitHubActionName = "megalinter/megalinter";
      this.dockerImageName = "megalinter/megalinter";
    } else {
      this.gitHubActionName =
        "megalinter/megalinter/flavors/" + this.props.flavor;
      this.dockerImageName = "megalinter/megalinter-" + this.props.flavor;
    }
    // Version
    if (this.props.version == "v5") {
      this.gitHubActionVersion = "v5";
      this.dockerImageVersion = "v5";
    } else {
      this.gitHubActionVersion = "beta";
      this.dockerImageVersion = "beta";
    }
    // VALIDATE_ALL_CODE_BASE
    if (this.props.validateAllCodeBase === "all") {
      this.validateAllCodeBaseGha = `true # Set \${{ github.event_name == 'push' && github.ref == 'refs/heads/main' }} to validate only diff with main branch`;
    } else {
      this.validateAllCodeBaseGha = `\${{ github.event_name == 'push' && github.ref == 'refs/heads/main' }} # Validates all source when push on main, else just the git diff with main. Set 'true' if you always want to lint all sources`;
    }
    this.disable = false;
    // COPY PASTES
    if (this.props.copyPaste === true) {
      this.configCopyPaste =
        "# - COPYPASTE # Uncomment to disable checks of abusive copy-pastes";
    } else {
      this.configCopyPaste =
        "- COPYPASTE # Comment to enable checks of abusive copy-pastes";
      this.disable = true;
    }
    // Spelling mistakes
    if (this.props.spellingMistakes === true) {
      this.configSpell =
        "# - SPELL # Uncomment to disable checks of spelling mistakes";
    } else {
      this.configSpell =
        "- SPELL # Comment to enable checks of spelling mistakes";
      this.disable = true;
    }
  }

  _generateGitHubAction() {
    if (this.props.ci !== "gitHubActions") {
      return;
    }
    this.fs.copyTpl(
      this.templatePath("mega-linter.yml"),
      this.destinationPath("./.github/workflows/mega-linter.yml"),
      {
        APPLY_FIXES: this.props.applyFixes === true ? "all" : "none",
        DEFAULT_BRANCH: this.props.defaultBranch,
        GITHUB_ACTION_NAME: this.gitHubActionName,
        GITHUB_ACTION_VERSION: this.gitHubActionVersion,
        VALIDATE_ALL_CODE_BASE_GHA: this.validateAllCodeBaseGha,
      }
    );
  }

  _generateJenkinsfile() {
    if (this.props.ci !== "jenkins") {
      return;
    }
    this.log(
      "Jenkinsfile config generation not implemented yet, please follow manual instructions at https://megalinter.github.io/installation/#jenkins"
    );
  }

  _generateGitLabCi() {
    if (this.props.ci !== "gitLabCI") {
      return;
    }
    this.fs.copyTpl(
      this.templatePath(".gitlab-ci.yml"),
      this.destinationPath(".gitlab-ci.yml"),
      {
        DEFAULT_BRANCH: this.props.defaultBranch,
        DOCKER_IMAGE_NAME: this.dockerImageName,
        DOCKER_IMAGE_VERSION: this.dockerImageVersion,
      }
    );
  }

  _generateAzurePipelines() {
    if (this.props.ci !== "azure") {
      return;
    }
    this.log(
      "Azure pipelines config generation not implemented yet, please follow manual instructions at https://megalinter.github.io/installation/#gitlab"
    );
  }

  _generateMegaLinterConfig() {
    this.fs.copyTpl(
      this.templatePath(".mega-linter.yml"),
      this.destinationPath(".mega-linter.yml"),
      {
        APPLY_FIXES: this.props.applyFixes === true ? "all" : "none",
        DEFAULT_BRANCH: this.props.defaultBranch,
        DISABLE: this.disable === true ? "DISABLE:" : "# DISABLE:",
        COPYPASTE: this.configCopyPaste,
        SPELL: this.configSpell,
        SHOW_ELAPSED_TIME: this.props.elapsedTime === true ? "true" : "false",
        FILEIO_REPORTER: this.props.fileIoReporter === true ? "true" : "false",
      }
    );
  }

  _generateCSpellConfig() {
    if (this.props.spellingMistakes !== true) {
      return;
    }
    this.fs.copyTpl(
      this.templatePath(".cspell.json"),
      this.destinationPath(".cspell.json"),
      {}
    );
  }

  _generateJsCpdConfig() {
    if (this.props.copyPaste !== true) {
      return;
    }
    this.fs.copyTpl(
      this.templatePath(".jscpd.json"),
      this.destinationPath(".jscpd.json"),
      {}
    );
  }
};
