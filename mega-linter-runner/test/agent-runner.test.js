import assert from "assert";
import * as path from "path";
import os from "os";
import fs from "fs-extra";
import { MegaLinterRunner } from "../lib/runner.js";
import { optionsDefinition } from "../lib/options.js";
import { DEFAULT_RELEASE } from "../lib/config.js";

function parse(argv) {
  return optionsDefinition.parse(["node", "mega-linter-runner", ...argv]);
}

const runner = new MegaLinterRunner();

describe("CLI parsing — agent options", () => {
  it("parses --linter", () => {
    const o = parse(["--linter", "PYTHON_RUFF"]);
    assert.strictEqual(o.linter, "PYTHON_RUFF");
  });

  it("parses --linter with positional files", () => {
    const o = parse(["--linter", "PYTHON_RUFF", "src/a.py", "src/b.py"]);
    assert.deepStrictEqual(o._, ["src/a.py", "src/b.py"]);
  });

  it("rejects --linter combined with --flavor", () => {
    assert.throws(() => parse(["--linter", "PYTHON_RUFF", "--flavor", "python"]));
  });

  it("rejects --linter combined with --image", () => {
    assert.throws(() =>
      parse(["--linter", "PYTHON_RUFF", "--image", "ghcr.io/oxsecurity/megalinter:latest"])
    );
  });

  it("parses setup options", () => {
    const o = parse([
      "--install",
      "--no-prompt",
      "--setup-ci",
      "gitLabCI",
      "--no-setup-copy-paste",
      "--setup-spelling-mistakes",
      "--setup-default-branch",
      "develop",
      "--setup-validate-all-code-base",
      "diff",
      "--no-setup-ox",
    ]);
    assert.strictEqual(o.install, true);
    assert.strictEqual(o.prompt, false);
    assert.strictEqual(o.setupCi, "gitLabCI");
    assert.strictEqual(o.setupCopyPaste, false);
    assert.strictEqual(o.setupSpellingMistakes, true);
    assert.strictEqual(o.setupDefaultBranch, "develop");
    assert.strictEqual(o.setupValidateAllCodeBase, "diff");
    assert.strictEqual(o.setupOx, false);
  });
});

describe("Docker image resolution", () => {
  it("defaults to main image with latest when nothing is defined", () => {
    const res = runner.resolveDockerImage({}, {});
    assert.strictEqual(res.dockerImage, "ghcr.io/oxsecurity/megalinter:latest");
  });

  it("uses MEGALINTER_FLAVOR and MEGALINTER_VERSION from .mega-linter.yml", () => {
    const res = runner.resolveDockerImage(
      {},
      { MEGALINTER_FLAVOR: "python", MEGALINTER_VERSION: "v9.1.0" }
    );
    assert.strictEqual(
      res.dockerImage,
      "ghcr.io/oxsecurity/megalinter-python:v9.1.0"
    );
  });

  it("CLI flags override .mega-linter.yml values", () => {
    const res = runner.resolveDockerImage(
      { flavor: "javascript", release: "beta" },
      { MEGALINTER_FLAVOR: "python", MEGALINTER_VERSION: "v9.1.0" }
    );
    assert.strictEqual(
      res.dockerImage,
      "ghcr.io/oxsecurity/megalinter-javascript:beta"
    );
  });

  it("--image overrides everything", () => {
    const res = runner.resolveDockerImage(
      { image: "my-registry.com/megalinter:custom" },
      { MEGALINTER_FLAVOR: "python" }
    );
    assert.strictEqual(res.dockerImage, "my-registry.com/megalinter:custom");
  });

  it("maps stable release to the default release", () => {
    const res = runner.resolveDockerImage({ release: "stable" }, {});
    assert.strictEqual(
      res.dockerImage,
      `ghcr.io/oxsecurity/megalinter:${DEFAULT_RELEASE}`
    );
  });

  it("resolves standalone linter image from --linter", () => {
    const res = runner.resolveDockerImage({ linter: "PYTHON_RUFF" }, {});
    assert.strictEqual(
      res.dockerImage,
      "ghcr.io/oxsecurity/megalinter-only-python_ruff:latest"
    );
  });

  it("standalone linter image uses MEGALINTER_VERSION from config", () => {
    const res = runner.resolveDockerImage(
      { linter: "MARKDOWN_MARKDOWNLINT" },
      { MEGALINTER_VERSION: "beta" }
    );
    assert.strictEqual(
      res.dockerImage,
      "ghcr.io/oxsecurity/megalinter-only-markdown_markdownlint:beta"
    );
  });
});

describe("APPLY_FIXES resolution", () => {
  it("injects APPLY_FIXES=all with --fix and no config value", () => {
    assert.deepStrictEqual(runner.applyFixesEnvArgs({ fix: true }, {}), [
      "-e",
      "APPLY_FIXES=all",
    ]);
  });

  it("injects nothing without --fix and no config value", () => {
    assert.deepStrictEqual(runner.applyFixesEnvArgs({}, {}), []);
  });

  it("does not override an APPLY_FIXES list from .mega-linter.yml with --fix", () => {
    assert.deepStrictEqual(
      runner.applyFixesEnvArgs(
        { fix: true },
        { APPLY_FIXES: ["JAVASCRIPT_ES", "MARKDOWN_MARKDOWNLINT"] }
      ),
      []
    );
  });

  it("does not override APPLY_FIXES=all from .mega-linter.yml", () => {
    assert.deepStrictEqual(
      runner.applyFixesEnvArgs({ fix: true }, { APPLY_FIXES: "all" }),
      []
    );
  });

  it("injects APPLY_FIXES=all with --fix when config says none", () => {
    assert.deepStrictEqual(
      runner.applyFixesEnvArgs({ fix: true }, { APPLY_FIXES: "none" }),
      ["-e", "APPLY_FIXES=all"]
    );
  });
});

describe("Standalone linter env args", () => {
  it("returns nothing without --linter", () => {
    assert.deepStrictEqual(runner.standaloneLinterEnvArgs({}), []);
  });

  it("activates the linter and isolates its reports", () => {
    assert.deepStrictEqual(
      runner.standaloneLinterEnvArgs({ linter: "python_ruff" }),
      [
        "-e",
        "ENABLE_LINTERS=PYTHON_RUFF",
        "-e",
        "REPORT_OUTPUT_FOLDER=/tmp/lint/megalinter-reports/python_ruff",
      ]
    );
  });

  it("respects a user-provided REPORT_OUTPUT_FOLDER", () => {
    assert.deepStrictEqual(
      runner.standaloneLinterEnvArgs({
        linter: "PYTHON_RUFF",
        env: ["REPORT_OUTPUT_FOLDER=/tmp/lint/custom"],
      }),
      ["-e", "ENABLE_LINTERS=PYTHON_RUFF"]
    );
  });
});

describe("Local .mega-linter.yml config reading", () => {
  it("returns an empty object when the file is missing", async () => {
    const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "ml-cfg-"));
    assert.deepStrictEqual(runner.readLocalConfig(tmpDir), {});
  });

  it("reads flavor, version and fixes properties", async () => {
    const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "ml-cfg-"));
    await fs.writeFile(
      path.join(tmpDir, ".mega-linter.yml"),
      "MEGALINTER_FLAVOR: python\nMEGALINTER_VERSION: v9\nAPPLY_FIXES: all\n"
    );
    const config = runner.readLocalConfig(tmpDir);
    assert.strictEqual(config.MEGALINTER_FLAVOR, "python");
    assert.strictEqual(config.MEGALINTER_VERSION, "v9");
    assert.strictEqual(config.APPLY_FIXES, "all");
  });

  it("ignores an unparsable file", async () => {
    const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "ml-cfg-"));
    await fs.writeFile(
      path.join(tmpDir, ".mega-linter.yml"),
      "invalid: [unclosed\n  - :::\n"
    );
    assert.deepStrictEqual(runner.readLocalConfig(tmpDir), {});
  });
});

describe("Setup targets backup", () => {
  it("backs up pre-existing generator targets", async () => {
    const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "ml-bak-"));
    await fs.writeFile(path.join(tmpDir, ".mega-linter.yml"), "APPLY_FIXES: all\n");
    await fs.mkdirp(path.join(tmpDir, ".github", "workflows"));
    await fs.writeFile(
      path.join(tmpDir, ".github", "workflows", "mega-linter.yml"),
      "name: custom\n"
    );
    const backedUp = runner.backupExistingSetupTargets(tmpDir);
    assert.deepStrictEqual(backedUp, [
      ".mega-linter.yml",
      path.join(".github", "workflows", "mega-linter.yml"),
    ]);
    assert.strictEqual(
      await fs.readFile(
        path.join(tmpDir, ".mega-linter.yml.megalinter-setup.bak"),
        "utf8"
      ),
      "APPLY_FIXES: all\n"
    );
    assert.ok(
      fs.existsSync(
        path.join(
          tmpDir,
          ".github",
          "workflows",
          "mega-linter.yml.megalinter-setup.bak"
        )
      )
    );
  });

  it("returns an empty list when nothing pre-exists", async () => {
    const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "ml-bak-"));
    assert.deepStrictEqual(runner.backupExistingSetupTargets(tmpDir), []);
  });
});

describe("Timeout handling", () => {
  function makeRunnerWithFakeEngine({ timeoutOnRun }) {
    const r = new MegaLinterRunner();
    const calls = [];
    r.spawnSyncFn = (cmd, args, opts) => {
      calls.push({ cmd, args, opts });
      if (args[0] === "run" && timeoutOnRun) {
        const error = new Error("spawnSync docker ETIMEDOUT");
        error.code = "ETIMEDOUT";
        return { error, status: null, signal: "SIGKILL" };
      }
      if (args[0] === "logs") {
        return { status: 0, stdout: "collecting files...\nstuck here\n", stderr: "" };
      }
      return { status: 0, stdout: "", stderr: "" };
    };
    return { r, calls };
  }

  async function makeTmpLintDir() {
    return await fs.mkdtemp(path.join(os.tmpdir(), "ml-timeout-"));
  }

  it("resolveTimeoutSeconds returns null when --timeout is not set", () => {
    assert.strictEqual(runner.resolveTimeoutSeconds({}), null);
  });

  it("resolveTimeoutSeconds parses a positive value", () => {
    assert.strictEqual(runner.resolveTimeoutSeconds({ timeout: 600 }), 600);
    assert.strictEqual(runner.resolveTimeoutSeconds({ timeout: "600" }), 600);
  });

  it("resolveTimeoutSeconds rejects zero, negative and non-numeric values", () => {
    assert.throws(
      () => runner.resolveTimeoutSeconds({ timeout: 0 }),
      /Invalid --timeout value/
    );
    assert.throws(
      () => runner.resolveTimeoutSeconds({ timeout: -5 }),
      /Invalid --timeout value/
    );
    assert.throws(
      () => runner.resolveTimeoutSeconds({ timeout: "abc" }),
      /Invalid --timeout value/
    );
  });

  it("on timeout, names the container, bounds spawnSync, then stops and removes the container after capturing its logs", async () => {
    const { r, calls } = makeRunnerWithFakeEngine({ timeoutOnRun: true });
    const res = await r.run({
      image: "megalinter-test:fake",
      nodockerpull: true,
      timeout: 5,
      path: await makeTmpLintDir(),
    });
    assert.strictEqual(res.status, 124);
    assert.strictEqual(res.timedOut, true);
    assert.match(res.errorMsg, /exceeded the --timeout of 5s/);
    const runCall = calls.find((call) => call.args[0] === "run");
    assert.strictEqual(runCall.opts.timeout, 5000);
    assert.strictEqual(runCall.opts.killSignal, "SIGKILL");
    const nameIndex = runCall.args.indexOf("--name");
    assert.ok(nameIndex > -1, "docker run args should contain --name");
    const containerName = runCall.args[nameIndex + 1];
    assert.match(containerName, /^megalinter-runner-/);
    const logsCall = calls.find((call) => call.args[0] === "logs");
    assert.deepStrictEqual(logsCall.args, ["logs", "--tail", "30", containerName]);
    const stopCall = calls.find((call) => call.args[0] === "stop");
    assert.deepStrictEqual(stopCall.args, ["stop", containerName]);
    const rmCall = calls.find((call) => call.args[0] === "rm");
    assert.deepStrictEqual(rmCall.args, ["rm", "--force", containerName]);
    // Logs must be captured before the container is stopped/removed
    assert.ok(calls.indexOf(logsCall) < calls.indexOf(stopCall));
    assert.ok(calls.indexOf(stopCall) < calls.indexOf(rmCall));
  });

  it("on timeout, keeps a user-provided --container-name for the cleanup commands", async () => {
    const { r, calls } = makeRunnerWithFakeEngine({ timeoutOnRun: true });
    const res = await r.run({
      image: "megalinter-test:fake",
      nodockerpull: true,
      timeout: 3,
      containerName: "my-megalinter-run",
      path: await makeTmpLintDir(),
    });
    assert.strictEqual(res.status, 124);
    const runCall = calls.find((call) => call.args[0] === "run");
    const nameIndex = runCall.args.indexOf("--name");
    assert.strictEqual(runCall.args[nameIndex + 1], "my-megalinter-run");
    const stopCall = calls.find((call) => call.args[0] === "stop");
    assert.deepStrictEqual(stopCall.args, ["stop", "my-megalinter-run"]);
  });

  it("without --timeout, adds no container name and no spawnSync time bound", async () => {
    const { r, calls } = makeRunnerWithFakeEngine({ timeoutOnRun: false });
    const res = await r.run({
      image: "megalinter-test:fake",
      nodockerpull: true,
      path: await makeTmpLintDir(),
    });
    assert.strictEqual(res.status, 0);
    const runCall = calls.find((call) => call.args[0] === "run");
    assert.strictEqual(runCall.args.indexOf("--name"), -1);
    assert.strictEqual(runCall.opts.timeout, undefined);
    assert.strictEqual(runCall.opts.killSignal, undefined);
    assert.strictEqual(calls.some((call) => call.args[0] === "stop"), false);
    assert.strictEqual(calls.some((call) => call.args[0] === "rm"), false);
  });
});

describe("Setup answers from CLI options", () => {
  it("maps provided options and drops undefined ones", () => {
    const answers = runner.buildSetupAnswers({
      flavor: "python",
      setupCi: "gitLabCI",
      setupCopyPaste: false,
      setupSpellingMistakes: true,
      release: "beta",
      setupDefaultBranch: "develop",
      setupValidateAllCodeBase: "diff",
      fix: true,
      setupOx: false,
    });
    assert.deepStrictEqual(answers, {
      flavor: "python",
      ci: "gitLabCI",
      copyPaste: false,
      spellingMistakes: true,
      version: "beta",
      defaultBranch: "develop",
      validateAllCodeBase: "diff",
      applyFixes: true,
      ox: false,
    });
  });

  it("maps a pinned release to the default release choice", () => {
    const answers = runner.buildSetupAnswers({ release: "v9.1.2" });
    assert.deepStrictEqual(answers, { version: DEFAULT_RELEASE });
  });

  it("returns no answers when no setup option is provided", () => {
    assert.deepStrictEqual(runner.buildSetupAnswers({}), {});
  });

  it("rejects an unknown --setup-ci value", () => {
    assert.throws(
      () => runner.buildSetupAnswers({ setupCi: "github" }),
      /Invalid --setup-ci value: github/
    );
  });

  it("rejects an unknown --setup-validate-all-code-base value", () => {
    assert.throws(
      () => runner.buildSetupAnswers({ setupValidateAllCodeBase: "full" }),
      /Invalid --setup-validate-all-code-base value: full/
    );
  });
});
