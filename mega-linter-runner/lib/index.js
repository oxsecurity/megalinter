#! /usr/bin/env node

import { MegaLinterRunner } from "./runner.js";
const { MegaLinterRunnerCli } = require("./cli");

// Run only if called by script
const runningAsScript = !module.parent;

// Run asynchronously to use the returned status for process.exit
if (runningAsScript) {
  (async () => {
    await new MegaLinterRunnerCli().run(process.argv);
  })();
}

export { MegaLinterRunner, MegaLinterRunnerCli };
