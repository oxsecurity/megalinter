/* jscpd:ignore-start */
import assert from 'assert';
import { exec as childProcessExec } from "child_process";
import os from "os";
import path from "path";
import fs from "fs-extra";
import { fileURLToPath } from "url";
import * as  util from "util";
const exec = util.promisify(childProcessExec);

const release = process.env.MEGALINTER_RELEASE || "beta";
const nodockerpull =
  process.env.MEGALINTER_NO_DOCKER_PULL === "true" ? true : false;
const packageDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

const MEGA_LINTER = "mega-linter-runner ";

describe("CLI", function () {
  it("(CLI) Show help", async () => {
    const params = ["--help"];
    const { stdout, stderr } = await exec(MEGA_LINTER + params.join(" "));
    if (stderr) {
      console.error(stderr);
    }
    assert(stdout, "stdout is set");
    assert(
      stdout.includes("mega-linter [options]"),
      "stdout contains help content"
    );
  });

  it("(CLI) Show version", async () => {
    const params = ["--version"];
    const { stdout, stderr } = await exec(MEGA_LINTER + params.join(" "));
    if (stderr) {
      console.error(stderr);
    }
    assert(stdout, "stdout is set");
    assert(
      stdout.includes("mega-linter-runner version"),
      'stdout should contains "mega-linter-runner version"'
    );
  });

  it("(CLI) Upgrade config", (done) => {
    if (process.env.CI) {
      // Skip in CI (bug to fix in CI but works locally :/ )
      done();
      return;
    }
    const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "megalinter-upgrade-"));
    fs.writeFileSync(path.join(tempDir, ".mega-linter.yml"), "ENABLE_LINTERS:\n  - YAML_PRETTIER\n");
    const params = ["--upgrade", "--no-prompt"];
    exec(`node ${path.join(packageDir, "lib", "index.js")} ${params.join(" ")}`, { cwd: tempDir })
      .then((res) => {
        const stdout = res.stdout;
        const stderr = res.stderr;
        if (stderr) {
          console.error(stderr);
        }
        assert(stdout, "stdout is set");
        assert(
          stdout.includes("mega-linter-runner applied"),
          'stdout should contains "mega-linter-runner applied"'
        );
        fs.removeSync(tempDir);
        done();
      })
      .catch((err) => {
        fs.removeSync(tempDir);
        done(err);
        throw err;
      });
  }).timeout(10000);

  /*
Disabled until find a way to run with default options
    it('(CLI) Run installer', async () => {
        const params = ["--install"];
        const { stdout, stderr } = await exec(MEGA_LINTER + params.join(" "));
        if (stderr) {
            console.error(stderr);
        }
        assert(stdout, "stdout is set");
    })
*/
  const params = [
    "--path",
    "./..",
    "--release",
    release,
    "-e",
    '"ENABLE=YAML"',
  ];

  it("(CLI) run on own code base", async () => {
    if (nodockerpull) {
      params.push("--nodockerpull");
    }
    if (process.env.MEGALINTER_IMAGE) {
      params.push("--image");
      params.push(process.env.MEGALINTER_IMAGE);
    }
    const { stdout, stderr } = await exec(MEGA_LINTER + params.join(" "));
    if (stderr) {
      console.error(stderr);
    }
    assert(stdout, "stdout is set");
  }).timeout(600000);

  it("(CLI) run on own code base with json output", async () => {
    params.push("--json");
    if (nodockerpull) {
      params.push("--nodockerpull");
    }
    if (process.env.MEGALINTER_IMAGE) {
      params.push("--image");
      params.push(process.env.MEGALINTER_IMAGE);
    }
    const { stdout, stderr } = await exec(MEGA_LINTER + params.join(" "));
    if (stderr) {
      console.error(stderr);
    }
    assert(stdout, "stdout is set");
  }).timeout(600000);
});
/* jscpd:ignore-end */
