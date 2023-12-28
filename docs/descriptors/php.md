---
title: PHP linters in MegaLinter
description: phpcs, phpstan, psalm, phplint are available to analyze PHP files in MegaLinter
---
<!-- markdownlint-disable MD003 MD020 MD033 MD041 -->
<!-- @generated by .automation/build.py, please don't update manually -->
<!-- Instead, update descriptor file at https://github.com/oxsecurity/megalinter/tree/main/megalinter/descriptors/php.yml -->
# PHP

## Linters

| Linter                                                            | Additional                                                                                                                                                            |
|-------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [**phpcs**](php_phpcs.md)<br/>[_PHP_PHPCS_](php_phpcs.md)         | [![GitHub stars](https://img.shields.io/github/stars/PHPCSStandards/PHP_CodeSniffer?cacheSeconds=3600)](https://github.com/PHPCSStandards/PHP_CodeSniffer)            |
| [**phpstan**](php_phpstan.md)<br/>[_PHP_PHPSTAN_](php_phpstan.md) | [![GitHub stars](https://img.shields.io/github/stars/phpstan/phpstan?cacheSeconds=3600)](https://github.com/phpstan/phpstan)                                          |
| [**psalm**](php_psalm.md)<br/>[_PHP_PSALM_](php_psalm.md)         | [![GitHub stars](https://img.shields.io/github/stars/vimeo/psalm?cacheSeconds=3600)](https://github.com/vimeo/psalm) ![sarif](https://shields.io/badge/-SARIF-orange) |
| [**phplint**](php_phplint.md)<br/>[_PHP_PHPLINT_](php_phplint.md) | [![GitHub stars](https://img.shields.io/github/stars/overtrue/phplint?cacheSeconds=3600)](https://github.com/overtrue/phplint)                                        |

## Linted files

- File extensions:
  - `.php`

## Configuration in MegaLinter

| Variable                 | Description                   | Default value |
|--------------------------|-------------------------------|---------------|
| PHP_FILTER_REGEX_INCLUDE | Custom regex including filter |               |
| PHP_FILTER_REGEX_EXCLUDE | Custom regex excluding filter |               |


## Behind the scenes

### Installation

- Dockerfile commands :
```dockerfile
RUN GITHUB_AUTH_TOKEN="$(cat /run/secrets/GITHUB_TOKEN)" \
    && export GITHUB_AUTH_TOKEN \
    && wget --tries=5 -q -O phive.phar https://phar.io/releases/phive.phar \
    && wget --tries=5 -q -O phive.phar.asc https://phar.io/releases/phive.phar.asc \
    && PHAR_KEY_ID="0x6AF725270AB81E04D79442549D8A98B29B2D5D79" \
    && ( gpg --keyserver hkps://keys.openpgp.org --recv-keys "$PHAR_KEY_ID" \
       || gpg --keyserver hkps://keyserver.ubuntu.com --recv-keys "$PHAR_KEY_ID" \
       || gpg --keyserver keyserver.pgp.com --recv-keys "$PHAR_KEY_ID" \
       || gpg --keyserver pgp.mit.edu --recv-keys "$PHAR_KEY_ID" ) \
    && gpg --verify phive.phar.asc phive.phar \
    && chmod +x phive.phar \
    && mv phive.phar /usr/local/bin/phive \
    && rm phive.phar.asc \
    && update-alternatives --install /usr/bin/php php /usr/bin/php81 110

```

- APK packages (Linux):
  - [gnupg](https://pkgs.alpinelinux.org/packages?branch=edge&name=gnupg)
  - [php81](https://pkgs.alpinelinux.org/packages?branch=edge&name=php81)
  - [php81-phar](https://pkgs.alpinelinux.org/packages?branch=edge&name=php81-phar)
  - [php81-mbstring](https://pkgs.alpinelinux.org/packages?branch=edge&name=php81-mbstring)
  - [php81-xmlwriter](https://pkgs.alpinelinux.org/packages?branch=edge&name=php81-xmlwriter)
  - [php81-tokenizer](https://pkgs.alpinelinux.org/packages?branch=edge&name=php81-tokenizer)
  - [php81-ctype](https://pkgs.alpinelinux.org/packages?branch=edge&name=php81-ctype)
  - [php81-curl](https://pkgs.alpinelinux.org/packages?branch=edge&name=php81-curl)
  - [php81-dom](https://pkgs.alpinelinux.org/packages?branch=edge&name=php81-dom)
  - [php81-simplexml](https://pkgs.alpinelinux.org/packages?branch=edge&name=php81-simplexml)
  - [dpkg](https://pkgs.alpinelinux.org/packages?branch=edge&name=dpkg)