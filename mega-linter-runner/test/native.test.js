// cspell:ignore packagetype bdist (PyPI JSON API fields)
import assert from "assert";
import crypto from "crypto";
import fs from "fs";
import os from "os";
import path from "path";
import { NativeRunner } from "../lib/native.js";
import { optionsDefinition } from "../lib/options.js";

function jsonResponse(body) {
  return { ok: true, status: 200, json: async () => body };
}

function binaryResponse(buffer) {
  return {
    ok: true,
    status: 200,
    arrayBuffer: async () =>
      buffer.buffer.slice(
        buffer.byteOffset,
        buffer.byteOffset + buffer.byteLength,
      ),
  };
}

function project(releases) {
  const result = {};
  for (const [version, uploaded] of Object.entries(releases)) {
    result[version] = [{ upload_time_iso_8601: uploaded }];
  }
  return { releases: result };
}

function makeRunner(fetchFn, extra = {}) {
  const home = fs.mkdtempSync(path.join(os.tmpdir(), "ml-native-"));
  return new NativeRunner({ fetchFn, home, ...extra });
}

describe("mega-linter-runner native mode", () => {
  describe("options", () => {
    it("rejects Docker-only options", () => {
      const runner = makeRunner(async () => {});
      for (const options of [
        { image: "x" },
        { platform: "linux/amd64" },
        { containerName: "x" },
        { nodockerpull: true },
        { flavor: "python" },
        { containerEngine: "podman" },
      ]) {
        assert.throws(() => runner.assertSupportedOptions(options), /Docker/);
      }
    });

    // Options as parsed from the command line, with their defaults: a Docker-only option with a
    // default value would make every native command fail
    it("accepts the parsed options of a native command", () => {
      const runner = makeRunner(async () => {});
      for (const args of [
        ["--native", "--release", "beta"],
        ["--install-linters", "--release", "beta"],
        ["--native", "--fix", "--filesonly", "src/app.py"],
      ]) {
        const options = optionsDefinition.parse([
          "node",
          "mega-linter-runner",
          ...args,
        ]);
        assert.doesNotThrow(() => runner.assertSupportedOptions(options));
      }
      const docker = optionsDefinition.parse([
        "node",
        "mega-linter-runner",
        "--native",
        "--platform",
        "linux/arm64",
      ]);
      assert.throws(() => runner.assertSupportedOptions(docker), /--platform/);
    });

    it("rejects an unknown runtime policy", () => {
      const runner = makeRunner(async () => {});
      assert.throws(
        () => runner.assertSupportedOptions({ runtimes: "sometimes" }),
        /--runtimes/,
      );
    });

    it("builds the run command", () => {
      const runner = makeRunner(async () => {});
      const args = runner.buildArguments({ path: "/work", runtimes: "auto" });
      assert.deepStrictEqual(args, [
        "run",
        "--input",
        path.resolve("/work"),
        "--runtimes",
        "auto",
      ]);
    });

    it("builds the install-linters command with linter keys and --all", () => {
      const runner = makeRunner(async () => {});
      const args = runner.buildArguments({
        installLinters: true,
        _: ["PYTHON_BLACK", "JAVASCRIPT_ES"],
        all: true,
        path: "/work",
      });
      assert.deepStrictEqual(args.slice(0, 4), [
        "install-linters",
        "PYTHON_BLACK",
        "JAVASCRIPT_ES",
        "--all",
      ]);
    });

    it("never trusts the repository unless asked", () => {
      const runner = makeRunner(async () => {});
      assert.ok(!runner.buildArguments({}).includes("--trust-repo-commands"));
      assert.ok(
        runner
          .buildArguments({ trustRepoCommands: true })
          .includes("--trust-repo-commands"),
      );
    });

    it("maps runner options to environment variables", () => {
      const runner = makeRunner(async () => {});
      const env = runner.buildEnvironment({
        fix: true,
        filesonly: true,
        linter: "python_black",
        env: ["FOO=bar=baz"],
      });
      assert.strictEqual(env.APPLY_FIXES, "all");
      assert.strictEqual(env.SKIP_CLI_LINT_MODES, "project");
      assert.strictEqual(env.NATIVE_LINTERS, "PYTHON_BLACK");
      assert.strictEqual(env.FOO, "bar=baz");
    });

    it("accepts the quoted --env values of the Docker mode", () => {
      const runner = makeRunner(async () => {});
      const env = runner.buildEnvironment({
        env: ["'ENABLE=MARKDOWN,YAML'", '"LOG_LEVEL=warning"'],
      });
      assert.strictEqual(env.ENABLE, "MARKDOWN,YAML");
      assert.strictEqual(env.LOG_LEVEL, "warning");
    });

    it("lints only the files given as arguments (pre-commit)", () => {
      const runner = makeRunner(async () => {});
      const env = runner.buildEnvironment({ _: ["src/a.py", "README.md"] });
      assert.strictEqual(env.MEGALINTER_FILES_TO_LINT, "src/a.py,README.md");
      const installEnv = runner.buildEnvironment({
        installLinters: true,
        _: ["PYTHON_BLACK"],
      });
      assert.strictEqual(installEnv.MEGALINTER_FILES_TO_LINT, undefined);
    });
  });

  describe("release resolution", () => {
    const releases = {
      "10.2.0": "2026-10-01T00:00:00Z",
      "10.2.0.post0.dev20261101000000": "2026-11-01T00:00:00Z",
      "10.2.0.post0.dev20261110000000": "2026-11-10T00:00:00Z",
    };

    it("beta resolves the most recent pre-release", async () => {
      const runner = makeRunner(async () => jsonResponse(project(releases)));
      assert.strictEqual(
        await runner.resolveVersion("beta"),
        "10.2.0.post0.dev20261110000000",
      );
    });

    it("accepts an exact version", async () => {
      const runner = makeRunner(async () => jsonResponse(project(releases)));
      assert.strictEqual(
        await runner.resolveVersion("10.2.0.post0.dev20261101000000"),
        "10.2.0.post0.dev20261101000000",
      );
    });

    it("explains that no stable native version exists while in beta", async () => {
      const onlyBetas = {
        "10.2.0.post0.dev20261110000000": "2026-11-10T00:00:00Z",
      };
      const runner = makeRunner(async () => jsonResponse(project(onlyBetas)));
      await assert.rejects(runner.resolveVersion("v10"), /--release beta/);
    });

    it("fails clearly when no beta was published", async () => {
      const runner = makeRunner(async () => jsonResponse(project({})));
      await assert.rejects(
        runner.resolveVersion("beta"),
        /No MegaLinter native beta/,
      );
    });
  });

  describe("package verification", () => {
    const content = Buffer.from("wheel content");
    const sha256 = crypto.createHash("sha256").update(content).digest("hex");
    const filename = "megalinter-1-py3-none-any.whl";

    function fetchFor({ digest = sha256, bundles }) {
      return async (url) => {
        if (url.endsWith("/megalinter/json")) {
          return jsonResponse(
            project({ "1.0.0.post0.dev1": "2026-11-10T00:00:00Z" }),
          );
        }
        if (url.endsWith("/json")) {
          return jsonResponse({
            urls: [
              {
                packagetype: "bdist_wheel",
                filename,
                url: `https://files.pythonhosted.org/${filename}`,
                digests: { sha256: digest },
              },
            ],
          });
        }
        if (url.includes("/provenance")) {
          return jsonResponse({ attestation_bundles: bundles });
        }
        return binaryResponse(content);
      };
    }

    const noopSpawn = () => ({ status: 0, stdout: "", stderr: "" });

    it("refuses a wheel whose sha256 differs from PyPI", async () => {
      const runner = makeRunner(
        fetchFor({ digest: "0".repeat(64), bundles: [] }),
        {
          spawnSyncFn: noopSpawn,
        },
      );
      await assert.rejects(runner.ensureCore("beta", "uv"), /sha256 mismatch/);
    });

    it("refuses a wheel without an attestation from this repository", async () => {
      const bundles = [
        {
          publisher: {
            kind: "GitHub",
            repository: "someone/else",
            workflow: "x.yml",
          },
          attestations: [{}],
        },
      ];
      const runner = makeRunner(fetchFor({ bundles }), {
        spawnSyncFn: noopSpawn,
      });
      await assert.rejects(
        runner.ensureCore("beta", "uv"),
        /refusing to install/,
      );
    });

    it("refuses a non-HTTPS download", async () => {
      const runner = makeRunner(async () => {});
      await assert.rejects(
        runner.download("http://example.com/x.whl", "/tmp/x", sha256),
        /non-HTTPS/,
      );
    });
  });

  describe("uv", () => {
    it("explains how to install uv when it is missing", async () => {
      const runner = makeRunner(async () => {}, {
        whichFn: async () => {
          throw new Error("not found");
        },
      });
      await assert.rejects(runner.findUv(), /uv is required/);
    });
  });
});
