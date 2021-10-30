/**
 * @fileoverview Options configuration for optionator.
 * @author Nicolas Vuillamy
 */

"use strict";

//------------------------------------------------------------------------------
// Requirements
//------------------------------------------------------------------------------

const optionator = require("optionator");

//------------------------------------------------------------------------------
// Initialization and Public Interface
//------------------------------------------------------------------------------

// exports "parse(args)", "generateHelp()", and "generateHelpForOption(optionName)"
module.exports = optionator({
  prepend: "mega-linter [options]",
  defaults: {
    concatRepeatedArrays: true,
    mergeRepeatedObjects: true,
  },
  options: [
    {
      option: "release",
      alias: "r",
      type: "String",
      default: "v5",
      description: "Mega-Linter version",
      example: ["stable", "latest", "v5.9.0"],
    },
    {
      option: "flavor",
      alias: "f",
      type: "String",
      default: "all",
      description: "Mega-Linter flavor",
      example: ["dotnet", "javascript", "java", "php", "python"],
    },
    {
      option: "image",
      alias: "d",
      type: "String",
      description: "Mega-Linter docker image",
      example: [
        "ghcr.io/megalinter/megalinter:latest",
        "ghcr.io/megalinter/megalinter:v5",
        "my-registry.com/mega-linter-python:v5",
      ],
    },
    {
      option: "path",
      alias: "p",
      type: "path::String",
      default: ".",
      description:
        "Directory containing the files to lint (default: current directory)",
      example: ["./path/to/my/files"],
    },
    {
      option: "env",
      alias: "e",
      type: "[String]",
      description: "Environment variable (multiple)",
      example: [
        "-e 'ENABLE=JAVASCRIPT' -e 'SHOW_ELAPSED_TIME=true'",
        "-e 'ENABLE=JAVASCRIPT,YAML' -e 'DISABLE_LINTERS=MARKDOWN_MARKDOWN_LINK_CHECK'",
      ],
    },
    {
      option: "fix",
      type: "Boolean",
      description: "Apply formatters and fixes in linted sources",
    },
    {
      option: "json",
      alias: "j",
      type: "Boolean",
      description: "Outputs results as JSON string",
    },
    {
      option: "nodockerpull",
      alias: "n",
      type: "Boolean",
      description: "Do not pull docker image before running it",
    },
    {
      option: "debug",
      type: "Boolean",
      description: "See debug logs",
    },
    {
      option: "help",
      alias: "h",
      type: "Boolean",
      description:
        "Show help (mega-linter --help OPTIONNAME to see option detail)",
    },
    {
      option: "version",
      alias: "v",
      type: "Boolean",
      description: "Show version",
    },
    {
      option: "install",
      alias: "i",
      type: "Boolean",
      description: "Generate Mega-Linter configuration in your project",
    },
    {
      option: "upgrade",
      alias: "u",
      type: "Boolean",
      description: "Upgrade local repository Mega-Linter configuration",
    },
  ],
  mutuallyExclusive: [
    ["help", "version", "install"],
    ["image", "flavor"],
  ],
});
