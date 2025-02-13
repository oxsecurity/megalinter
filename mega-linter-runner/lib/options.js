/**
 * @fileoverview Options configuration for optionator.
 * @author Nicolas Vuillamy
 */

//------------------------------------------------------------------------------
// Requirements
//------------------------------------------------------------------------------

import * as optionator from 'optionator';
import { DEFAULT_RELEASE } from "./config.js";

//------------------------------------------------------------------------------
// Initialization and Public Interface
//------------------------------------------------------------------------------

// exports "parse(args)", "generateHelp()", and "generateHelpForOption(optionName)"
export const optionsDefinition = optionator.default({
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
      default: DEFAULT_RELEASE,
      description: "MegaLinter version",
      example: ["stable", "latest", `${DEFAULT_RELEASE}.1.2`],
    },
    {
      option: "flavor",
      alias: "f",
      type: "String",
      default: "all",
      description: "MegaLinter flavor",
      example: ["dotnet", "javascript", "java", "php", "python"],
    },
    {
      option: "image",
      alias: "d",
      type: "String",
      description: "MegaLinter docker image",
      example: [
        "ghcr.io/oxsecurity/megalinter:latest",
        `ghcr.io/oxsecurity/megalinter:${DEFAULT_RELEASE}`,
        `my-registry.com/mega-linter-python:${DEFAULT_RELEASE}`,
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
      option: "filesonly",
      type: "Boolean",
      description: "Do not run linters with project as CLI lint mode",
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
      option: "platform",
      alias: "z",
      type: "String",
      default: "linux/amd64",
      description:
        "Force a docker image platform (currently, only linux/amd64 works)",
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
      description: "Generate MegaLinter configuration in your project",
    },
    {
      option: "upgrade",
      alias: "u",
      type: "Boolean",
      description: "Upgrade local repository MegaLinter configuration",
    },
    {
      option: "container-name",
      alias: "containername",
      type: "String",
      description: "Specify MegaLinter container name",
    },
    {
      option: "remove-container",
      type: "Boolean",
      description: "Remove MegaLinter Docker container when done (default: true since v7.8.0)",
    },
    {
      option: "no-remove-container",
      type: "Boolean",
      description: "Do not remove MegaLinter Docker container when done",
    },
    {
      option: "codetotal",
      type: "Boolean",
      description: "Run CodeTotal locally",
    },
    {
      option: "codetotal-url",
      type: "String",
      default: "http://localhost:8081/",
      description: "URL Hosting CodeTotal once launched",
    },
  ],
  mutuallyExclusive: [
    ["help", "version", "install"],
    ["image", "flavor"],
  ],
});
