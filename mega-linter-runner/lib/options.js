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

export const KNOWN_FLAVORS = [
  "all",
  "c_cpp",
  "ci_light",
  "cupcake",
  "documentation",
  "dotnet",
  "dotnetweb",
  "formatters",
  "go",
  "java",
  "javascript",
  "php",
  "python",
  "ruby",
  "rust",
  "salesforce",
  "security",
  "swift",
  "terraform",
];

export const KNOWN_CONTAINER_ENGINES = ["docker", "podman"];

export const KNOWN_PLATFORMS = ["linux/amd64", "linux/arm64"];

// exports "parse(args)", "generateHelp()", and "generateHelpForOption(optionName)"
export const optionsDefinition = optionator.default({
  prepend: "mega-linter [options] [FILES...]",
  append:
    "Tips:\n" +
    "  - Pass MegaLinter env variables with -e KEY=VALUE (repeat or use commas: -e KEY1=val1,KEY2=val2).\n" +
    "  - List all 2300+ MegaLinter env variables with `mega-linter-runner --list-vars [pattern]`.\n" +
    "  - Online reference: https://megalinter.io/latest/config-variables/",
  defaults: {
    concatRepeatedArrays: [true, { oneValuePerFlag: true }],
    mergeRepeatedObjects: true,
  },
  options: [
    {
      option: "release",
      alias: "r",
      type: "String",
      default: DEFAULT_RELEASE,
      description:
        "MegaLinter version tag pulled from ghcr.io/oxsecurity/megalinter. Accepts a release tag (`v9.1.2`), a moving tag (`stable`, `latest`, `beta`, `alpha`), or a major-version tag (`v9`).",
      example: ["stable", "latest", "beta", `${DEFAULT_RELEASE}.1.2`],
    },
    {
      option: "flavor",
      alias: "f",
      type: "String",
      default: "all",
      description:
        "Specialized MegaLinter image to pull. Smaller flavors start faster and avoid pulling tools you do not need.\n" +
        `Allowed values: ${KNOWN_FLAVORS.join(", ")}.`,
      example: KNOWN_FLAVORS,
    },
    {
      option: "image",
      alias: "d",
      type: "String",
      description:
        "Full docker image reference to run instead of resolving from --flavor/--release. Mutually exclusive with --flavor.",
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
        "Directory containing the files to lint (default: current working directory). Mounted into the container at /tmp/lint.",
      example: ["./path/to/my/files", "/abs/path/to/repo"],
    },
    {
      option: "env",
      alias: "e",
      type: "[String]",
      description:
        "MegaLinter environment variable in KEY=VALUE form. Repeat the flag for multiple variables, or pass several with a single flag using commas (KEY1=val1,KEY2=val2). Commas inside a single value (e.g. ENABLE_LINTERS=A,B) are preserved as-is, quoted or not. Run `mega-linter-runner --list-vars [pattern]` to discover supported variables.",
      example: [
        "-e ENABLE=JAVASCRIPT -e SHOW_ELAPSED_TIME=true",
        "-e ENABLE_LINTERS=YAML_PRETTIER,YAML_YAMLLINT",
        "-e APPLY_FIXES=all,LOG_LEVEL=DEBUG",
        "--env=DISABLE_LINTERS=MARKDOWN_MARKDOWN_LINK_CHECK",
      ],
    },
    {
      option: "fix",
      type: "Boolean",
      description:
        "Apply formatters and auto-fixes (equivalent to -e APPLY_FIXES=all).",
    },
    {
      option: "filesonly",
      type: "Boolean",
      description:
        "Do not run linters in `project` CLI lint mode (equivalent to -e SKIP_CLI_LINT_MODES=project).",
    },
    {
      option: "json",
      alias: "j",
      type: "Boolean",
      description:
        "Output the run summary as a JSON object on stdout (equivalent to -e JSON_REPORTER=true).",
    },
    {
      option: "nodockerpull",
      alias: "n",
      type: "Boolean",
      description:
        "Skip `docker pull` before running. Useful for offline / cached / locally built images.",
    },
    {
      option: "platform",
      alias: "z",
      type: "String",
      default: "linux/amd64",
      description:
        "Container image platform forwarded to `docker --platform`.\n" +
        `Allowed values: ${KNOWN_PLATFORMS.join(", ")} (linux/arm64 support is partial — see docs).`,
      example: KNOWN_PLATFORMS,
    },
    {
      option: "debug",
      type: "Boolean",
      description:
        "Enable verbose logs (equivalent to -e LOG_LEVEL=DEBUG).",
    },
    {
      option: "help",
      alias: "h",
      type: "Boolean",
      description:
        "Show help. Pass an option name as positional arg to see details: `mega-linter-runner --help env`.",
    },
    {
      option: "version",
      alias: "v",
      type: "Boolean",
      description: "Print the mega-linter-runner version and exit.",
    },
    {
      option: "install",
      alias: "i",
      type: "Boolean",
      description:
        "Interactive generator that scaffolds .mega-linter.yml and CI workflow files in the current project.",
    },
    {
      option: "custom-flavor-setup",
      alias: "cfs",
      type: "Boolean",
      description: "Generate scaffolding files to build a custom MegaLinter flavor.",
    },
    {
      option: "custom-flavor-linters",
      type: "String",
      description:
        "Comma-separated list of MegaLinter linter keys to include in the custom flavor (e.g. YAML_PRETTIER,YAML_YAMLLINT).",
      example: ["YAML_PRETTIER,YAML_YAMLLINT", "PYTHON_RUFF,PYTHON_BLACK"],
    },
    {
      option: "upgrade",
      alias: "u",
      type: "Boolean",
      description:
        "Upgrade the local MegaLinter configuration (.mega-linter.yml and related CI files) to the current major version.",
    },
    {
      option: "container-name",
      alias: "containername",
      type: "String",
      description:
        "Override the container name passed to `docker run --name`.",
      example: ["my-megalinter-run"],
    },
    {
      option: "container-engine",
      alias: "",
      type: "String",
      default: "docker",
      description:
        "Container engine binary to invoke.\n" +
        `Allowed values: ${KNOWN_CONTAINER_ENGINES.join(", ")}.`,
      example: KNOWN_CONTAINER_ENGINES,
    },
    {
      option: "remove-container",
      type: "Boolean",
      description:
        "Remove the MegaLinter container when done. This is the default since v7.8.0; use --no-remove-container to keep it.",
    },
    {
      option: "no-remove-container",
      type: "Boolean",
      description:
        "Keep the MegaLinter container after the run. Useful for `docker logs <container>` post-mortem.",
    },
    {
      option: "codetotal",
      type: "Boolean",
      description:
        "[NOT ACTIVELY MAINTAINED] Launch CodeTotal locally (companion UI for MegaLinter results). The CodeTotal project is no longer actively maintained; use at your own risk.",
    },
    {
      option: "codetotal-url",
      type: "String",
      default: "http://localhost:8081/",
      description:
        "[NOT ACTIVELY MAINTAINED] URL where the local CodeTotal instance will be served. The CodeTotal project is no longer actively maintained.",
      example: ["http://localhost:8081/"],
    },
    {
      option: "list-vars",
      type: "Boolean",
      description:
        "List MegaLinter environment variables that can be passed via -e. Add a positional substring to filter (case-insensitive), e.g. `mega-linter-runner --list-vars PYTHON_RUFF`. Add --json for machine-readable output.",
    },
  ],
  mutuallyExclusive: [
    ["help", "version", "install", "list-vars"],
    ["image", "flavor"],
  ],
});
