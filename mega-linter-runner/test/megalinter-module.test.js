import { MegaLinterRunner } from "../lib/index.js";
import assert from 'assert';

const release = process.env.MEGALINTER_RELEASE || "beta";
const nodockerpull =
  process.env.MEGALINTER_NO_DOCKER_PULL === "true" ? true : false;

describe("Module", function () {
  it("(Module) Show help", async () => {
    const options = {
      help: true,
    };
    const res = await new MegaLinterRunner().run(options);
    assert(res.status === 0, `status is 0 (${res.status} returned)`);
    assert(
      res.stdout.includes("mega-linter [options]"),
      "stdout contains help content"
    );
  });

  it("(Module) Show version", async () => {
    const options = {
      version: true,
    };
    const res = await new MegaLinterRunner().run(options);
    assert(res.status === 0, `status is 0 (${res.status} returned)`);
    assert(
      res.stdout.includes("mega-linter-runner version"),
      'stdout should contains "mega-linter-runner version"'
    );
  });

  /*
Disabled until find a way to run with default options
    it('(Module) Run installer', async () => {
        const options = {
            install: true
        }
        const res = await new MegaLinterRunner().run(options)
        assert(res.status === 0, `status is 0 (${res.status} returned)`)
    })
*/

  it("(Module) List vars without pattern", async () => {
    const options = {
      listVars: true,
      _: [],
    };
    const res = await new MegaLinterRunner().run(options);
    assert(res.status === 0, `status is 0 (${res.status} returned)`);
    assert(
      res.stdout.includes("MegaLinter variables"),
      'stdout should contain "MegaLinter variables"'
    );
    assert(
      res.stdout.includes("LOG_LEVEL"),
      "stdout should list LOG_LEVEL variable"
    );
  });

  it("(Module) List vars with pattern", async () => {
    const options = {
      listVars: true,
      _: ["LOG_LEVEL"],
    };
    const res = await new MegaLinterRunner().run(options);
    assert(res.status === 0, `status is 0 (${res.status} returned)`);
    assert(
      res.stdout.includes("LOG_LEVEL"),
      "stdout should contain filtered LOG_LEVEL variable"
    );
  });

  it("(Module) Help for a specific option", async () => {
    const options = {
      help: true,
      _: ["env"],
    };
    const res = await new MegaLinterRunner().run(options);
    assert(res.status === 0, `status is 0 (${res.status} returned)`);
    assert(
      res.stdout.includes("--env") || res.stdout.includes("KEY=VALUE"),
      "stdout should describe the --env option"
    );
  });

  it("(Module) run on own code base", async () => {
    const options = {
      path: "./..",
      release,
      nodockerpull,
      env: ["ENABLE=YAML"],
    };
    if (process.env.MEGALINTER_IMAGE) {
      options.image = process.env.MEGALINTER_IMAGE;
    }
    const res = await new MegaLinterRunner().run(options);
    assert(res.status === 0, `status is 0 (${res.status} returned)`);
  }).timeout(600000);
});
