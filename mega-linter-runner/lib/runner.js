#! /usr/bin/env node
"use strict";
const optionsDefinition = require("./options");
const { spawnSync } = require("child_process");
const path = require("path");
const which = require("which");
const fs = require("fs-extra");
const { MegaLinterUpgrader } = require("./upgrade");

class MegaLinterRunner {

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
          const FindPackageJson = require("find-package-json");
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
      const yeoman = require("yeoman-environment");
      const env = yeoman.createEnv();
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
      return { status: 0 }
    }

    // Build Mega-Linter docker image name with flavor and release version
    const release =
      options.release in ["stable"]
        ? "v5"
        : options.release;
    const dockerImageName =
      // v4 retrocompatibility >>
      ((options.flavor === "all" || options.flavor == null) && this.isv4(release))
        ? "nvuillam/mega-linter"
        : ((options.flavor === "all" || options.flavor == null && this.isv4(release))) ?
          `nvuillam/mega-linter-${options.flavor}` :
          // << v4 retrocompatibility 
          options.flavor === "all" || options.flavor == null
            ? "megalinter/megalinter"
            : `megalinter/megalinter-${options.flavor}`;
    const dockerImage = options.image || `${dockerImageName}:${release}`; // Docker image can be directly sent in options

    // Check for docker installation
    const whichPromise = which("docker");
    whichPromise.catch(() => {
      console.error(`
ERROR: Docker engine has not been found on your system.
- to run Mega-Linter locally, please install docker desktop: https://www.docker.com/products/docker-desktop
- to run docker on CI, use a base image containing docker engine`);
    });

    // Pull docker image
    if (options.nodockerpull !== true) {
      console.info(`Pulling docker image ${dockerImage} ... `);
      console.info(
        "INFO: this operation can be long during the first use of mega-linter-runner"
      );
      console.info(
        "The next runs, it will be immediate (thanks to docker cache !)"
      );
      const spawnResPull = spawnSync("docker", ["pull", dockerImage], {
        detached: false,
        stdio: "inherit",
        windowsHide: true,
        windowsVerbatimArguments: true,
      });
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
    const commandArgs = [
      "run",
      "-v",
      "/var/run/docker.sock:/var/run/docker.sock:rw",
      "-v",
      `${lintPath}:/tmp/lint:rw`,
    ];
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
    commandArgs.push(dockerImage);

    // Call docker run
    console.log(`Command: docker ${commandArgs.join(" ")}`);
    const spawnOptions = {
      detached: false,
      cwd: process.cwd(),
      env: Object.assign({}, process.env),
      stdio: "inherit",
      windowsHide: true,
      windowsVerbatimArguments: true,
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
    return {
      status: spawnRes.status,
      stdout: spawnRes.stdout,
      stderr: spawnRes.stderr,
    };
  }

  isv4(release) {
    const isV4flag = release === 'insiders' || release.includes('v4');
    if (isV4flag) {
      console.warn(c.yellow("#######################################################################"));
      console.warn(c.yellow("MEGA-LINTER HAS A NEW V5 VERSION. Please upgrade to it by:"));
      console.warn(c.yellow("- Running the command at the root of your repo (requires node.js): npx mega-linter-runner --upgrade"));
      console.warn(c.yellow("- Replace versions used by latest (v5 latest stable version) or beta (previously 'insiders', content of main branch of megalinter/megalinter)"));
      console.warn(c.yellow("#######################################################################"));
    }
    return isV4flag;
  }
}

module.exports = { MegaLinterRunner };
