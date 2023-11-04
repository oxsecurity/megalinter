import helpers, { RunResult, result } from "yeoman-test";
import MyGenerator from "../generators/mega-linter/index.js";

import { dirname } from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

import * as path from "path";

describe("generator test", () => {
  describe("test", () => {
    beforeEach(async () => {
      const files = {
        "mega-linter-runner/generators/mega-linter/templates/mega-linter.yml":
          {},
      };
      await helpers
        .run(MyGenerator, {
          targetDir: RunResult,
          resolved: path.join(__dirname, "..", "generators", "mega-linter"),
          namespace: "mega-linter-runner:mega-linter",
        })
        .withAnswers({ flavor: "all", ox: false, ci: "gitHubActions" });
    });

    it("creates files", () => {
      // before(() => helpers.prepareTemporaryDir());
      result
        .dumpFiles(".github/workflows/mega-linter.yml")
        .fs.copy(
          ".github/workflows/mega-linter.yml",
          path.join(
            __dirname,
            "..",
            "generators",
            "mega-linter",
            "out",
            ".github/workflows/mega-linter.yml"
          )
        );
      result.fs.commit();
      result.dumpFilenames();
    });
  });
});
