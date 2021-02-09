#! /usr/bin/env node
"use strict";

const { MegaLinterRunner } = require("./runner");
const { MegaLinterRunnerCli } = require("./cli");

// Run only if called by script
const runningAsScript = !module.parent;

// Run asynchronously to use the returned status for process.exit
if (runningAsScript) {
  (async () => {
    await new MegaLinterRunnerCli().run(process.argv);
  })();
}

module.exports = { MegaLinterRunner, MegaLinterRunnerCli };
