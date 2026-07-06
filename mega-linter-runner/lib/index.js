#! /usr/bin/env node

import { MegaLinterRunner } from "./runner.js";
import { MegaLinterRunnerCli } from "./cli.js";

import { realpathSync } from "fs";
import { pathToFileURL } from "url";

// Run only if called by script
// This check handles symlinks as well
// See https://stackoverflow.com/a/71925565 and
// https://exploringjs.com/nodejs-shell-scripting/ch_nodejs-path.html#detecting-if-module-is-main
function wasCalledAsScript() {
  // We use realpathSync to resolve symlinks, as cli scripts will often
  // be executed from symlinks in the `node_modules/.bin`-folder
  const realPath = realpathSync(process.argv[1]);

  // Convert the file-path to a file-url before comparing it
  const realPathAsUrl = pathToFileURL(realPath).href;

  return import.meta.url === realPathAsUrl;
}

// Run asynchronously to use the returned status for process.exit
if (wasCalledAsScript()) {
  (async () => {
    await new MegaLinterRunnerCli().run(process.argv);
  })();
}

export { MegaLinterRunner, MegaLinterRunnerCli };
