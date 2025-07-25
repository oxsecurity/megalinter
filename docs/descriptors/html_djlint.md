---
title: djlint configuration in MegaLinter
description: How to use djlint (configure, ignore files, ignore errors, help & version documentations) to analyze HTML files
---
<!-- markdownlint-disable MD033 MD041 -->
<!-- @generated by .automation/build.py, please don't update manually -->

<div align="center">
  <a href="https://djlint.com/" target="blank" title="Visit linter Web Site">
    <img src="https://raw.githubusercontent.com/Riverside-Healthcare/djLint/master/docs/src/static/img/icon.png" alt="djlint" height="150px" class="megalinter-banner">
  </a>
</div>

[![GitHub stars](https://img.shields.io/github/stars/Riverside-Healthcare/djlint?cacheSeconds=3600)](https://github.com/Riverside-Healthcare/djlint) [![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/Riverside-Healthcare/djlint?sort=semver)](https://github.com/Riverside-Healthcare/djlint/releases) [![GitHub last commit](https://img.shields.io/github/last-commit/Riverside-Healthcare/djlint)](https://github.com/Riverside-Healthcare/djlint/commits) [![GitHub commit activity](https://img.shields.io/github/commit-activity/y/Riverside-Healthcare/djlint)](https://github.com/Riverside-Healthcare/djlint/graphs/commit-activity/) [![GitHub contributors](https://img.shields.io/github/contributors/Riverside-Healthcare/djlint)](https://github.com/Riverside-Healthcare/djlint/graphs/contributors/)

**djLint** is a comprehensive linter and formatter for HTML templates that supports multiple template languages. Originally created for use in the Atlas projects, it helps you find common syntax errors and reformat your HTML templates to make them shine.

**Key Features:**

- **Multi-Language Support**: Supports Django, Jinja, Nunjucks, Twig, Handlebars, Mustache, Golang templates, and Angular
- **Comprehensive Rule Set**: 60+ built-in rules covering HTML standards, accessibility, security, and template-specific best practices
- **Language-Specific Rules**: Specialized rules for Django (D-codes), Jinja (J-codes), HTML (H-codes), and general templates (T-codes)
- **Auto-Formatting**: Automatically formats and beautifies HTML templates with consistent indentation and structure
- **Configurable Profiles**: Pre-configured profiles for different template languages with appropriate rule sets
- **Custom Rules**: Support for custom pattern-based and Python module rules for project-specific requirements
- **Flexible Configuration**: Enable/disable rules via command line, configuration files, or inline comments

For example, define `HTML_DJLINT_ARGUMENTS: ["--profile", "django"]` to select django format

## djlint documentation

- Version in MegaLinter: **1.36.4**
- Visit [Official Web Site](https://djlint.com/){target=_blank}
- See [How to configure djlint rules](https://djlint.com/docs/configuration/){target=_blank}
- See [How to disable djlint rules in files](https://djlint.com/docs/ignoring-code/){target=_blank}
- See [Index of problems detected by djlint](https://djlint.com/docs/linter/){target=_blank}

[![djlint - GitHub](https://gh-card.dev/repos/Riverside-Healthcare/djlint.svg?fullname=)](https://github.com/Riverside-Healthcare/djlint){target=_blank}

## Configuration in MegaLinter

- Enable djlint by adding `HTML_DJLINT` in [ENABLE_LINTERS variable](https://megalinter.io/beta/configuration/#activation-and-deactivation)
- Disable djlint by adding `HTML_DJLINT` in [DISABLE_LINTERS variable](https://megalinter.io/beta/configuration/#activation-and-deactivation)

| Variable                                | Description                                                                                                                                                                                                         | Default value       |
|-----------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------|
| HTML_DJLINT_ARGUMENTS                   | User custom arguments to add in linter CLI call<br/>Ex: `-s --foo "bar"`                                                                                                                                            |                     |
| HTML_DJLINT_COMMAND_REMOVE_ARGUMENTS    | User custom arguments to remove from command line before calling the linter<br/>Ex: `-s --foo "bar"`                                                                                                                |                     |
| HTML_DJLINT_FILTER_REGEX_INCLUDE        | Custom regex including filter<br/>Ex: `(src\|lib)`                                                                                                                                                                  | Include every file  |
| HTML_DJLINT_FILTER_REGEX_EXCLUDE        | Custom regex excluding filter<br/>Ex: `(test\|examples)`                                                                                                                                                            | Exclude no file     |
| HTML_DJLINT_CLI_LINT_MODE               | Override default CLI lint mode<br/>- `file`: Calls the linter for each file<br/>- `list_of_files`: Call the linter with the list of files as argument<br/>- `project`: Call the linter from the root of the project | `list_of_files`     |
| HTML_DJLINT_FILE_EXTENSIONS             | Allowed file extensions. `"*"` matches any extension, `""` matches empty extension. Empty list excludes all files<br/>Ex: `[".py", ""]`                                                                             | `[".html", ".htm"]` |
| HTML_DJLINT_FILE_NAMES_REGEX            | File name regex filters. Regular expression list for filtering files by their base names using regex full match. Empty list includes all files<br/>Ex: `["Dockerfile(-.+)?", "Jenkinsfile"]`                        | Include every file  |
| HTML_DJLINT_PRE_COMMANDS                | List of bash commands to run before the linter                                                                                                                                                                      | None                |
| HTML_DJLINT_POST_COMMANDS               | List of bash commands to run after the linter                                                                                                                                                                       | None                |
| HTML_DJLINT_UNSECURED_ENV_VARIABLES     | List of env variables explicitly not filtered before calling HTML_DJLINT and its pre/post commands                                                                                                                  | None                |
| HTML_DJLINT_DISABLE_ERRORS              | Run linter but consider errors as warnings                                                                                                                                                                          | `false`             |
| HTML_DJLINT_DISABLE_ERRORS_IF_LESS_THAN | Maximum number of errors allowed                                                                                                                                                                                    | `0`                 |
| HTML_DJLINT_CLI_EXECUTABLE              | Override CLI executable                                                                                                                                                                                             | `['djlint']`        |

## IDE Integration

Use djlint in your favorite IDE to catch errors before MegaLinter !

|                                                                   <!-- -->                                                                   | IDE                                                  | Extension Name                                                                                  |                                                                               Install                                                                                |
|:--------------------------------------------------------------------------------------------------------------------------------------------:|------------------------------------------------------|-------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/sublime.ico" alt="" height="32px" class="megalinter-icon"></a> | [Sublime Text](https://www.sublimetext.com/)         | [SublimeLinter-contrib-djlint](https://packagecontrol.io/packages/SublimeLinter-contrib-djlint) |                                   [Visit Web Site](https://packagecontrol.io/packages/SublimeLinter-contrib-djlint){target=_blank}                                   |
| <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/vscode.ico" alt="" height="32px" class="megalinter-icon"></a>  | [Visual Studio Code](https://code.visualstudio.com/) | [djlint-vscode](https://marketplace.visualstudio.com/items?itemName=monosans.djlint)            | [![Install in VSCode](https://github.com/oxsecurity/megalinter/raw/main/docs/assets/images/btn_install_vscode.png)](vscode:extension/monosans.djlint){target=_blank} |

## MegaLinter Flavors

This linter is available in the following flavors

|                                                                         <!-- -->                                                                         | Flavor                                                             | Description                                              | Embedded linters |                                                                                                                                                                                                   Info |
|:--------------------------------------------------------------------------------------------------------------------------------------------------------:|:-------------------------------------------------------------------|:---------------------------------------------------------|:----------------:|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/images/mega-linter-square.png" alt="" height="32px" class="megalinter-icon"></a> | [all](https://megalinter.io/beta/supported-linters/)               | Default MegaLinter Flavor                                |       126        |                             ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter) |
|        <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/c_cpp.ico" alt="" height="32px" class="megalinter-icon"></a>        | [c_cpp](https://megalinter.io/beta/flavors/c_cpp/)                 | Optimized for pure C/C++ projects                        |        56        |                 ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-c_cpp/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-c_cpp) |
|       <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/cupcake.ico" alt="" height="32px" class="megalinter-icon"></a>       | [cupcake](https://megalinter.io/beta/flavors/cupcake/)             | MegaLinter for the most commonly used languages          |        87        |             ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-cupcake/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-cupcake) |
|    <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/documentation.ico" alt="" height="32px" class="megalinter-icon"></a>    | [documentation](https://megalinter.io/beta/flavors/documentation/) | MegaLinter for documentation projects                    |        49        | ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-documentation/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-documentation) |
|       <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/dotnet.ico" alt="" height="32px" class="megalinter-icon"></a>        | [dotnet](https://megalinter.io/beta/flavors/dotnet/)               | Optimized for C, C++, C# or VB based projects            |        64        |               ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-dotnet/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-dotnet) |
|      <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/dotnetweb.ico" alt="" height="32px" class="megalinter-icon"></a>      | [dotnetweb](https://megalinter.io/beta/flavors/dotnetweb/)         | Optimized for C, C++, C# or VB based projects with JS/TS |        73        |         ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-dotnetweb/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-dotnetweb) |
|         <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/go.ico" alt="" height="32px" class="megalinter-icon"></a>          | [go](https://megalinter.io/beta/flavors/go/)                       | Optimized for GO based projects                          |        51        |                       ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-go/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-go) |
|        <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/java.ico" alt="" height="32px" class="megalinter-icon"></a>         | [java](https://megalinter.io/beta/flavors/java/)                   | Optimized for JAVA based projects                        |        54        |                   ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-java/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-java) |
|     <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/javascript.ico" alt="" height="32px" class="megalinter-icon"></a>      | [javascript](https://megalinter.io/beta/flavors/javascript/)       | Optimized for JAVASCRIPT or TYPESCRIPT based projects    |        59        |       ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-javascript/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-javascript) |
|         <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/php.ico" alt="" height="32px" class="megalinter-icon"></a>         | [php](https://megalinter.io/beta/flavors/php/)                     | Optimized for PHP based projects                         |        54        |                     ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-php/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-php) |
|       <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/python.ico" alt="" height="32px" class="megalinter-icon"></a>        | [python](https://megalinter.io/beta/flavors/python/)               | Optimized for PYTHON based projects                      |        65        |               ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-python/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-python) |
|        <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/ruby.ico" alt="" height="32px" class="megalinter-icon"></a>         | [ruby](https://megalinter.io/beta/flavors/ruby/)                   | Optimized for RUBY based projects                        |        50        |                   ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-ruby/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-ruby) |
|        <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/rust.ico" alt="" height="32px" class="megalinter-icon"></a>         | [rust](https://megalinter.io/beta/flavors/rust/)                   | Optimized for RUST based projects                        |        50        |                   ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-rust/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-rust) |
|     <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/salesforce.ico" alt="" height="32px" class="megalinter-icon"></a>      | [salesforce](https://megalinter.io/beta/flavors/salesforce/)       | Optimized for Salesforce based projects                  |        54        |       ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-salesforce/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-salesforce) |
|        <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/swift.ico" alt="" height="32px" class="megalinter-icon"></a>        | [swift](https://megalinter.io/beta/flavors/swift/)                 | Optimized for SWIFT based projects                       |        50        |                 ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-swift/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-swift) |
|      <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/terraform.ico" alt="" height="32px" class="megalinter-icon"></a>      | [terraform](https://megalinter.io/beta/flavors/terraform/)         | Optimized for TERRAFORM based projects                   |        54        |         ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-terraform/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-terraform) |

## Behind the scenes

### How are identified applicable files

- File extensions: `.html`, `.htm`

<!-- markdownlint-disable -->
<!-- /* cSpell:disable */ -->
### How the linting is performed

- djlint is called once with the list of files as arguments (`list_of_files` CLI lint mode)

### Example calls

```shell
djlint myfile1.html myfile2.html
```


### Help content

```shell
Usage: djlint [OPTIONS] SRC ...

  djLint · HTML template linter and formatter.

Options:
  --version                       Show the version and exit.
  -e, --extension TEXT            File extension to check [default: html]
  -i, --ignore TEXT               Codes to ignore. ex: "H014,H017"
  --reformat                      Reformat the file(s).
  --check                         Check formatting on the file(s).
  --indent INTEGER                Indent spacing. [default: 4]
  --quiet                         Do not print diff when reformatting.
  --profile TEXT                  Enable defaults by template language. ops:
                                  django, jinja, nunjucks, handlebars, golang,
                                  angular, html [default: html]
  --require-pragma                Only format or lint files that starts with a
                                  comment with the text 'djlint:on'
  --lint                          Lint for common issues. [default option]
  --use-gitignore                 Use .gitignore file to extend excludes.
  --warn                          Return errors as warnings.
  --preserve-leading-space        Attempt to preserve leading space on text.
  --preserve-blank-lines          Attempt to preserve blank lines.
  --format-css                    Also format contents of <style> tags.
  --format-js                     Also format contents of <script> tags.
  --configuration FILE            Path to global configuration file in
                                  djlint.toml or .djlintrc format
  --statistics                    Count the number of occurrences of each
                                  error/warning code.
  --include TEXT                  Codes to include. ex: "H014,H017"
  --ignore-case                   Do not fix case on known html tags.
  --ignore-blocks TEXT            Comma list of template blocks to not indent.
  --blank-line-after-tag TEXT     Add an additional blank line after {% <tag>
                                  ... %} tag groups.
  --blank-line-before-tag TEXT    Add an additional blank line before {% <tag>
                                  ... %} tag groups.
  --line-break-after-multiline-tag
                                  Do not condense the content of multi-line
                                  tags into the line of the last attribute.
  --custom-blocks TEXT            Indent custom template blocks. For example
                                  {% toc %}...{% endtoc %}
  --custom-html TEXT              Indent custom HTML tags. For example <mjml>
  --exclude TEXT                  Override the default exclude paths.
  --extend-exclude TEXT           Add additional paths to the default exclude.
  --linter-output-format TEXT     Customize order of linter output message.
  --max-line-length INTEGER       Max line length. [default: 120]
  --max-attribute-length INTEGER  Max attribute length. [default: 70]
  --format-attribute-template-tags
                                  Attempt to format template syntax inside of
                                  tag attributes.
  --per-file-ignores <TEXT TEXT>...
                                  Ignore linter rules on a per-file basis.
  --indent-css INTEGER            Set CSS indent level.
  --indent-js INTEGER             Set JS indent level.
  --close-void-tags               Add closing mark on known void tags. Ex:
                                  <img> becomse <img />
  --no-line-after-yaml            Do not add a blank line after yaml front
                                  matter.
  --no-function-formatting        Do not attempt to format function contents.
  --no-set-formatting             Do not attempt to format set contents.
  --max-blank-lines INTEGER       Consolidate blank lines down to x lines.
                                  [default: 0]
  -h, --help                      Show this message and exit.
```

### Installation on mega-linter Docker image

- Dockerfile commands :
```dockerfile
# renovate: datasource=pypi depName=djlint
ARG PIP_DJLINT_VERSION=1.36.4
```

- PIP packages (Python):
  - [djlint==1.36.4](https://pypi.org/project/djlint/1.36.4)
