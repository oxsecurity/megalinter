<?php

$finder = (new PhpCsFixer\Finder())
    ->in('.')
;

return (new PhpCsFixer\Config())
    ->setRules([
        '@PER-CS' => true,
        '@PhpCsFixer:risky' => true,
    ])
    ->setFinder($finder)
;
