import { spawnSync, spawn } from "child_process";
import { default as c } from 'chalk';
import { default as fs } from "fs-extra";
import * as https from 'https';
import { default as open } from 'open';
import * as path from "path";
import which from "which";
import { asciiArtCodeTotal } from "./ascii.js";

export class CodeTotalRunner {
  constructor(options = {}) {
    this.options = options;
  }

  async run() {
    console.log(asciiArtCodeTotal());

    // Retrieve docker-compose
    if (!fs.existsSync(path.join(process.cwd(), 'docker-compose.yml'))) {
      const dockerComposeUrl = "https://raw.githubusercontent.com/oxsecurity/codetotal/main/docker-compose.yml";
      console.info(c.cyan(`Downloading latest docker-compose.yml from ${c.bold(dockerComposeUrl)} ...`));
      https.get(dockerComposeUrl, resp => resp.pipe(fs.createWriteStream(path.join(process.cwd(), 'docker-compose.yml'))));
      await new Promise(r => setTimeout(r, 2000));
    }

    // Check for docker installation
    const whichPromise = which("docker");
    whichPromise.catch(() => {
      console.error(c.red(`
    ERROR: Docker engine has not been found on your system.
    - to run CodeTotal locally, please install docker desktop: https://www.docker.com/products/docker-desktop`));
    });

    // Get platform to use with docker pull & run
    const imagesPlatform = this.options.platform || "linux/amd64";
    const platformVars = {
      "DOCKER_DEFAULT_PLATFORM": imagesPlatform
    };

    // Pull docker image
    if (this.options.nodockerpull !== true) {
      console.info(c.cyan(`Pulling docker-compose.yml images...`));
      console.info(c.grey(
        "INFO: this operation can be long during the first use of CodeTotal"
      ));
      console.info(c.grey(
        "The next runs, it will be immediate (thanks to docker cache !)"
      ));
      console.log("Running command: " + c.whiteBright(c.bgGray("docker-compose " + ["-f", "docker-compose.yml", "pull"].join(" "))));
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
    const uiUrl = this.options["codetotal-url"] || "http://localhost:8081/";
    let interval = setInterval(async () => {
      let response;
      try {
        response = await fetch(uiUrl);
      } catch (e) {
        // URL not available yet
        return;
      }
      const statusCode = response.status;
      if (statusCode >= 200 && statusCode <= 400 && isOpen === false) {
        clearInterval(interval);
        isOpen = true;
        console.log(c.green("CodeTotal is started: opening " + uiUrl + " ..."));
        open(uiUrl);
        console.log(c.yellow("Hit CTRL+C to terminate"));
      }
    }, 2000);

    // Call docker run
    console.log("Running command: " + c.whiteBright(c.bgGray("docker-compose " + commandArgs.join(" "))));
    const spawnOptions = {
      stdio: "inherit",
      windowsHide: true,
      env: { ...process.env, ...platformVars }
    };
    const spawnRes = spawn("docker-compose", commandArgs, spawnOptions);
    return spawnRes;
  }
}

