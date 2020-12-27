'use strict';
const Generator = require('yeoman-generator');
const chalk = require('chalk');
const yosay = require('yosay');

module.exports = class extends Generator {
  prompting() {
    // Have Yeoman greet the user.
    this.log(
      yosay(`Welcome to the ${chalk.red('Mega-Linter')} configuration generator !\n When you don't know, please use default values`)
    );

    const prompts = [
      {
        type: 'list',
        name: 'flavor',
        message: 'What is your project type ?',
        default: "all",
        choices: [
          { value: "all", name: "Let Mega-Linter suggest me later" },
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
          { value: "scala", name: "Scala" },
          { value: "salesforce", name: "Salesforce" },
          { value: "terraform", name: "Terraform" },
        ]
      },
      {
        type: 'list',
        name: 'ci',
        message: 'What CI/CD system do you use ?',
        default: "gitHubActions",
        choices: [
          { name: "GitHub Actions", value: "gitHubActions" },
          { name: "Jenkins", value: "jenkins" },
          { name: "GitLab CI", value: "gitLabCI" },
          { name: "Azure Pipelines", value: "azure" },
          { name: "Other, I will install workflow manually", value: "other" }
        ]
      },
      {
        type: 'confirm',
        name: 'copyPaste',
        message: 'Do you want to detect abusive copy-pastes ?',
        default: true
      },
      {
        type: 'confirm',
        name: 'spellingMistakes',
        message: 'Do you want to detect spelling mistakes ?',
        default: true
      },
      {
        type: 'list',
        name: 'version',
        message: 'Which Mega-Linter version do you want to use ?',
        default: "v4",
        choices: [
          { name: "V4 (Latest stable version)", value: "v4" },
          { name: "Insiders (master branch of Mega-Linter repository)", value: "insiders" },
        ]
      },
      {
        type: 'list',
        name: 'defaultBranch',
        message: 'What is the name of your repository default branch ?',
        default: "master",
        choices: [
          { name: "master", value: "master" },
          { name: "main", value: "main" },
        ]
      },
      {
        type: 'list',
        name: 'validateAllCodeBase',
        message: 'Do you want Mega-Linter to validate all source code or only updated one ?',
        default: "all",
        choices: [
          { name: "Validate all sources", value: "all" },
          { name: "Validate only sources diff with master/main branch", value: "diff" },
        ]
      },
      {
        type: 'confirm',
        name: 'applyFixes',
        message: 'Do you want to automatically apply formatting and auto-fixes (--fix option of linters) ?',
        default: true
      },
      {
        type: 'confirm',
        name: 'fileIoReporter',
        message: 'Do you want Mega-Linter to upload reports on file.io ? (report is deleted after being downloaded once)',
        default: false
      },
      {
        type: 'confirm',
        name: 'elapsedTime',
        message: 'Do you want to see elapsed time by linter in logs ?',
        default: true
      },
    ];

    return this.prompt(prompts).then(props => {
      this.props = props;
      this.computeValues()
    });
  }

  computeValues() {
    // Flavor
    if (this.props.flavor === 'all') {
      this.gitHubActionName = "nvuillam/mega-linter"
      this.dockerImageName = "nvuillam/mega-linter"
    }
    else {
      this.gitHubActionName = "nvuillam/mega-linter/flavors/" + this.props.flavor
      this.dockerImageName = "nvuillam/mega-linter-" + this.props.flavor
    }
    // Version
    if (this.props.version == 'v4') {
      this.gitHubActionVersion = "v4"
      this.dockerImageVersion = "v4"
    }
    else {
      this.gitHubActionVersion = "insiders"
      this.dockerImageVersion = "latest"
    }
    // VALIDATE_ALL_CODE_BASE
    if (this.props.validateAllCodeBase === "all") {
      this.validateAllCodeBaseGha = `true # Set \${{ github.event_name == 'push' && github.ref == 'refs/heads/master' }} to validate only diff with master branch`
    }
    else {
      this.validateAllCodeBaseGha = `\${{ github.event_name == 'push' && github.ref == 'refs/heads/master' }} # Validates all source when push on master, else just the git diff with master. Set 'true' if you always want to lint all sources`
    }
    // COPY PASTES
    if (this.props.copyPaste === true) {
      this.configCopyPaste = "# - COPYPASTE # Uncomment to enable checks of abusive copy-pastes"
    }
    else {
      this.configCopyPaste = "- COPYPASTE # Comment to disable checks of abusive copy-pastes"
    }
    // COPY PASTES
    if (this.props.spellingMistakes === true) {
      this.configSpell = "# - SPELL # Uncomment to enable checks of spelling mistakes"
    }
    else {
      this.configSpell = "- SPELL # Comment to disable checks of spelling mistakes"
    }
  }

  writing() {
    // Generate workflow config
    this.generateGitHubAction();
    this.generateJenkinsfile();
    this.generateGitLabCi();
    this.generateAzurePipelines();
    if (this.props.ci === 'other') {
      this.log("Please follow manual instructions to define CI job at https://nvuillam.github.io/mega-linter/installation/");
    }
    // Generate .mega-linter.yml config
    this.generateMegaLinterConfig();
  }

  generateGitHubAction() {
    if (this.props.ci !== "gitHubActions") {
      return;
    }
    this.fs.copyTpl(
      this.templatePath('mega-linter.yml'),
      this.destinationPath('./.github/workflows/mega-linter.yml'),
      {
        'APPLY_FIXES': this.props.applyFixes === true ? 'all' : 'none',
        'DEFAULT_BRANCH': this.props.defaultBranch,
        'GITHUB_ACTION_NAME': this.gitHubActionName,
        'GITHUB_ACTION_VERSION': this.gitHubActionVersion,
        'VALIDATE_ALL_CODE_BASE_GHA': this.validateAllCodeBaseGha
      }
    );
  }

  generateJenkinsfile() {
    if (this.props.ci !== "jenkins") {
      return;
    }
    this.log("Jenkinsfile config generation not implemented yet, please follow manual instructions at https://nvuillam.github.io/mega-linter/installation/#jenkins")
  }

  generateGitLabCi() { 
    if (this.props.ci !== "gitLabCI") {
      return;
    }
    this.log("GitLab CI config generation not implemented yet, please follow manual instructions at https://nvuillam.github.io/mega-linter/installation/#gitlab")
  }

  generateAzurePipelines() {
    if (this.props.ci !== "azure") {
      return;
    }
    this.log("Azure pipelines config generation not implemented yet, please follow manual instructions at https://nvuillam.github.io/mega-linter/installation/#gitlab")
  }

  generateMegaLinterConfig() {
    this.fs.copyTpl(
      this.templatePath('.mega-linter.yml'),
      this.destinationPath('.mega-linter.yml'),
      {
        'APPLY_FIXES': this.props.applyFixes === true ? 'all' : 'none',
        'DEFAULT_BRANCH': this.props.defaultBranch,
        'COPYPASTE': this.configCopyPaste,
        'SPELL': this.configSpell,
        'SHOW_ELAPSED_TIME': (this.props.elapsedTime === true) ? 'true': 'false',
        'FILEIO_REPORTER': (this.props.fileIoReporter === true) ? 'true': 'false'
      }
    );
  }

};
