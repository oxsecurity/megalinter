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
import { DEFAULT_RELEASE } from "./config.js";
import { createEnv } from "yeoman-environment";
import { default as FindPackageJson } from "find-package-json";
import { load as yamlLoad } from "js-yaml";

function isSElinuxOn() {
  return ["Enforcing", "Permissive", "enforcing", "permissive"].includes(process.env.SELINUX_MODE);
}

export class MegaLinterRunner {

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

    // Run configuration generator
    if (options.install) {
      const env = createEnv();
      const __dirname = dirname(fileURLToPath(import.meta.url));
      const generatorPath = path.resolve(
        path.join(__dirname, "..", "generators", "mega-linter")
      );
      console.log("Yeoman generator used: " + generatorPath);
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
    if (options["containerName"]) {
      commandArgs.push(...["--name", options["containerName"]]);
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
    const spawnRes = spawnSync(this.containerEngine, commandArgs, spawnOptions);
    // Output json if requested
    if (options.json === true) {
      const reportSubFolder = options.linter
        ? path.join("megalinter-reports", options.linter.toLowerCase())
        : process.env.REPORT_OUTPUT_FOLDER || "report";
      const jsonOutputFile = path.join(
        lintPath,
        reportSubFolder,
        "mega-linter-report.json"
      );
      if (fs.existsSync(jsonOutputFile)) {
        const jsonRaw = await fs.readFile(jsonOutputFile, "utf8");
        console.log(JSON.stringify(JSON.parse(jsonRaw)));
      }
    }
    return spawnRes;
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
    };
    Object.keys(answers).forEach(
      (key) => answers[key] === undefined && delete answers[key]
    );
    return answers;
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
