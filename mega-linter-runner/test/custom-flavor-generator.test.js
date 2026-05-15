import assert from "assert";
import { createEnv } from "yeoman-environment";
import { TestAdapter } from "@yeoman/adapter/testing";
import * as path from "path";
import os from "os";
import fs from "fs-extra";
import { execSync } from "child_process";
import { fileURLToPath } from "url";
import { dirname } from "path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const GENERATOR_PATH = path.resolve(
  path.join(__dirname, "..", "generators", "mega-linter-custom-flavor"),
);

async function makeGitRepo(remoteUrl) {
  const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "ml-cf-"));
  execSync("git init", { cwd: tmpDir });
  execSync(`git remote add origin ${remoteUrl}`, { cwd: tmpDir });
  execSync("git config user.email test@example.com", { cwd: tmpDir });
  execSync("git config user.name test-user", { cwd: tmpDir });
  return tmpDir;
}

async function runGenerator(tmpDir, mockedAnswers) {
  const originalCwd = process.cwd();
  const adapter = new TestAdapter({ mockedAnswers });
  try {
    process.chdir(tmpDir);
    const env = createEnv({ adapter, cwd: tmpDir });
    await env.run([GENERATOR_PATH]);
  } finally {
    process.chdir(originalCwd);
  }
}

describe("Custom flavor generator (--custom-flavor-setup)", function () {
  this.timeout(30000);

  it("throws when run in a repo whose name does not include 'megalinter-custom-flavor'", async () => {
    const tmpDir = await makeGitRepo(
      "https://github.com/example/some-other-repo.git",
    );
    await assert.rejects(
      runGenerator(tmpDir, {}),
      /megalinter-custom-flavor/,
      "should reject when remote URL lacks 'megalinter-custom-flavor'",
    );
  });

  describe("when run in a properly named repo with mocked schema fetch", function () {
    const originalFetch = globalThis.fetch;

    beforeEach(() => {
      const fakeSchema = {
        definitions: {
          enum_linter_keys: {
            enum: ["YAML_PRETTIER", "YAML_YAMLLINT", "PYTHON_RUFF"],
          },
        },
      };
      globalThis.fetch = async () => ({
        ok: true,
        json: async () => fakeSchema,
      });
    });

    afterEach(() => {
      globalThis.fetch = originalFetch;
      delete globalThis.customFlavorLinters;
    });

    it("generates expected files for a HTTPS remote", async () => {
      const tmpDir = await makeGitRepo(
        "https://github.com/example/megalinter-custom-flavor-yaml.git",
      );
      await runGenerator(tmpDir, {
        customFlavorLabel: "MyYamlFlavor",
        selectedLinters: ["YAML_PRETTIER", "YAML_YAMLLINT"],
      });
      assert.ok(
        fs.existsSync(path.join(tmpDir, "megalinter-custom-flavor.yml")),
        "megalinter-custom-flavor.yml should be created",
      );
      assert.ok(
        fs.existsSync(path.join(tmpDir, "action.yml")),
        "action.yml should be created",
      );
      assert.ok(
        fs.existsSync(path.join(tmpDir, "README.md")),
        "README.md should be created",
      );
      assert.ok(
        fs.existsSync(
          path.join(
            tmpDir,
            ".github",
            "workflows",
            "megalinter-custom-flavor-builder.yml",
          ),
        ),
        "builder workflow should be created",
      );
      const flavorYml = await fs.readFile(
        path.join(tmpDir, "megalinter-custom-flavor.yml"),
        "utf8",
      );
      assert.match(flavorYml, /MyYamlFlavor/);
      assert.match(flavorYml, /YAML_PRETTIER/);
      assert.match(flavorYml, /YAML_YAMLLINT/);
    });

    it("supports SSH-form git remotes", async () => {
      const tmpDir = await makeGitRepo(
        "git@github.com:example/megalinter-custom-flavor-python.git",
      );
      await runGenerator(tmpDir, {
        customFlavorLabel: "MyPythonFlavor",
        selectedLinters: ["PYTHON_RUFF"],
      });
      const readme = await fs.readFile(
        path.join(tmpDir, "README.md"),
        "utf8",
      );
      assert.match(readme, /MyPythonFlavor/);
      assert.match(readme, /https:\/\/github\.com\/example\/megalinter-custom-flavor-python/);
    });

    it("rejects an invalid linter key when seeded via globalThis.customFlavorLinters", async () => {
      const tmpDir = await makeGitRepo(
        "https://github.com/example/megalinter-custom-flavor-bad.git",
      );
      globalThis.customFlavorLinters = ["YAML_PRETTIER", "NOT_A_REAL_LINTER"];
      await assert.rejects(
        runGenerator(tmpDir, {}),
        /Invalid linter key: NOT_A_REAL_LINTER/,
      );
    });

    it("uses seeded linters from globalThis.customFlavorLinters when valid", async () => {
      const tmpDir = await makeGitRepo(
        "https://github.com/example/megalinter-custom-flavor-seeded.git",
      );
      globalThis.customFlavorLinters = ["YAML_PRETTIER"];
      await runGenerator(tmpDir, {
        customFlavorLabel: "SeededFlavor",
        selectedLinters: ["YAML_PRETTIER"],
      });
      const flavorYml = await fs.readFile(
        path.join(tmpDir, "megalinter-custom-flavor.yml"),
        "utf8",
      );
      assert.match(flavorYml, /YAML_PRETTIER/);
    });
  });
});
