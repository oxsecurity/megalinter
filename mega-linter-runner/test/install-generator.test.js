import assert from "assert";
import { createEnv } from "yeoman-environment";
import { TestAdapter } from "@yeoman/adapter/testing";
import * as path from "path";
import os from "os";
import fs from "fs-extra";
import { fileURLToPath } from "url";
import { dirname } from "path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const GENERATOR_PATH = path.resolve(
  path.join(__dirname, "..", "generators", "mega-linter"),
);

const DEFAULT_ANSWERS = {
  flavor: "all",
  ci: "gitHubActions",
  copyPaste: false,
  spellingMistakes: false,
  version: "v9",
  defaultBranch: "main",
  validateAllCodeBase: "all",
  applyFixes: false,
  ox: false,
};

async function runGenerator(answers) {
  const originalCwd = process.cwd();
  const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "ml-gen-"));
  const adapter = new TestAdapter({ mockedAnswers: { ...DEFAULT_ANSWERS, ...answers } });
  try {
    process.chdir(tmpDir);
    const env = createEnv({ adapter, cwd: tmpDir });
    await env.run([GENERATOR_PATH]);
    return tmpDir;
  } finally {
    process.chdir(originalCwd);
  }
}

describe("Install generator (--install)", function () {
  this.timeout(30000);

  it("generates GitHub Actions workflow and .mega-linter.yml for default options", async () => {
    const tmpDir = await runGenerator({});
    assert.ok(
      fs.existsSync(path.join(tmpDir, ".mega-linter.yml")),
      ".mega-linter.yml should be created",
    );
    assert.ok(
      fs.existsSync(
        path.join(tmpDir, ".github", "workflows", "mega-linter.yml"),
      ),
      ".github/workflows/mega-linter.yml should be created",
    );
    assert.ok(
      fs.existsSync(path.join(tmpDir, ".gitignore")),
      ".gitignore should be created",
    );
    const gitignore = await fs.readFile(path.join(tmpDir, ".gitignore"), "utf8");
    assert.match(gitignore, /megalinter-reports\//);
  });

  it("generates GitLab CI config when ci=gitLabCI", async () => {
    const tmpDir = await runGenerator({ ci: "gitLabCI" });
    assert.ok(
      fs.existsSync(path.join(tmpDir, ".gitlab-ci.yml")),
      ".gitlab-ci.yml should be created",
    );
    assert.ok(
      !fs.existsSync(
        path.join(tmpDir, ".github", "workflows", "mega-linter.yml"),
      ),
      "GitHub Actions workflow should NOT be created",
    );
  });

  it("generates Azure Pipelines config when ci=azure", async () => {
    const tmpDir = await runGenerator({ ci: "azure" });
    assert.ok(
      fs.existsSync(path.join(tmpDir, "azure-pipelines.yml")),
      "azure-pipelines.yml should be created",
    );
  });

  it("generates Jenkinsfile when ci=jenkins", async () => {
    const tmpDir = await runGenerator({ ci: "jenkins" });
    assert.ok(
      fs.existsSync(path.join(tmpDir, "Jenkinsfile")),
      "Jenkinsfile should be created",
    );
  });

  it("generates Bitbucket Pipelines config when ci=bitbucket", async () => {
    const tmpDir = await runGenerator({ ci: "bitbucket" });
    assert.ok(
      fs.existsSync(path.join(tmpDir, "bitbucket-pipelines.yml")),
      "bitbucket-pipelines.yml should be created",
    );
  });

  it("generates Drone CI config when ci=droneCI", async () => {
    const tmpDir = await runGenerator({ ci: "droneCI" });
    assert.ok(
      fs.existsSync(path.join(tmpDir, ".drone.yml")),
      ".drone.yml should be created",
    );
  });

  it("generates Concourse CI config when ci=concourse", async () => {
    const tmpDir = await runGenerator({ ci: "concourse" });
    assert.ok(
      fs.existsSync(path.join(tmpDir, "concourse-task.yml")),
      "concourse-task.yml should be created",
    );
  });

  it("uses python flavor in generated GitHub Actions workflow", async () => {
    const tmpDir = await runGenerator({ flavor: "python" });
    const workflow = await fs.readFile(
      path.join(tmpDir, ".github", "workflows", "mega-linter.yml"),
      "utf8",
    );
    assert.match(workflow, /megalinter\/flavors\/python/);
  });

  it("generates .cspell.json when spellingMistakes is true", async () => {
    const tmpDir = await runGenerator({ spellingMistakes: true });
    assert.ok(
      fs.existsSync(path.join(tmpDir, ".cspell.json")),
      ".cspell.json should be created",
    );
  });

  it("does not generate .cspell.json when spellingMistakes is false", async () => {
    const tmpDir = await runGenerator({ spellingMistakes: false });
    assert.ok(
      !fs.existsSync(path.join(tmpDir, ".cspell.json")),
      ".cspell.json should NOT be created",
    );
  });

  it("generates .jscpd.json when copyPaste is true", async () => {
    const tmpDir = await runGenerator({ copyPaste: true });
    assert.ok(
      fs.existsSync(path.join(tmpDir, ".jscpd.json")),
      ".jscpd.json should be created",
    );
  });

  it("does not generate .jscpd.json when copyPaste is false", async () => {
    const tmpDir = await runGenerator({ copyPaste: false });
    assert.ok(
      !fs.existsSync(path.join(tmpDir, ".jscpd.json")),
      ".jscpd.json should NOT be created",
    );
  });

  it("reflects applyFixes=true in the generated workflow", async () => {
    const tmpDir = await runGenerator({ applyFixes: true });
    const workflow = await fs.readFile(
      path.join(tmpDir, ".github", "workflows", "mega-linter.yml"),
      "utf8",
    );
    assert.match(workflow, /APPLY_FIXES:\s*all/);
  });

  it("reflects applyFixes=false in the generated workflow", async () => {
    const tmpDir = await runGenerator({ applyFixes: false });
    const workflow = await fs.readFile(
      path.join(tmpDir, ".github", "workflows", "mega-linter.yml"),
      "utf8",
    );
    assert.match(workflow, /APPLY_FIXES:\s*none/);
  });

  it("writes only manual instructions when ci=other", async () => {
    const tmpDir = await runGenerator({ ci: "other" });
    assert.ok(
      !fs.existsSync(
        path.join(tmpDir, ".github", "workflows", "mega-linter.yml"),
      ),
      "no GitHub workflow when ci=other",
    );
    assert.ok(
      !fs.existsSync(path.join(tmpDir, ".gitlab-ci.yml")),
      "no GitLab CI when ci=other",
    );
    assert.ok(
      fs.existsSync(path.join(tmpDir, ".mega-linter.yml")),
      ".mega-linter.yml is still created when ci=other",
    );
  });
});
