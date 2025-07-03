<?php

$finder = (new PhpCsFixer\Finder())
    ->in('.')
;

return (new PhpCsFixer\Config())
    // use default @link https://www.php-fig.org/per/coding-style/
    ->setRules([
        '@PER-CS' => true,
    ])
    // default source code to scan
    ->setFinder($finder)
;
