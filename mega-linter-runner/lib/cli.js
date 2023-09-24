#! /usr/bin/env node
import { MegaLinterRunner } from "./runner.js";
import {optionsDefinition} from "./options.js";

export class MegaLinterRunnerCli {
  async run(argv) {
    const megaLinter = new MegaLinterRunner();
    const options = optionsDefinition.parse(argv);
    const res = await megaLinter.run(options);
    process.exitCode = res.status;
  }
}
