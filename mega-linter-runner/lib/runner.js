import { optionsDefinition } from "./options.js"
import { spawnSync } from "child_process";
import { default as c } from 'chalk';
import * as path from 'path';
import { dirname } from 'path';
import { fileURLToPath } from 'url';
import which from "which";
import { default as fs } from "fs-extra";
import { MegaLinterUpgrader } from "./upgrade.js";
import { CodeTotalRunner } from "./codetotal.js";
import { DEFAULT_RELEASE } from "./config.js";
import { createEnv} from "yeoman-environment";
import { default as FindPackageJson } from "find-package-json";

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
      env.run(generatorPath);
      return { status: 0 };
    }

    // Run upgrader from v4 to v5
    if (options.upgrade) {
      const megaLinterUpgrader = new MegaLinterUpgrader();
      await megaLinterUpgrader.run();
      return { status: 0 };
    }

    if (options.codetotal) {
      const codeTotalRunner = new CodeTotalRunner(options);
      await codeTotalRunner.run();
      return { status: 0 }
    }

    // Build MegaLinter docker image name with flavor and release version
    const release = options.release in ["stable"] ? DEFAULT_RELEASE : options.release;
    const dockerImageName =
      // v4 retrocompatibility >>
      (options.flavor === "all" || options.flavor == null) && this.isv4(release)
        ? "nvuillam/mega-linter"
        : options.flavor !== "all" && this.isv4(release)
          ? `nvuillam/mega-linter-${options.flavor}`
          : // << v4 retrocompatibility
          // v5 retrocompatibility >>
          (options.flavor === "all" || options.flavor == null) &&
            this.isv5(release)
            ? "megalinter/megalinter"
            : options.flavor !== "all" && this.isv5(release)
              ? `megalinter/megalinter-${options.flavor}`
              : // << v5 retrocompatibility
              options.flavor === "all" || options.flavor == null
                ? "oxsecurity/megalinter"
                : `oxsecurity/megalinter-${options.flavor}`;
    this.checkPreviousVersion(release);
    const dockerImage = options.image || `${dockerImageName}:${release}`; // Docker image can be directly sent in options

    // Check for docker installation
    const whichPromise = which("docker");
    whichPromise.catch(() => {
      console.error(`
ERROR: Docker engine has not been found on your system.
- to run MegaLinter locally, please install docker desktop: https://www.docker.com/products/docker-desktop
- to run docker on CI, use a base image containing docker engine`);
    });

    // Get platform to use with docker pull & run
    const imagePlatform = options.platform || "linux/amd64";

    // Pull docker image
    if (options.nodockerpull !== true) {
      console.info(`Pulling docker image ${dockerImage} ... `);
      console.info(
        "INFO: this operation can be long during the first use of mega-linter-runner"
      );
      console.info(
        "The next runs, it will be immediate (thanks to docker cache !)"
      );
      const spawnResPull = spawnSync(
        "docker",
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
    const commandArgs = ["run", "--platform", imagePlatform];
    const removeContainer = options["removeContainer"] ? true: options["noRemoveContainer"] ? false: true ;
    if (removeContainer) {
      commandArgs.push("--rm");
    }
    if (options["containerName"]) {
      commandArgs.push(...["--name", options["containerName"]]);
    }
    commandArgs.push(...["-v", "/var/run/docker.sock:/var/run/docker.sock:rw"]);
    commandArgs.push(...["-v", `${lintPath}:/tmp/lint:rw`]);
    if (options.fix === true) {
      commandArgs.push(...["-e", "APPLY_FIXES=all"]);
    }
    if (options.debug === true) {
      commandArgs.push(...["-e", "LOG_LEVEL=DEBUG"]);
    }
    if (options.json === true) {
      commandArgs.push(...["-e", "JSON_REPORTER=true"]);
    }
    if (options.env) {
      for (const envVarEqualsValue of options.env) {
        commandArgs.push(...["-e", envVarEqualsValue]);
      }
    }
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

    // Call docker run
    console.log(`Command: docker ${commandArgs.join(" ")}`);
    const spawnOptions = {
      env: Object.assign({}, process.env),
      stdio: "inherit",
      windowsHide: true,
    };
    const spawnRes = spawnSync("docker", commandArgs, spawnOptions);
    // Output json if requested
    if (options.json === true) {
      const jsonOutputFile = path.join(
        lintPath,
        process.env.REPORT_OUTPUT_FOLDER || "report",
        "mega-linter-report.json"
      );
      if (fs.existsSync(jsonOutputFile)) {
        const jsonRaw = await fs.readFile(jsonOutputFile, "utf8");
        console.log(JSON.stringify(JSON.parse(jsonRaw)));
      }
    }
    return spawnRes;
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
