<?php

$finder = (new PhpCsFixer\Finder())
    ->in('.')
;

return (new PhpCsFixer\Config())
    // allow to run on unsupported PHP Versions
    // {@link https://github.com/PHP-CS-Fixer/PHP-CS-Fixer/blob/master/README.md#supported-php-versions}
    ->setUnsupportedPhpVersionAllowed(true)
    // use default @link https://www.php-fig.org/per/coding-style/
    ->setRules([
        '@PER-CS' => true,
    ])
    // default source code to scan
    ->setFinder($finder)
;
