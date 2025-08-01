---
title: eslint configuration in MegaLinter
description: How to use eslint (configure, ignore files, ignore errors, help & version documentations) to analyze TSX files
---
<!-- markdownlint-disable MD033 MD041 -->
<!-- @generated by .automation/build.py, please don't update manually -->

<div align="center">
  <a href="https://github.com/jsx-eslint/eslint-plugin-react#readme" target="blank" title="Visit linter Web Site">
    <img src="https://d33wubrfki0l68.cloudfront.net/3b5ac7586466159bb6f237b633bfc4f5a8d5acf8/ee0a1/assets/img/posts/eslint-collective.png" alt="eslint" height="150px" class="megalinter-banner">
  </a>
</div>

[![GitHub stars](https://img.shields.io/github/stars/jsx-eslint/eslint-plugin-react?cacheSeconds=3600)](https://github.com/jsx-eslint/eslint-plugin-react) ![autofix](https://shields.io/badge/-autofix-green) ![sarif](https://shields.io/badge/-SARIF-orange) [![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/jsx-eslint/eslint-plugin-react?sort=semver)](https://github.com/jsx-eslint/eslint-plugin-react/releases) [![GitHub last commit](https://img.shields.io/github/last-commit/jsx-eslint/eslint-plugin-react)](https://github.com/jsx-eslint/eslint-plugin-react/commits) [![GitHub commit activity](https://img.shields.io/github/commit-activity/y/jsx-eslint/eslint-plugin-react)](https://github.com/jsx-eslint/eslint-plugin-react/graphs/commit-activity/) [![GitHub contributors](https://img.shields.io/github/contributors/jsx-eslint/eslint-plugin-react)](https://github.com/jsx-eslint/eslint-plugin-react/graphs/contributors/)

**ESLint with React Plugin** provides comprehensive linting for TSX (TypeScript React) files, combining ESLint's powerful static analysis with React-specific rules to ensure high-quality React applications written in TypeScript.

**Key Features:**

- **React-Specific Linting**: 90+ rules covering React best practices, hooks usage, JSX syntax, and component lifecycle patterns
- **TypeScript Integration**: Full TypeScript support for type-aware linting in React components with proper TSX syntax validation
- **Hooks Rules**: Comprehensive validation of React Hooks usage patterns, dependencies, and effect cleanup
- **Accessibility Integration**: Built-in support for jsx-a11y plugin ensuring accessible React components
- **Performance Optimization**: Rules to detect unnecessary re-renders, missing dependency arrays, and performance anti-patterns
- **Modern React Patterns**: Support for latest React features including Suspense, Error Boundaries, and concurrent features

ESLint requires a custom configuration file applicable to your project. You can create it by typing `npx eslint --init` in the root of your repository

## eslint documentation

- Version in MegaLinter: **8.57.1**
- Visit [Official Web Site](https://github.com/jsx-eslint/eslint-plugin-react#readme){target=_blank}
- See [How to configure eslint rules](https://github.com/jsx-eslint/eslint-plugin-react#configuration-legacy-eslintrc){target=_blank}
- See [How to disable eslint rules in files](https://eslint.org/docs/latest/use/configure/rules#disabling-rules){target=_blank}
- See [How to ignore files and directories with eslint](https://eslint.org/docs/latest/use/configure/ignore#the-eslintignore-file){target=_blank}
  - You can define a `.eslintignore` file to ignore files and folders
- See [Index of problems detected by eslint](https://github.com/jsx-eslint/eslint-plugin-react#list-of-supported-rules){target=_blank}

[![eslint-plugin-react - GitHub](https://gh-card.dev/repos/jsx-eslint/eslint-plugin-react.svg?fullname=)](https://github.com/jsx-eslint/eslint-plugin-react){target=_blank}

## Configuration in MegaLinter

- Enable eslint by adding `TSX_ESLINT` in [ENABLE_LINTERS variable](https://megalinter.io/beta/configuration/#activation-and-deactivation)
- Disable eslint by adding `TSX_ESLINT` in [DISABLE_LINTERS variable](https://megalinter.io/beta/configuration/#activation-and-deactivation)

- Enable **autofixes** by adding `TSX_ESLINT` in [APPLY_FIXES variable](https://megalinter.io/beta/configuration/#apply-fixes)

| Variable                               | Description                                                                                                                                                                                                         | Default value                                   |
|----------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------|
| TSX_ESLINT_ARGUMENTS                   | User custom arguments to add in linter CLI call<br/>Ex: `-s --foo "bar"`                                                                                                                                            |                                                 |
| TSX_ESLINT_COMMAND_REMOVE_ARGUMENTS    | User custom arguments to remove from command line before calling the linter<br/>Ex: `-s --foo "bar"`                                                                                                                |                                                 |
| TSX_ESLINT_FILTER_REGEX_INCLUDE        | Custom regex including filter<br/>Ex: `(src\|lib)`                                                                                                                                                                  | Include every file                              |
| TSX_ESLINT_FILTER_REGEX_EXCLUDE        | Custom regex excluding filter<br/>Ex: `(test\|examples)`                                                                                                                                                            | Exclude no file                                 |
| TSX_ESLINT_CLI_LINT_MODE               | Override default CLI lint mode<br/>- `file`: Calls the linter for each file<br/>- `list_of_files`: Call the linter with the list of files as argument<br/>- `project`: Call the linter from the root of the project | `list_of_files`                                 |
| TSX_ESLINT_FILE_EXTENSIONS             | Allowed file extensions. `"*"` matches any extension, `""` matches empty extension. Empty list excludes all files<br/>Ex: `[".py", ""]`                                                                             | `[".tsx"]`                                      |
| TSX_ESLINT_FILE_NAMES_REGEX            | File name regex filters. Regular expression list for filtering files by their base names using regex full match. Empty list includes all files<br/>Ex: `["Dockerfile(-.+)?", "Jenkinsfile"]`                        | Include every file                              |
| TSX_ESLINT_PRE_COMMANDS                | List of bash commands to run before the linter                                                                                                                                                                      | None                                            |
| TSX_ESLINT_POST_COMMANDS               | List of bash commands to run after the linter                                                                                                                                                                       | None                                            |
| TSX_ESLINT_UNSECURED_ENV_VARIABLES     | List of env variables explicitly not filtered before calling TSX_ESLINT and its pre/post commands                                                                                                                   | None                                            |
| TSX_ESLINT_CONFIG_FILE                 | eslint configuration file name</br>Use `LINTER_DEFAULT` to let the linter find it                                                                                                                                   | `.eslintrc.json`                                |
| TSX_ESLINT_RULES_PATH                  | Path where to find linter configuration file                                                                                                                                                                        | Workspace folder, then MegaLinter default rules |
| TSX_ESLINT_DISABLE_ERRORS              | Run linter but consider errors as warnings                                                                                                                                                                          | `false`                                         |
| TSX_ESLINT_DISABLE_ERRORS_IF_LESS_THAN | Maximum number of errors allowed                                                                                                                                                                                    | `0`                                             |
| TSX_ESLINT_CLI_EXECUTABLE              | Override CLI executable                                                                                                                                                                                             | `['eslint']`                                    |

## IDE Integration

Use eslint in your favorite IDE to catch errors before MegaLinter !

|                                                                   <!-- -->                                                                    | IDE                                                      | Extension Name                                                                                 |                                                                                   Install                                                                                   |
|:---------------------------------------------------------------------------------------------------------------------------------------------:|----------------------------------------------------------|------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/brackets.ico" alt="" height="32px" class="megalinter-icon"></a> | [Brackets](https://brackets.io/)                         | [brackets-eslint](https://github.com/brackets-userland/brackets-eslint)                        |                                            [Visit Web Site](https://github.com/brackets-userland/brackets-eslint){target=_blank}                                            |
| <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/eclipse.ico" alt="" height="32px" class="megalinter-icon"></a>  | [Eclipse](https://www.eclipse.org/)                      | [Tern-Linter-ESLint](https://github.com/angelozerr/tern.java/wiki/Tern-Linter-ESLint)          |                                      [Visit Web Site](https://github.com/angelozerr/tern.java/wiki/Tern-Linter-ESLint){target=_blank}                                       |
|  <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/emacs.ico" alt="" height="32px" class="megalinter-icon"></a>   | [Emacs](https://www.gnu.org/software/emacs/)             | [flycheck](http://www.flycheck.org/en/latest/languages.html#javascript)                        |                                        [Visit Web Site](http://www.flycheck.org/en/latest/languages.html#javascript){target=_blank}                                         |
|   <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/idea.ico" alt="" height="32px" class="megalinter-icon"></a>   | [IDEA](https://www.jetbrains.com/products.html#type=ide) | [ESLint Plugin](https://plugins.jetbrains.com/plugin/7494-eslint)                              |                        <iframe frameborder="none" width="245px" height="48px" src="https://plugins.jetbrains.com/embeddable/install/7494"></iframe>                         |
| <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/sublime.ico" alt="" height="32px" class="megalinter-icon"></a>  | [Sublime Text](https://www.sublimetext.com/)             | [SublimeLinter-eslint](https://github.com/roadhump/SublimeLinter-eslint)                       |                                              [Visit Web Site](https://github.com/roadhump/SublimeLinter-eslint){target=_blank}                                              |
|   <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/vim.ico" alt="" height="32px" class="megalinter-icon"></a>    | [vim](https://www.vim.org/)                              | [ale](https://github.com/w0rp/ale)                                                             |                                                        [Visit Web Site](https://github.com/w0rp/ale){target=_blank}                                                         |
|   <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/vim.ico" alt="" height="32px" class="megalinter-icon"></a>    | [vim](https://www.vim.org/)                              | [Syntastic](https://github.com/vim-syntastic/syntastic/tree/master/syntax_checkers/javascript) |                             [Visit Web Site](https://github.com/vim-syntastic/syntastic/tree/master/syntax_checkers/javascript){target=_blank}                              |
|  <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/vscode.ico" alt="" height="32px" class="megalinter-icon"></a>  | [Visual Studio Code](https://code.visualstudio.com/)     | [vscode-eslint](https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint)    | [![Install in VSCode](https://github.com/oxsecurity/megalinter/raw/main/docs/assets/images/btn_install_vscode.png)](vscode:extension/dbaeumer.vscode-eslint){target=_blank} |

## MegaLinter Flavors

This linter is available in the following flavors

|                                                                         <!-- -->                                                                         | Flavor                                                       | Description                                              | Embedded linters |                                                                                                                                                                                             Info |
|:--------------------------------------------------------------------------------------------------------------------------------------------------------:|:-------------------------------------------------------------|:---------------------------------------------------------|:----------------:|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/images/mega-linter-square.png" alt="" height="32px" class="megalinter-icon"></a> | [all](https://megalinter.io/beta/supported-linters/)         | Default MegaLinter Flavor                                |       126        |                       ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter) |
|       <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/cupcake.ico" alt="" height="32px" class="megalinter-icon"></a>       | [cupcake](https://megalinter.io/beta/flavors/cupcake/)       | MegaLinter for the most commonly used languages          |        87        |       ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-cupcake/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-cupcake) |
|      <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/dotnetweb.ico" alt="" height="32px" class="megalinter-icon"></a>      | [dotnetweb](https://megalinter.io/beta/flavors/dotnetweb/)   | Optimized for C, C++, C# or VB based projects with JS/TS |        73        |   ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-dotnetweb/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-dotnetweb) |
|     <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/javascript.ico" alt="" height="32px" class="megalinter-icon"></a>      | [javascript](https://megalinter.io/beta/flavors/javascript/) | Optimized for JAVASCRIPT or TYPESCRIPT based projects    |        59        | ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-javascript/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-javascript) |

## Behind the scenes

### How are identified applicable files

- Activated only if one of these files is found: `.eslintrc.json, .eslintrc.yml, .eslintrc.yaml, .eslintrc.js, .eslintrc.cjs, package.json:eslintConfig`
- File extensions: `.tsx`

<!-- markdownlint-disable -->
<!-- /* cSpell:disable */ -->
### How the linting is performed

- eslint is called once with the list of files as arguments (`list_of_files` CLI lint mode)

### Example calls

```shell
eslint myfile.tsx
```

```shell
eslint -c .eslintrc.json --no-eslintrc --no-ignore myfile.tsx
```

```shell
eslint --fix -c .eslintrc.json --no-eslintrc --no-ignore myfile.tsx
```


### Help content

```shell
eslint [options] file.js [file.js] [dir]

Basic configuration:
  --no-eslintrc                    Disable use of configuration from .eslintrc.*
  -c, --config path::String        Use this configuration, overriding .eslintrc.* config options if present
  --env [String]                   Specify environments
  --ext [String]                   Specify JavaScript file extensions
  --global [String]                Define global variables
  --parser String                  Specify the parser to be used
  --parser-options Object          Specify parser options
  --resolve-plugins-relative-to path::String  A folder where plugins should be resolved from, CWD by default

Specify Rules and Plugins:
  --plugin [String]                Specify plugins
  --rule Object                    Specify rules
  --rulesdir [path::String]        Load additional rules from this directory. Deprecated: Use rules from plugins

Fix Problems:
  --fix                            Automatically fix problems
  --fix-dry-run                    Automatically fix problems without saving the changes to the file system
  --fix-type Array                 Specify the types of fixes to apply (directive, problem, suggestion, layout)

Ignore Files:
  --ignore-path path::String       Specify path of ignore file
  --no-ignore                      Disable use of ignore files and patterns
  --ignore-pattern [String]        Pattern of files to ignore (in addition to those in .eslintignore)

Use stdin:
  --stdin                          Lint code provided on <STDIN> - default: false
  --stdin-filename String          Specify filename to process STDIN as

Handle Warnings:
  --quiet                          Report errors only - default: false
  --max-warnings Int               Number of warnings to trigger nonzero exit code - default: -1

Output:
  -o, --output-file path::String   Specify file to write report to
  -f, --format String              Use a specific output format - default: stylish
  --color, --no-color              Force enabling/disabling of color

Inline configuration comments:
  --no-inline-config               Prevent comments from changing config or rules
  --report-unused-disable-directives  Adds reported errors for unused eslint-disable and eslint-enable directives
  --report-unused-disable-directives-severity String  Chooses severity level for reporting unused eslint-disable and eslint-enable directives - either: off, warn, error, 0, 1, or 2

Caching:
  --cache                          Only check changed files - default: false
  --cache-file path::String        Path to the cache file. Deprecated: use --cache-location - default: .eslintcache
  --cache-location path::String    Path to the cache file or directory
  --cache-strategy String          Strategy to use for detecting changed files in the cache - either: metadata or content - default: metadata

Miscellaneous:
  --init                           Run config initialization wizard - default: false
  --env-info                       Output execution environment information - default: false
  --no-error-on-unmatched-pattern  Prevent errors when pattern is unmatched
  --exit-on-fatal-error            Exit with exit code 2 in case of fatal error - default: false
  --debug                          Output debugging information
  -h, --help                       Show help
  -v, --version                    Output the version number
  --print-config path::String      Print the configuration for the given file
```

### Installation on mega-linter Docker image

- Dockerfile commands :
```dockerfile
# renovate: datasource=npm depName=typescript
ARG NPM_TYPESCRIPT_VERSION=5.8.3
# renovate: datasource=npm depName=eslint
ARG NPM_ESLINT_VERSION=8.57.1
# renovate: datasource=npm depName=eslint-config-airbnb
ARG NPM_ESLINT_CONFIG_AIRBNB_VERSION=19.0.4
# renovate: datasource=npm depName=eslint-config-prettier
ARG NPM_ESLINT_CONFIG_PRETTIER_VERSION=10.1.8
# renovate: datasource=npm depName=eslint-plugin-jest
ARG NPM_ESLINT_PLUGIN_JEST_VERSION=29.0.1
# renovate: datasource=npm depName=eslint-plugin-prettier
ARG NPM_ESLINT_PLUGIN_PRETTIER_VERSION=5.5.3
# renovate: datasource=npm depName=eslint-plugin-react
ARG NPM_ESLINT_PLUGIN_REACT_VERSION=7.37.5
# renovate: datasource=npm depName=@babel/eslint-parser
ARG NPM_BABEL_ESLINT_PARSER_VERSION=7.28.0
# renovate: datasource=npm depName=prettier
ARG NPM_PRETTIER_VERSION=3.6.2
# renovate: datasource=npm depName=prettyjson
ARG NPM_PRETTYJSON_VERSION=1.2.5
# renovate: datasource=npm depName=@typescript-eslint/eslint-plugin
ARG NPM_TYPESCRIPT_ESLINT_ESLINT_PLUGIN_VERSION=8.38.0
# renovate: datasource=npm depName=@typescript-eslint/parser
ARG NPM_TYPESCRIPT_ESLINT_PARSER_VERSION=8.38.0
# renovate: datasource=npm depName=@microsoft/eslint-formatter-sarif
ARG NPM_MICROSOFT_ESLINT_FORMATTER_SARIF_VERSION=3.1.0
```

- NPM packages (node.js):
  - [typescript@5.8.3](https://www.npmjs.com/package/typescript/v/5.8.3)
  - [eslint@8.57.1](https://www.npmjs.com/package/eslint/v/8.57.1)
  - [eslint-config-airbnb@19.0.4](https://www.npmjs.com/package/eslint-config-airbnb/v/19.0.4)
  - [eslint-config-prettier@10.1.8](https://www.npmjs.com/package/eslint-config-prettier/v/10.1.8)
  - [eslint-plugin-jest@29.0.1](https://www.npmjs.com/package/eslint-plugin-jest/v/29.0.1)
  - [eslint-plugin-prettier@5.5.3](https://www.npmjs.com/package/eslint-plugin-prettier/v/5.5.3)
  - [eslint-plugin-react@7.37.5](https://www.npmjs.com/package/eslint-plugin-react/v/7.37.5)
  - [@babel/eslint-parser@7.28.0](https://www.npmjs.com/package/@babel/eslint-parser/v/7.28.0)
  - [prettier@3.6.2](https://www.npmjs.com/package/prettier/v/3.6.2)
  - [prettyjson@1.2.5](https://www.npmjs.com/package/prettyjson/v/1.2.5)
  - [@typescript-eslint/eslint-plugin@8.38.0](https://www.npmjs.com/package/@typescript-eslint/eslint-plugin/v/8.38.0)
  - [@typescript-eslint/parser@8.38.0](https://www.npmjs.com/package/@typescript-eslint/parser/v/8.38.0)
  - [@microsoft/eslint-formatter-sarif@3.1.0](https://www.npmjs.com/package/@microsoft/eslint-formatter-sarif/v/3.1.0)
