/**
 * @fileoverview Options configuration for optionator.
 * @author Nicolas Vuillamy
 */

//------------------------------------------------------------------------------
// Requirements
//------------------------------------------------------------------------------

import * as optionator from 'optionator';
import { DEFAULT_RELEASE } from "./config.js";
import { KNOWN_DASHBOARD_PROVIDERS } from "./upload-dashboards.js";

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

export const KNOWN_SETUP_CI_SYSTEMS = [
  "gitHubActions",
  "gitLabCI",
  "azure",
  "bitbucket",
  "jenkins",
  "droneCI",
  "concourse",
  "other",
];

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
      description:
        // MAJOR-RELEASE-IMPACTED
        "MegaLinter version tag pulled from ghcr.io/oxsecurity/megalinter. Accepts a release tag (`v10.0.0`), a moving tag (`stable`, `latest`, `beta`, `alpha`), or a major-version tag (`v10`).\n" +
        "Default: MEGALINTER_VERSION property of .mega-linter.yml if defined, else `latest`.",
      example: ["stable", "latest", "beta", `${DEFAULT_RELEASE}.1.2`],
    },
    {
      option: "flavor",
      alias: "f",
      type: "String",
      description:
        "Specialized MegaLinter image to pull. Smaller flavors start faster and avoid pulling tools you do not need.\n" +
        "Default: MEGALINTER_FLAVOR property of .mega-linter.yml if defined, else `all`.\n" +
        `Allowed values: ${KNOWN_FLAVORS.join(", ")}.`,
      example: KNOWN_FLAVORS,
    },
    {
      option: "linter",
      alias: "l",
      type: "String",
      description:
        "Run a single linter using its standalone MegaLinter image (ghcr.io/oxsecurity/megalinter-only-<linter_key>). " +
        "Pass files to lint as positional arguments to restrict the analysis. " +
        "Reports are written to megalinter-reports/<linter_key> so several standalone runs can be launched in parallel. " +
        "Mutually exclusive with --flavor and --image.",
      example: ["PYTHON_RUFF", "MARKDOWN_MARKDOWNLINT src/README.md docs/index.md"],
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
      option: "prerun",
      type: "Boolean",
      description:
        "Analysis-only mode (equivalent to -e MEGALINTER_PRERUN=true): identify active linters and collect files, then stop before running any linter and output configuration suggestions to improve performances (directories to exclude, lighter flavor), in the console and in megalinter-reports/prerun-report.json. Requires MegaLinter v10 or beta.",
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
      option: "timeout",
      alias: "t",
      type: "Int",
      description:
        "Maximum duration in seconds of the MegaLinter container run (image pull time is not counted). " +
        "When the limit is reached, the container is stopped and removed, its last log lines are displayed, and mega-linter-runner exits with code 124. " +
        "If --container-name is not set, a container name is auto-generated so the exact container can be stopped even if the CLI process itself is killed. " +
        "No limit by default. Recommended when mega-linter-runner is driven by automation (CI wrappers, AI agents) so a stuck run cannot hang forever.",
      example: ["600", "1800"],
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
        "Generator that scaffolds .mega-linter.yml and CI workflow files in the current project. " +
        "Interactive by default: use --no-prompt and the --setup-* options (plus --flavor, --release and --fix) to run it non-interactively (e.g. from a coding agent or a CI job).",
    },
    {
      option: "setup-ci",
      type: "String",
      description:
        "[--install] CI/CD system to generate a workflow file for.\n" +
        `Allowed values: ${KNOWN_SETUP_CI_SYSTEMS.join(", ")}.`,
      example: ["gitHubActions", "gitLabCI"],
    },
    {
      option: "setup-copy-paste",
      type: "Boolean",
      description:
        "[--install] Enable detection of excessive copy-pastes (jscpd). Use --no-setup-copy-paste to disable it. Default: true.",
    },
    {
      option: "setup-spelling-mistakes",
      type: "Boolean",
      description:
        "[--install] Enable detection of spelling mistakes (cspell). Use --no-setup-spelling-mistakes to disable it. Default: true.",
    },
    {
      option: "setup-default-branch",
      type: "String",
      description: "[--install] Default branch of the repository. Default: main.",
      example: ["main", "master"],
    },
    {
      option: "setup-validate-all-code-base",
      type: "String",
      description:
        "[--install] `all` to lint all sources on each run, `diff` to lint only files updated compared to the default branch.",
      example: ["all", "diff"],
    },
    {
      option: "setup-ox",
      type: "Boolean",
      description:
        "[--install] Visit OX Security to secure your software supply chain. Use --no-setup-ox to skip it. Default: true in interactive mode, false with --no-prompt.",
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
      option: "prompt",
      type: "Boolean",
      description:
        "Enable interactive prompts. Use --no-prompt to run non-interactively. For `--upgrade`, that proceeds with the upgrade and skips optional follow-up prompts.",
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
      option: "user-map",
      type: "Boolean",
      description:
        "Run the container as a non-root user. On POSIX systems this uses your user. On other hosts it uses 1000:1000.",
    },
    {
      option: "no-user-map",
      type: "Boolean",
      description:
        "Run the container as root.",
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
    {
      option: "upload-dashboards",
      type: "String",
      description:
        "Upload (create or refresh) the MegaLinter observability dashboards to a provider. " +
        "Requires the provider auth environment variables (see https://megalinter.io/latest/reporters/ApiReporter/): " +
        "grafana: GRAFANA_URL + GRAFANA_TOKEN | datadog: DD_SITE + DD_API_KEY + DD_APP_KEY (or DD_BEARER_TOKEN) | " +
        "elastic: KIBANA_URL + ELASTIC_API_KEY | newrelic: NEW_RELIC_API_KEY + NEW_RELIC_ACCOUNT_ID + NEW_RELIC_REGION.\n" +
        `Allowed values: ${KNOWN_DASHBOARD_PROVIDERS.join(", ")}.`,
      example: KNOWN_DASHBOARD_PROVIDERS,
    },
    {
      option: "dashboards-folder",
      type: "String",
      description:
        "[--upload-dashboards] Grafana folder receiving the dashboards. Default: MegaLinter.",
      example: ["MegaLinter"],
    },
    {
      option: "setup-dashboards",
      type: "String",
      description:
        "[--install/--upgrade] Provision the observability dashboards of the given provider after generating/upgrading the configuration (non-interactive equivalent of the dashboards prompt).\n" +
        `Allowed values: ${KNOWN_DASHBOARD_PROVIDERS.join(", ")}.`,
      example: KNOWN_DASHBOARD_PROVIDERS,
    },
  ],
  mutuallyExclusive: [
    ["help", "version", "install", "list-vars", "upload-dashboards"],
    ["image", "flavor", "linter"],
  ],
});
