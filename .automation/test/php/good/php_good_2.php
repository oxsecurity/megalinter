<?php

/**
 * PHP version 8
 *
 * @category Template_Class
 * @package  Template_Class
 * @author   Author <author@domain.com>
 * @license  https://opensource.org/licenses/MIT MIT License
 * @link     http://localhost/
 */

/**
 * Summary of helloName
 * @param string $name test
 * @return string[]
 */
function helloName(string $name): array
{
    return ["hello", $name];
}

/**
 * Summary of helloMegalinter
 * @return void
 */
function helloMegalinter(): void
{
    $hello = helloName("MegaLinter");
    echo implode(" ", $hello) . PHP_EOL;
}

/**
 * Summary of helloOrWorld
 * @return void
 */
function helloOrWorld(): void
{
    $random = rand(0, 10);
    if ($random >= 5) {
        echo "Hello";
    } else {
        echo "World";
    }
}
