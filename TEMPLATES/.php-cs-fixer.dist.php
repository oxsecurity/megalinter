<?php

$finder = (new PhpCsFixer\Finder())
    ->in('.')
;

return (new PhpCsFixer\Config())
    ->setRules([
        '@PER-CS' => true,
    ])
    ->setFinder($finder)
;
