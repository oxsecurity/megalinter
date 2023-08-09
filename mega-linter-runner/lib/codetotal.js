#! /usr/bin/env node
"use strict";
const { spawnSync, spawn } = require("child_process");
const fs = require("fs-extra");
const https = require('https');
const open = require("open");
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
    if (!fs.existsSync(path.join(process.cwd(), 'docker-compose.yml'))) {
      const dockerComposeUrl = "https://raw.githubusercontent.com/oxsecurity/codetotal/main/docker-compose.yml";
      console.info(`Downloading latest docker-compose.yml from ${dockerComposeUrl}`);
      https.get(dockerComposeUrl, resp => resp.pipe(fs.createWriteStream(path.join(process.cwd(), 'docker-compose.yml'))));
      await new Promise(r => setTimeout(r, 2000));
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
    const platformVars = {
      "DOCKER_DEFAULT_PLATFORM": imagesPlatform
    };

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
        ["-f", "docker-compose.yml", "pull"],
        {
          detached: false,
          stdio: "inherit",
          windowsHide: true,
          windowsVerbatimArguments: true,
          env: { ...process.env, ...platformVars }
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
    const commandArgs = ["-f", "docker-compose.yml", "up"];

    // Prepare interval to check localhost is open
    let isOpen = false;
    const uiUrl = "http://localhost:8081/";
    let interval = setInterval(async () => {
      let response;
      try {
       response = await fetch(uiUrl);
      } catch (e) {
        // URL not available yet
        return ;
      }
      const statusCode = response.status;
      if (statusCode >= 200 && statusCode <= 400 && isOpen === false) {
        clearInterval(interval);
        isOpen = true;
        console.log("CodeTotal is started: opening " + uiUrl + " ...");
        open(uiUrl);
      }
    }, 2000);

    // Call docker run
    console.log(`Command: docker-compose ${commandArgs.join(" ")}`);
    const spawnOptions = {
      stdio: "inherit",
      windowsHide: true,
      env: { ...process.env, ...platformVars }
    };
    const spawnRes = spawn("docker-compose", commandArgs, spawnOptions);
    return spawnRes;
  }
}

module.exports = { CodeTotalRunner };
