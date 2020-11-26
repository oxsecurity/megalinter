#! /usr/bin/env node
"use strict";
const optionsDefinition = require("./options");
const { spawnSync } = require("child_process");
const path = require("path")

class MegaLinterRunner {

    async run(options) {

        // Show help ( index or for an options)
        if (this.options.help) {
            if (this.options._.length) {
                this.outputString = optionsDefinition.generateHelpForOption(this.options._[0]);
            } else {
                this.outputString = optionsDefinition.generateHelp();
            }
            console.info(this.outputString);
            return;
        }

        // Show version
        if (this.options.version) {
            let v = process.env.npm_package_version;
            if (!v) {
                try {
                    const FindPackageJson = require("find-package-json");
                    const finder = FindPackageJson(__dirname);
                    v = finder.next().value.version;
                } catch {
                    v = "error";
                }
            }
            console.log(`mega-linter-runner version ${v}`);
            return
        }

        // Build Mega-Linter docker image name with release version
        const release = (options.release in ["v4", "stable"]) ? "v4" :
            (options.release == "insiders") ? "latest" :
                (options.release) ? options.release :
                    "v4"
        const dockerImage = `nvuillam/mega-linter:${release}`

        // Pull docker image
        if (options.nodockerpull !== true) {
            console.info(`Pulling docker image ${dockerImage} ... `)
            console.info("this operation can be long during the first use of mega-linter-runner, but will be much faster later thanks to docker cache)")
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
        }
        else {
            console.log(`Skipped pull of ${dockerImage} (--nodockerpull used)`)
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
