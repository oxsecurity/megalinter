#! /usr/bin/env node
"use strict";

const { MegaLinterRunner } = require("./runner");
const optionsDefinition = require("./options");

class MegaLinterRunnerCli {
  async run(argv) {
    const megaLinter = new MegaLinterRunner();
    const options = optionsDefinition.parse(argv);
    const res = await megaLinter.run(options);
    process.exitCode = res.status;
  }
}

module.exports = { MegaLinterRunnerCli };
