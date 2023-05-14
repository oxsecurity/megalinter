#! /usr/bin/env node
"use strict";
/* jscpd:ignore-start */
const assert = require("assert");
const childProcess = require("child_process");
const util = require("util");
const exec = util.promisify(childProcess.exec);

const release = process.env.MEGALINTER_RELEASE || "beta";
const nodockerpull =
  process.env.MEGALINTER_NO_DOCKER_PULL === "true" ? true : false;

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
    const params = ["--upgrade"];
    exec(MEGA_LINTER + params.join(" "))
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
        done();
      })
      .catch((err) => {
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
    const { stdout, stderr } = await exec(MEGA_LINTER + params.join(" "));
    if (stderr) {
      console.error(stderr);
    }
    assert(stdout, "stdout is set");
  }).timeout(600000);
});
/* jscpd:ignore-end */
