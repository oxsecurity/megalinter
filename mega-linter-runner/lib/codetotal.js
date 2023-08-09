#! /usr/bin/env node
"use strict";
const { spawnSync } = require("child_process");
const fs = require("fs-extra");
const https = require('https');
const path = require("path");
const which = require("which");
const { asciiArtCodeTotal } = require("./ascii");

class CodeTotalRunner {
  constructor(options = {}) {
    this.options = options;
  }

  async run() {
    console.log(asciiArtCodeTotal());

    // Retrieve docker-compose
    if (!fs.existsSync(path.join(process.cwd(),'docker-compose.yml'))) {
      const dockerComposeUrl = "https://raw.githubusercontent.com/oxsecurity/codetotal/main/docker-compose.yml";
      console.info(`Downloading latest docker-compose.yml from ${dockerComposeUrl}`);
      https.get(dockerComposeUrl, resp => resp.pipe(fs.createWriteStream(path.join(process.cwd(),'docker-compose.yml'))));
    }

    // Check for docker installation
    const whichPromise = which("docker");
    whichPromise.catch(() => {
      console.error(`
    ERROR: Docker engine has not been found on your system.
    - to run CodeTotal locally, please install docker desktop: https://www.docker.com/products/docker-desktop`);
    });

    // Get platform to use with docker pull & run
    const imagesPlatform = this.options.platform || "linux/amd64";

    // Pull docker image
    if (this.options.nodockerpull !== true) {
      console.info(`Pulling docker-compose.yml images... `);
      console.info(
        "INFO: this operation can be long during the first use of CodeTotal"
      );
      console.info(
        "The next runs, it will be immediate (thanks to docker cache !)"
      );
      const spawnResPull = spawnSync(
        "docker-compose",
        ["-f", "docker-compose.yml", "--platform", imagesPlatform, "pull"],
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
          errorMsg: `Unable to pull docker images: \n${JSON.stringify(
            spawnResPull,
            null,
            2
          )}`,
        };
      }
    } else {
      console.log(`Skipped pull of docker images (--nodockerpull used)`);
    }

    // Prepare docker-compose command
    const commandArgs = ["--platform", imagesPlatform, "-f", "docker-compose.yml", "up"];

    // Call docker run
    console.log(`Command: docker-compose ${commandArgs.join(" ")}`);
    const spawnOptions = {
      env: Object.assign({}, process.env),
      stdio: "inherit",
      windowsHide: true,
    };
    const spawnRes = spawnSync("docker-compose", commandArgs, spawnOptions);
    return spawnRes;
  }
}

module.exports = { CodeTotalRunner };
