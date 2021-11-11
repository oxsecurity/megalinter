<?php

/**
 * @return array<string>
 */
function helloName(string $name): array
{
    return ["hello", $name];
}

function helloMegalinter(): void
{
    $hello = helloName("MegaLinter");
    echo implode(" ", $hello) . PHP_EOL;
}

function helloOrWorld(): void
{
    $random = rand(0, 10);
    if ($random >= 5) {
        echo "Hello";
    } else {
        echo "World";
    }
}
