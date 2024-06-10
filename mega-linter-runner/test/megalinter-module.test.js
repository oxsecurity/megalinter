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
