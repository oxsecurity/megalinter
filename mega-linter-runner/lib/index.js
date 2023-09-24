#! /usr/bin/env node

import { MegaLinterRunner } from "./runner.js";
import { MegaLinterRunnerCli } from "./cli.js";

// Run only if called by script
const runningAsScript = (this === undefined);

// Run asynchronously to use the returned status for process.exit
if (runningAsScript) {
  (async () => {
    await new MegaLinterRunnerCli().run(process.argv);
  })();
}

export { MegaLinterRunner, MegaLinterRunnerCli };
