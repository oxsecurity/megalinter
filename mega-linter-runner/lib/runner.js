#! /usr/bin/env node
const { spawnSync } = require("child_process");
const { assert } = require("console");
const path = require("path")

class MegaLinterRunner {
    "use strict";

    async run(options) {
        // Build Mega-Linter docker image name with release version
        const release = (options.release in ["v4", "stable"]) ? "v4" :
            (options.release == "insiders") ? "latest" :
                (options.release) ? options.release :
                    "v4"

        // Pull docker image
        const dockerImage = `nvuillam/mega-linter:${release}`
        const spawnResPull = spawnSync(
            "docker",
            ["pull", dockerImage],
            {
                detached: false, stdio: "inherit",
                windowsHide: true,
                windowsVerbatimArguments: true
            });
        if (spawnResPull.status !== 0) {
            throw new Error(`Unable to pull ${dockerImage}: \n${spawnResPull.stderr}`)
        }

        // Build docker run options
        const lintPath = path.resolve(options.path || ".")
        const commandArgs = [
            "run",
            "-v", `${lintPath}:/tmp/lint`
        ]
        if (options.fix === true) {
            commandArgs.push(...["-e", "APPLY_FIXES=all"])
        }
        if (options.debug === true) {
            commandArgs.push(...["-e", "LOG_LEVEL=DEBUG"])
        }
        commandArgs.push(dockerImage)

        // Call docker run
        console.log(`Command: docker ${commandArgs.join(" ")}`);
        const spawnOptions = {
            detached: false,
            cwd: process.cwd(),
            env: Object.assign({}, process.env),
            stdio: "inherit",
            windowsHide: true,
            windowsVerbatimArguments: true
        };
        const spawnRes = spawnSync("docker", commandArgs, spawnOptions);
        process.exitCode = spawnRes.status
    }
}

module.exports = { MegaLinterRunner };
