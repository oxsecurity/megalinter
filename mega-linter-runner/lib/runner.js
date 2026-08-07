import {
  optionsDefinition,
  KNOWN_CONTAINER_ENGINES,
  KNOWN_SETUP_CI_SYSTEMS,
} from "./options.js";
import { expandEnvEntries } from "./env-parser.js";
import { listVars } from "./list-vars.js";
import { spawnSync } from "child_process";
import { default as c } from "chalk";
import * as path from "path";
import { dirname } from "path";
import { fileURLToPath } from "url";
import os from "os";
import which from "which";
import { default as fs } from "fs-extra";
import { MegaLinterUpgrader } from "./upgrade.js";
import { CodeTotalRunner } from "./codetotal.js";
import {
  DashboardUploader,
  KNOWN_DASHBOARD_PROVIDERS,
} from "./upload-dashboards.js";
import prompts from "prompts";
import { DEFAULT_RELEASE } from "./config.js";
import { createEnv } from "yeoman-environment";
import { default as FindPackageJson } from "find-package-json";
import { load as yamlLoad } from "js-yaml";

function isSElinuxOn() {
  return ["Enforcing", "Permissive", "enforcing", "permissive"].includes(process.env.SELINUX_MODE);
}

export class MegaLinterRunner {

  constructor() {
    // Injectable for tests: lets unit tests fake the container engine calls
    this.spawnSyncFn = spawnSync;
  }

  async run(options) {
    // Show help ( index or for an options)
    if (options.help) {
      let outputString;
      if (options._ && options._.length) {
        outputString = optionsDefinition.generateHelpForOption(options._[0]);
      } else {
        outputString = optionsDefinition.generateHelp();
      }
      console.info(outputString);
      return { status: 0, stdout: outputString };
    }

    // List MegaLinter env variables (optionally filtered)
    if (options.listVars) {
      const pattern = options._ && options._.length ? options._[0] : null;
      const { stdout } = listVars({ pattern, asJson: options.json === true });
      console.log(stdout);
      return { status: 0, stdout };
    }

    // Show version
    if (options.version) {
      let v = process.env.npm_package_version;
      if (!v) {
        try {
          const finder = FindPackageJson(__dirname);
          v = finder.next().value.version;
        } catch (e) {
          v = "error";
        }
      }
      const outputString = `mega-linter-runner version ${v}`;
      console.log(outputString);
      return { status: 0, stdout: outputString };
    }

    // Upload observability dashboards to a provider
    if (options.uploadDashboards) {
      const uploader = new DashboardUploader(options.uploadDashboards, {
        dashboardsFolder: options.dashboardsFolder,
      });
      await uploader.run();
      return { status: 0 };
    }

    // Run configuration generator
    if (options.install) {
      const env = createEnv();
      const __dirname = dirname(fileURLToPath(import.meta.url));
      const generatorPath = path.resolve(
        path.join(__dirname, "..", "generators", "mega-linter")
      );
      console.log("Yeoman generator used: " + generatorPath);
      if (options.prompt === false) {
        // Non-interactive mode overwrites conflicting files (force: true below):
        // keep a backup of pre-existing ones so customizations can be merged back
        this.backupExistingSetupTargets(process.cwd());
      }
      env.run(generatorPath, {
        promptAnswers: this.buildSetupAnswers(options),
        noPrompt: options.prompt === false,
        // Also skip yeoman's interactive overwrite-conflict prompts in no-prompt mode
        force: options.prompt === false,
      });
      return { status: 0 };
    }

    // Run custom flavor generator
    if (options.customFlavorSetup) {
      if (options.customFlavorLinters) {
        globalThis.customFlavorLinters = options.customFlavorLinters.split(",").map((linter) => linter.trim());
      }
      const env = createEnv();
      const __dirname = dirname(fileURLToPath(import.meta.url));
      const generatorPath = path.resolve(
        path.join(__dirname, "..", "generators", "mega-linter-custom-flavor")
      );
      console.log("Yeoman generator used: " + generatorPath);
      env.run(generatorPath);
      return { status: 0 };
    }

    // Run upgrader from v4 to v5
    if (options.upgrade) {
      const megaLinterUpgrader = new MegaLinterUpgrader({
        noPrompt: options.prompt === false,
      });
      await megaLinterUpgrader.run();
      await this.manageSetupDashboards(options);
      return { status: 0 };
    }

    if (options.codetotal) {
      console.warn(
        c.yellow(
          "[WARNING] CodeTotal is not actively maintained. The --codetotal integration is kept for legacy users and may be removed in a future major release.",
        ),
      );
      const codeTotalRunner = new CodeTotalRunner(options);
      await codeTotalRunner.run();
      return { status: 0 }
    }

    // Build MegaLinter docker image name with flavor and release version
    this.containerEngine = options.containerEngine || "docker";
    if (!KNOWN_CONTAINER_ENGINES.includes(this.containerEngine)) {
      throw new Error(
        `Invalid container engine: ${this.containerEngine}. Supported engines are ${KNOWN_CONTAINER_ENGINES.join(", ")}.`,
      );
    }
    // Flavor & version resolution: CLI args > .mega-linter.yml (MEGALINTER_FLAVOR / MEGALINTER_VERSION) > defaults
    const localConfig = this.readLocalConfig(path.resolve(options.path || "."));
    const { dockerImage, release } = this.resolveDockerImage(
      options,
      localConfig
    );
    this.checkPreviousVersion(release);

    // Check for docker installation
    const whichPromise = which(this.containerEngine);
    whichPromise.catch(() => {
      if (this.containerEngine === "podman") {
        console.error(`
  ERROR: Podman engine has not been found on your system.
  - To run MegaLinter locally, please install Podman: https://podman.io/docs/installation
  - To run Podman on CI, use a base image containing Podman engine`);
      }
      else {
        console.error(`
  ERROR: Docker engine has not been found on your system.
  - to run MegaLinter locally, please install docker desktop: https://www.docker.com/products/docker-desktop
  - to run docker on CI, use a base image containing docker engine`);
      }
    });

    // Get platform to use with docker pull & run
    const imagePlatform = options.platform || "linux/amd64";

    // Pull docker image. Pinned version tags (vX.Y.Z) are immutable: skip the pull
    // (and its registry round-trip) when the image is already available locally
    // for the requested platform
    const pinnedInspect =
      !options.image && /^v\d+\.\d+\.\d+$/.test(release)
        ? spawnSync(
            this.containerEngine,
            [
              "image",
              "inspect",
              "--format",
              "{{.Os}}/{{.Architecture}}",
              dockerImage,
            ],
            { encoding: "utf8", windowsHide: true }
          )
        : null;
    const pinnedVersionLocallyAvailable =
      pinnedInspect !== null &&
      pinnedInspect.status === 0 &&
      (pinnedInspect.stdout || "").trim() === imagePlatform;
    if (pinnedVersionLocallyAvailable) {
      console.log(
        `Skipped pull of ${dockerImage} (pinned version already available locally)`
      );
    } else if (options.nodockerpull !== true) {
      console.info(`Pulling docker image ${dockerImage} ... `);
      console.info(
        "INFO: this operation can be long during the first use of mega-linter-runner"
      );
      console.info(
        "The next runs, it will be immediate (thanks to docker cache !)"
      );
      const spawnResPull = spawnSync(
        this.containerEngine,
        ["pull", "--platform", imagePlatform, dockerImage],
        {
          detached: false,
          stdio: "inherit",
          windowsHide: true,
          windowsVerbatimArguments: true,
        }
      );
      // Manage case when unable to pull docker image
      if (spawnResPull.status !== 0) {
        return {
          status: 2,
          errorMsg: `Unable to pull [${dockerImage}]: \n${JSON.stringify(
            spawnResPull,
            null,
            2
          )}`,
        };
      }
    } else {
      console.log(`Skipped pull of ${dockerImage} (--nodockerpull used)`);
    }

    // Build docker run options
    const lintPath = path.resolve(options.path || ".");
    // Warn when the workspace contains well-known heavy directories:
    // local runs mount the raw workspace, so they can be much slower than CI
    const heavyDirCandidates = [
      "node_modules",
      ".wireit",
      ".turbo",
      ".nx",
      ".yarn/cache",
      ".pnpm-store",
      ".venv",
      "target",
      "vendor",
      "dist",
      "build",
    ];
    const heavyDirsFound = heavyDirCandidates.filter((dir) =>
      fs.existsSync(path.join(lintPath, dir))
    );
    if (heavyDirsFound.length > 0) {
      console.log(
        `Heavy folders detected in workspace (${heavyDirsFound.join(", ")}): ` +
          "local runs can be slower than CI on a fresh checkout. " +
          "Excluded directories are forwarded to project-mode linters that support native exclusions; " +
          "you can also skip project-mode linters entirely with -e SKIP_CLI_LINT_MODES=project"
      );
    }
    const dotenvPath = path.join(lintPath, ".env");
    const envVarsFromDotenv = [];
    let emptyEnvFile = null;
    if (fs.existsSync(dotenvPath)) {
      const dotenvContent = await fs.readFile(dotenvPath, "utf8");
      dotenvContent.split(/\r?\n/).forEach((line) => {
        const trimmedLine = line.trim();
        if (!trimmedLine || trimmedLine.startsWith("#")) {
          return;
        }
        const equalIndex = trimmedLine.indexOf("=");
        if (equalIndex === -1) {
          return;
        }
        const key = trimmedLine.slice(0, equalIndex).trim();
        const value = trimmedLine.slice(equalIndex + 1).trim();
        if (!key) {
          return;
        }
        envVarsFromDotenv.push(`${key}=${value}`);
      });
      const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "megalinter-"));
      emptyEnvFile = path.join(tmpDir, "empty.env");
      await fs.writeFile(emptyEnvFile, "");
    }
    const commandArgs = ["run", "--platform", imagePlatform];
    const removeContainer = options["removeContainer"] ? true : options["noRemoveContainer"] ? false : true;
    if (removeContainer) {
      commandArgs.push("--rm");
    }
    const timeoutSeconds = this.resolveTimeoutSeconds(options);
    let containerName = options["containerName"] || null;
    if (timeoutSeconds !== null && !containerName) {
      // A known container name is required to stop and remove the exact container
      // if the timeout is reached: killing the CLI process alone does not reliably
      // stop a `docker run`/`podman run` child on every platform (Windows signal
      // emulation in particular), which leaves orphan containers running
      containerName = `megalinter-runner-${Math.random().toString(36).slice(2, 10)}`;
      console.info(
        `--timeout: the container will be named ${containerName} so it can be stopped and removed if the time limit is reached`
      );
    }
    if (containerName) {
      commandArgs.push(...["--name", containerName]);
    }

    if (isSElinuxOn()) {
      commandArgs.push(...["-v", `${lintPath}:/tmp/lint:rw,z`]);
    } else {
      commandArgs.push(...["-v", `${lintPath}:/tmp/lint:rw`]);
    }

    if (options["userMap"] === true) {
      const runtimeUid =
        typeof process.getuid === "function" ? process.getuid() : 1000;
      const runtimeGid =
        typeof process.getgid === "function" ? process.getgid() : 1000;
      commandArgs.push(...["-e", `MEGALINTER_UID=${runtimeUid}`]);
      commandArgs.push(...["-e", `MEGALINTER_GID=${runtimeGid}`]);
      commandArgs.push(...["-e", "HOME=/home/megalinter"]);
    }
    if (emptyEnvFile) {
      if (isSElinuxOn()) {
        commandArgs.push(...["-v", `${emptyEnvFile}:/tmp/lint/.env:ro,z`]);
      } else {
        commandArgs.push(...["-v", `${emptyEnvFile}:/tmp/lint/.env:ro`]);
      }
    }

    commandArgs.push(...this.applyFixesEnvArgs(options, localConfig));
    if (options.debug === true) {
      commandArgs.push(...["-e", "LOG_LEVEL=DEBUG"]);
    }
    if (options.json === true) {
      commandArgs.push(...["-e", "JSON_REPORTER=true"]);
    }
    if (envVarsFromDotenv.length > 0) {
      for (const envVarEqualsValue of envVarsFromDotenv) {
        commandArgs.push(...["-e", envVarEqualsValue]);
      }
    }
    if (options.env) {
      for (const envVarEqualsValue of expandEnvEntries(options.env)) {
        commandArgs.push(...["-e", envVarEqualsValue]);
      }
    }
    commandArgs.push(
      ...this.standaloneLinterEnvArgs(options, envVarsFromDotenv)
    );
    // Files only
    if (options.filesonly === true) {
      commandArgs.push(...["-e", "SKIP_CLI_LINT_MODES=project"]);
    }
    // Prerun analysis mode
    if (options.prerun === true) {
      commandArgs.push(...["-e", "MEGALINTER_PRERUN=true"]);
      const releaseMajorMatch = /^v?(\d+)/.exec(release);
      if (releaseMajorMatch && Number(releaseMajorMatch[1]) < 10) {
        console.warn(
          c.yellow(
            `[WARNING] --prerun requires MegaLinter v10 or beta: with ${release}, a full lint run will happen instead. Use --release beta (or set MEGALINTER_VERSION: beta in .mega-linter.yml).`
          )
        );
      }
    }
    // list of files
    if ((options._ || []).length > 0) {
      commandArgs.push(
        ...["-e"],
        `MEGALINTER_FILES_TO_LINT=${options._.join(",")}`
      );
    }
    commandArgs.push(dockerImage);

    // Call docker run (mask secret-looking env values in the displayed command)
    const maskedArgs = commandArgs.map((arg, i) =>
      commandArgs[i - 1] === "-e"
        ? arg.replace(
            /^([^=]*(?:KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL|_PAT\b|AUTH)[^=]*)=.+$/i,
            "$1=***"
          )
        : arg
    );
    console.log(`Command: ${this.containerEngine} ${maskedArgs.join(" ")}`);
    const spawnOptions = {
      env: Object.assign({}, process.env),
      stdio: "inherit",
      windowsHide: true,
    };
    if (timeoutSeconds !== null) {
      spawnOptions.timeout = timeoutSeconds * 1000;
      // SIGKILL: SIGTERM emulation is unreliable on Windows, and the container
      // itself is stopped explicitly by name below anyway
      spawnOptions.killSignal = "SIGKILL";
    }
    const spawnRes = this.spawnSyncFn(
      this.containerEngine,
      commandArgs,
      spawnOptions
    );
    if (spawnRes.error && spawnRes.error.code === "ETIMEDOUT") {
      const errorMsg = this.handleRunTimeout(containerName, timeoutSeconds);
      // 124 is the conventional "command timed out" exit code (GNU timeout)
      return { status: 124, errorMsg, timedOut: true };
    }
    // Output json if requested
    if (options.json === true) {
      const reportSubFolder = options.linter
        ? path.join("megalinter-reports", options.linter.toLowerCase())
        : process.env.REPORT_OUTPUT_FOLDER || "megalinter-reports";
      const jsonOutputFile = path.join(
        lintPath,
        reportSubFolder,
        options.prerun === true ? "prerun-report.json" : "mega-linter-report.json"
      );
      if (fs.existsSync(jsonOutputFile)) {
        const jsonRaw = await fs.readFile(jsonOutputFile, "utf8");
        console.log(JSON.stringify(JSON.parse(jsonRaw)));
      }
    }
    return spawnRes;
  }

  // --timeout value in seconds, or null when no time limit is requested
  resolveTimeoutSeconds(options) {
    if (options.timeout === undefined || options.timeout === null) {
      return null;
    }
    const timeoutSeconds = Number(options.timeout);
    if (!Number.isInteger(timeoutSeconds) || timeoutSeconds <= 0) {
      throw new Error(
        `Invalid --timeout value: ${options.timeout}. It must be a positive number of seconds.`
      );
    }
    return timeoutSeconds;
  }

  // The run exceeded --timeout: the CLI child process has been killed, but the
  // container can survive it (notably on Windows, where signal emulation does
  // not propagate to docker/podman children), so print its last log lines for
  // diagnosis then stop and remove it explicitly by name
  handleRunTimeout(containerName, timeoutSeconds) {
    const errorMsg = `MegaLinter run exceeded the --timeout of ${timeoutSeconds}s and was stopped.`;
    console.error(
      c.red(
        `[ERROR] ${errorMsg} Common causes: a bind-mounted workspace with slow I/O ` +
          "(e.g. a Windows path mounted into a WSL2-backed container engine), " +
          "a linter waiting on a slow or unreachable network resource, " +
          "or a genuinely large repository needing a longer --timeout."
      )
    );
    // Capture the log tail before removing the container: it usually shows the
    // exact step where the run was stuck
    const logsRes = this.spawnSyncFn(
      this.containerEngine,
      ["logs", "--tail", "30", containerName],
      { encoding: "utf8", windowsHide: true }
    );
    const logsOutput = `${logsRes.stdout || ""}${logsRes.stderr || ""}`.trim();
    if (logsRes.status === 0 && logsOutput) {
      console.error(
        c.yellow(
          `Last log lines of container ${containerName} before it was stopped:`
        )
      );
      console.error(logsOutput);
    }
    const stopRes = this.spawnSyncFn(
      this.containerEngine,
      ["stop", containerName],
      { encoding: "utf8", windowsHide: true }
    );
    // With --rm (the default), stopping the container also removes it: the rm
    // fallback covers --no-remove-container and cases where --rm did not fire
    // because the run was hard-killed
    const rmRes = this.spawnSyncFn(
      this.containerEngine,
      ["rm", "--force", containerName],
      { encoding: "utf8", windowsHide: true }
    );
    if (stopRes.status === 0 || rmRes.status === 0) {
      console.error(
        `Container ${containerName} has been stopped and removed: no orphan container is left behind.`
      );
    } else {
      console.error(
        c.yellow(
          `[WARNING] Unable to confirm removal of container ${containerName}. ` +
            `Check manually with: ${this.containerEngine} ps --all --filter name=${containerName}`
        )
      );
    }
    return errorMsg;
  }

  resolveDockerImage(options, localConfig) {
    const flavor = options.flavor || localConfig.MEGALINTER_FLAVOR || "all";
    const releaseValue =
      options.release || localConfig.MEGALINTER_VERSION || "latest";
    const release = releaseValue === "stable" ? DEFAULT_RELEASE : releaseValue;
    const dockerImageName = options.linter
      ? `ghcr.io/oxsecurity/megalinter-only-${options.linter.toLowerCase()}`
      : // v4 retrocompatibility >>
      flavor === "all" && this.isv4(release)
        ? "nvuillam/mega-linter"
        : flavor !== "all" && this.isv4(release)
          ? `nvuillam/mega-linter-${flavor}`
          : // << v4 retrocompatibility
          // v5 retrocompatibility >>
          flavor === "all" && this.isv5(release)
            ? "megalinter/megalinter"
            : flavor !== "all" && this.isv5(release)
              ? `megalinter/megalinter-${flavor}`
              : // << v5 retrocompatibility
              flavor === "all"
                ? "ghcr.io/oxsecurity/megalinter"
                : `ghcr.io/oxsecurity/megalinter-${flavor}`;
    return {
      dockerImage: options.image || `${dockerImageName}:${release}`,
      release,
      flavor,
    };
  }

  // A non-"none" APPLY_FIXES defined in .mega-linter.yml takes precedence over the
  // --fix generic "all" value; --fix still forces "all" when config says "none"
  applyFixesEnvArgs(options, localConfig) {
    const applyFixesConfig = localConfig.APPLY_FIXES
      ? Array.isArray(localConfig.APPLY_FIXES)
        ? localConfig.APPLY_FIXES.join(",")
        : String(localConfig.APPLY_FIXES)
      : null;
    if (applyFixesConfig && applyFixesConfig !== "none") {
      console.info(
        `Fixes will be applied (APPLY_FIXES=${applyFixesConfig} from .mega-linter.yml)`
      );
      return [];
    }
    if (options.fix === true) {
      return ["-e", "APPLY_FIXES=all"];
    }
    return [];
  }

  // Standalone linter image: activate only this linter and isolate its reports
  // so several standalone runs can execute in parallel on the same repository
  standaloneLinterEnvArgs(options, dotenvVars = []) {
    if (!options.linter) {
      return [];
    }
    const linterKey = options.linter.toUpperCase();
    const envArgs = ["-e", `ENABLE_LINTERS=${linterKey}`];
    const userEnvVars = expandEnvEntries(options.env || []).concat(dotenvVars);
    if (!userEnvVars.some((e) => e.startsWith("REPORT_OUTPUT_FOLDER="))) {
      envArgs.push(
        "-e",
        `REPORT_OUTPUT_FOLDER=/tmp/lint/megalinter-reports/${linterKey.toLowerCase()}`
      );
    }
    return envArgs;
  }

  backupExistingSetupTargets(baseDir) {
    const targets = [
      ".mega-linter.yml",
      ".cspell.json",
      ".jscpd.json",
      path.join(".github", "workflows", "mega-linter.yml"),
      ".gitlab-ci.yml",
      "azure-pipelines.yml",
      "bitbucket-pipelines.yml",
      "Jenkinsfile",
      ".drone.yml",
      "concourse-task.yml",
    ];
    const backedUp = [];
    for (const target of targets) {
      const targetPath = path.join(baseDir, target);
      if (fs.existsSync(targetPath)) {
        fs.copySync(targetPath, `${targetPath}.megalinter-setup.bak`);
        backedUp.push(target);
      }
    }
    if (backedUp.length > 0) {
      console.warn(
        "[--install] Existing files that may be overwritten have been backed up " +
          `with a .megalinter-setup.bak extension: ${backedUp.join(", ")}. ` +
          "Compare them with the generated files to restore your customizations, then delete the backups."
      );
    }
    return backedUp;
  }

  readLocalConfig(lintPath) {
    const configFilePath = path.join(lintPath, ".mega-linter.yml");
    if (!fs.existsSync(configFilePath)) {
      return {};
    }
    try {
      return yamlLoad(fs.readFileSync(configFilePath, "utf8")) || {};
    } catch (e) {
      console.warn(
        c.yellow(
          `[WARNING] Unable to parse ${configFilePath}: ${e.message}. Ignoring it.`
        )
      );
      return {};
    }
  }

  buildSetupAnswers(options) {
    if (options.setupCi && !KNOWN_SETUP_CI_SYSTEMS.includes(options.setupCi)) {
      throw new Error(
        `Invalid --setup-ci value: ${options.setupCi}. ` +
          `Allowed values: ${KNOWN_SETUP_CI_SYSTEMS.join(", ")}`
      );
    }
    if (
      options.setupValidateAllCodeBase &&
      !["all", "diff"].includes(options.setupValidateAllCodeBase)
    ) {
      throw new Error(
        `Invalid --setup-validate-all-code-base value: ${options.setupValidateAllCodeBase}. Allowed values: all, diff`
      );
    }
    if (options.release && !["beta", DEFAULT_RELEASE].includes(options.release)) {
      console.info(
        `--install only generates configuration for ${DEFAULT_RELEASE} or beta: using ${DEFAULT_RELEASE} instead of ${options.release}`
      );
    }
    if (
      options.setupDashboards &&
      !KNOWN_DASHBOARD_PROVIDERS.includes(options.setupDashboards)
    ) {
      throw new Error(
        `Invalid --setup-dashboards value: ${options.setupDashboards}. ` +
          `Allowed values: ${KNOWN_DASHBOARD_PROVIDERS.join(", ")}`
      );
    }
    const answers = {
      flavor: options.flavor,
      ci: options.setupCi,
      copyPaste: options.setupCopyPaste,
      spellingMistakes: options.setupSpellingMistakes,
      version: options.release
        ? options.release === "beta"
          ? "beta"
          : DEFAULT_RELEASE
        : undefined,
      defaultBranch: options.setupDefaultBranch,
      validateAllCodeBase: options.setupValidateAllCodeBase,
      applyFixes: options.fix === true ? true : undefined,
      ox: options.setupOx,
      dashboards: options.setupDashboards,
    };
    Object.keys(answers).forEach(
      (key) => answers[key] === undefined && delete answers[key]
    );
    return answers;
  }

  // Offer observability dashboards provisioning after an upgrade:
  // --setup-dashboards <provider> in non-interactive mode, prompt otherwise
  async manageSetupDashboards(options) {
    let provider = options.setupDashboards;
    if (!provider && options.prompt !== false) {
      const response = await prompts({
        type: "select",
        name: "dashboards",
        message:
          "Do you want to provision/refresh MegaLinter observability dashboards (requires provider auth env variables) ?",
        choices: [
          { title: "No / later", value: "none" },
          { title: "Grafana (Loki + Prometheus)", value: "grafana" },
          { title: "Datadog", value: "datadog" },
          { title: "Elastic / Kibana", value: "elastic" },
          { title: "New Relic", value: "newrelic" },
        ],
        initial: 0,
      });
      provider = response.dashboards;
    }
    if (!provider || provider === "none") {
      return;
    }
    try {
      await new DashboardUploader(provider, {
        dashboardsFolder: options.dashboardsFolder,
      }).run();
      console.log(`Observability dashboards uploaded to ${provider} :)`);
    } catch (e) {
      console.error(`Dashboards upload failed: ${e.message}`);
      console.error(
        "Set the required auth environment variables then run: " +
          `npx mega-linter-runner --upload-dashboards ${provider}\n` +
          "Documentation: https://megalinter.io/latest/reporters/ApiReporter/"
      );
    }
  }

  isv4(release) {
    const isV4flag = release === "insiders" || release.includes("v4");
    return isV4flag;
  }

  isv5(release) {
    const isV5flag = release.includes("v5");
    return isV5flag;
  }

  checkPreviousVersion(release) {
    if (release.includes("v4") || release.includes("v5") || release.includes("v6")) {
      console.warn(
        c.bold(
          "#######################################################################"
        )
      );
      console.warn(
        c.bold(`MEGA-LINTER HAS A NEW ${DEFAULT_RELEASE} VERSION. Please upgrade to benefit of latest features :)`)
      );
      console.warn(
        c.bold(
          "- Running the command at the root of your repo (requires node.js): npx mega-linter-runner@latest --upgrade"
        )
      );
      console.warn(
        c.bold(
          `- or replace ${release} by ${DEFAULT_RELEASE} in your scripts`
        )
      );
      console.warn(
        c.bold(
          "#######################################################################"
        )
      );
    }
  }
}
