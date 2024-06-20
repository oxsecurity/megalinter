<!-- markdownlint-disable MD033 MD041 -->
<!-- @generated by .automation/build.py, please do not update manually -->

<div align="center">
  <a href="https://www.php.net" target="blank" title="Visit linter Web Site">
    <img src="https://www.php.net/images/logos/new-php-logo.svg" alt="php" height="150px" class="megalinter-banner">
  </a>
</div>

[![GitHub last commit](https://img.shields.io/github/last-commit/php/php-src)](https://github.com/php/php-src/commits)

## php documentation

- Version in MegaLinter: **7.4.26**
- Visit [Official Web Site](https://www.php.net){target=_blank}

[![php-src - GitHub](https://gh-card.dev/repos/php/php-src.svg?fullname=)](https://github.com/php/php-src){target=_blank}

## Configuration in MegaLinter

- Enable php by adding `PHP_BUILTIN` in [ENABLE_LINTERS variable](https://megalinter.io/configuration/#activation-and-deactivation)
- Disable php by adding `PHP_BUILTIN` in [DISABLE_LINTERS variable](https://megalinter.io/configuration/#activation-and-deactivation)

| Variable                                | Description                                                                                                                                                                                                         | Default value      |
|-----------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------|
| PHP_BUILTIN_ARGUMENTS                   | User custom arguments to add in linter CLI call<br/>Ex: `-s --foo "bar"`                                                                                                                                            |                    |
| PHP_BUILTIN_FILTER_REGEX_INCLUDE        | Custom regex including filter<br/>Ex: `(src\|lib)`                                                                                                                                                                  | Include every file |
| PHP_BUILTIN_FILTER_REGEX_EXCLUDE        | Custom regex excluding filter<br/>Ex: `(test\|examples)`                                                                                                                                                            | Exclude no file    |
| PHP_BUILTIN_CLI_LINT_MODE               | Override default CLI lint mode<br/>- `file`: Calls the linter for each file<br/>- `list_of_files`: Call the linter with the list of files as argument<br/>- `project`: Call the linter from the root of the project | `file`             |
| PHP_BUILTIN_FILE_EXTENSIONS             | Allowed file extensions. `"*"` matches any extension, `""` matches empty extension. Empty list excludes all files<br/>Ex: `[".py", ""]`                                                                             | `[".php"]`         |
| PHP_BUILTIN_FILE_NAMES_REGEX            | File name regex filters. Regular expression list for filtering files by their base names using regex full match. Empty list includes all files<br/>Ex: `["Dockerfile(-.+)?", "Jenkinsfile"]`                        | Include every file |
| PHP_BUILTIN_PRE_COMMANDS                | List of bash commands to run before the linter                                                                                                                                                                      | None               |
| PHP_BUILTIN_POST_COMMANDS               | List of bash commands to run after the linter                                                                                                                                                                       | None               |
| PHP_BUILTIN_DISABLE_ERRORS              | Run linter but consider errors as warnings                                                                                                                                                                          | `false`            |
| PHP_BUILTIN_DISABLE_ERRORS_IF_LESS_THAN | Maximum number of errors allowed                                                                                                                                                                                    | `0`                |

## MegaLinter Flavours

This linter is available in the following flavours

|                                                                         <!-- -->                                                                         | Flavor                                          | Description                      | Embedded linters |                                                                                                                                                                             Info |
|:--------------------------------------------------------------------------------------------------------------------------------------------------------:|:------------------------------------------------|:---------------------------------|:----------------:|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/images/mega-linter-square.png" alt="" height="32px" class="megalinter-icon"></a> | [all](https://megalinter.io/supported-linters/) | Default MegaLinter Flavor        |        97        |         ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/megalinter/megalinter/v5) ![Docker Pulls](https://img.shields.io/docker/pulls/megalinter/megalinter) |
|         <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/php.ico" alt="" height="32px" class="megalinter-icon"></a>         | [php](https://megalinter.io/flavors/php/)       | Optimized for PHP based projects |        46        | ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/megalinter/megalinter-php/v5) ![Docker Pulls](https://img.shields.io/docker/pulls/megalinter/megalinter-php) |

## Behind the scenes

### How are identified applicable files

- File extensions: `.php`

<!-- markdownlint-disable -->
<!-- /* cSpell:disable */ -->
### How the linting is performed

- php is called one time by identified file

### Example calls

```shell
php -l myfile.js
```


### Help content

```shell
Usage: php [options] [-f] <file> [--] [args...]
   php [options] -r <code> [--] [args...]
   php [options] [-B <begin_code>] -R <code> [-E <end_code>] [--] [args...]
   php [options] [-B <begin_code>] -F <file> [-E <end_code>] [--] [args...]
   php [options] -S <addr>:<port> [-t docroot] [router]
   php [options] -- [args...]
   php [options] -a

  -a               Run as interactive shell
  -c <path>|<file> Look for php.ini file in this directory
  -n               No configuration (ini) files will be used
  -d foo[=bar]     Define INI entry foo with value 'bar'
  -e               Generate extended information for debugger/profiler
  -f <file>        Parse and execute <file>.
  -h               This help
  -i               PHP information
  -l               Syntax check only (lint)
  -m               Show compiled in modules
  -r <code>        Run PHP <code> without using script tags <?..?>
  -B <begin_code>  Run PHP <begin_code> before processing input lines
  -R <code>        Run PHP <code> for every input line
  -F <file>        Parse and execute <file> for every input line
  -E <end_code>    Run PHP <end_code> after processing all input lines
  -H               Hide any passed arguments from external tools.
  -S <addr>:<port> Run with built-in web server.
  -t <docroot>     Specify document root <docroot> for built-in web server.
  -s               Output HTML syntax highlighted source.
  -v               Version number
  -w               Output source with stripped comments and whitespace.
  -z <file>        Load Zend extension <file>.

  args...          Arguments passed to script. Use -- args when first argument
                   starts with - or script is read from stdin

  --ini            Show configuration file names

  --rf <name>      Show information about function <name>.
  --rc <name>      Show information about class <name>.
  --re <name>      Show information about extension <name>.
  --rz <name>      Show information about Zend extension <name>.
  --ri <name>      Show configuration for extension <name>.

```

### Installation on mega-linter Docker image
