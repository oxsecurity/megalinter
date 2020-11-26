#! /usr/bin/env node
"use strict";

const { MegaLinterRunner } = require("./runner");
const optionsDefinition = require("./options");

class MegaLinterRunnerCli {

    async run(argv) {
        const megaLinter = new MegaLinterRunner();
        const options = optionsDefinition.parse(argv);
        const { status } = await megaLinter.run(options);
        process.exitCode = status;
    }
}

module.exports = { MegaLinterRunnerCli };
