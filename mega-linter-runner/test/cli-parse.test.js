import assert from "assert";
import { optionsDefinition } from "../lib/options.js";
import { expandEnvEntries } from "../lib/env-parser.js";

function parse(argv) {
  return optionsDefinition.parse(["node", "mega-linter-runner", ...argv]);
}

describe("CLI parsing — env flag", () => {
  it("preserves commas in a single -e value (issue #7500)", () => {
    const o = parse(["-e", "ENABLE_LINTERS=YAML_PRETTIER,YAML_YAMLLINT"]);
    assert.deepStrictEqual(o.env, [
      "ENABLE_LINTERS=YAML_PRETTIER,YAML_YAMLLINT",
    ]);
  });

  it("accumulates repeated -e flags into an array", () => {
    const o = parse(["-e", "VAR1=foo", "-e", "VAR2=bar"]);
    assert.deepStrictEqual(o.env, ["VAR1=foo", "VAR2=bar"]);
  });

  it("accumulates repeated -e flags when values contain commas", () => {
    const o = parse([
      "-e",
      "ENABLE=JAVASCRIPT,YAML",
      "-e",
      "DISABLE_LINTERS=MARKDOWN_MARKDOWN_LINK_CHECK",
    ]);
    assert.deepStrictEqual(o.env, [
      "ENABLE=JAVASCRIPT,YAML",
      "DISABLE_LINTERS=MARKDOWN_MARKDOWN_LINK_CHECK",
    ]);
  });

  it("accepts --env=KEY=VALUE long form with comma in value", () => {
    const o = parse(["--env=ENABLE_LINTERS=YAML_PRETTIER,YAML_YAMLLINT"]);
    assert.deepStrictEqual(o.env, [
      "ENABLE_LINTERS=YAML_PRETTIER,YAML_YAMLLINT",
    ]);
  });

  it("accepts --env KEY=VALUE space form", () => {
    const o = parse(["--env", "ENABLE_LINTERS=YAML_PRETTIER,YAML_YAMLLINT"]);
    assert.deepStrictEqual(o.env, [
      "ENABLE_LINTERS=YAML_PRETTIER,YAML_YAMLLINT",
    ]);
  });

  it("mixes -e and --env=", () => {
    const o = parse([
      "-e",
      "ENABLE_LINTERS=YAML_PRETTIER,YAML_YAMLLINT",
      "--env=APPLY_FIXES=all",
    ]);
    assert.deepStrictEqual(o.env, [
      "ENABLE_LINTERS=YAML_PRETTIER,YAML_YAMLLINT",
      "APPLY_FIXES=all",
    ]);
  });

  it("leaves env undefined when no -e is passed", () => {
    const o = parse(["--release", "beta"]);
    assert.strictEqual(o.env, undefined);
  });
});

describe("CLI parsing — custom-flavor-linters", () => {
  it("keeps comma-separated list intact with space form", () => {
    const o = parse([
      "--custom-flavor-linters",
      "YAML_PRETTIER,YAML_YAMLLINT",
    ]);
    assert.strictEqual(o.customFlavorLinters, "YAML_PRETTIER,YAML_YAMLLINT");
  });

  it("keeps comma-separated list intact with = form", () => {
    const o = parse(["--custom-flavor-linters=YAML_PRETTIER,YAML_YAMLLINT"]);
    assert.strictEqual(o.customFlavorLinters, "YAML_PRETTIER,YAML_YAMLLINT");
  });
});

describe("env-parser — expandEnvEntries (backward compatibility)", () => {
  it("keeps single env with comma-separated value intact (issue #7500)", () => {
    assert.deepStrictEqual(
      expandEnvEntries(["ENABLE_LINTERS=YAML_PRETTIER,YAML_YAMLLINT"]),
      ["ENABLE_LINTERS=YAML_PRETTIER,YAML_YAMLLINT"],
    );
  });

  it("expands legacy KEY=VAL,KEY=VAL form into multiple entries", () => {
    assert.deepStrictEqual(
      expandEnvEntries(["VAR1=foo,VAR2=bar"]),
      ["VAR1=foo", "VAR2=bar"],
    );
  });

  it("expands three comma-separated KEY=VAL pairs", () => {
    assert.deepStrictEqual(
      expandEnvEntries(["A=1,B=2,C=3"]),
      ["A=1", "B=2", "C=3"],
    );
  });

  it("does not split when only some parts look like KEY=VAL", () => {
    // Mixed: first looks like KV but later parts don't — comma belongs to the value
    assert.deepStrictEqual(
      expandEnvEntries(["ENABLE_LINTERS=A,B,APPLY_FIXES=all"]),
      ["ENABLE_LINTERS=A,B,APPLY_FIXES=all"],
    );
  });

  it("leaves entries without commas untouched", () => {
    assert.deepStrictEqual(
      expandEnvEntries(["APPLY_FIXES=all", "LOG_LEVEL=DEBUG"]),
      ["APPLY_FIXES=all", "LOG_LEVEL=DEBUG"],
    );
  });

  it("handles a mix of single-value and legacy-multi entries", () => {
    assert.deepStrictEqual(
      expandEnvEntries([
        "ENABLE_LINTERS=YAML_PRETTIER,YAML_YAMLLINT",
        "VAR1=foo,VAR2=bar",
        "LOG_LEVEL=DEBUG",
      ]),
      [
        "ENABLE_LINTERS=YAML_PRETTIER,YAML_YAMLLINT",
        "VAR1=foo",
        "VAR2=bar",
        "LOG_LEVEL=DEBUG",
      ],
    );
  });

  it("preserves empty-value KEY=VAL pairs in legacy form", () => {
    assert.deepStrictEqual(
      expandEnvEntries(["FOO=,BAR="]),
      ["FOO=", "BAR="],
    );
  });

  it("returns non-array input unchanged", () => {
    assert.strictEqual(expandEnvEntries(undefined), undefined);
    assert.strictEqual(expandEnvEntries(null), null);
  });
});

describe("CLI parsing — scalar flags", () => {
  it("parses --release as a string", () => {
    const o = parse(["--release", "v9.1.2"]);
    assert.strictEqual(o.release, "v9.1.2");
  });

  it("parses --release=value form", () => {
    const o = parse(["--release=v9.1.2"]);
    assert.strictEqual(o.release, "v9.1.2");
  });

  it("exposes known flavors / engines / platforms as exported constants", async () => {
    const opts = await import("../lib/options.js");
    assert.ok(opts.KNOWN_FLAVORS.includes("python"));
    assert.deepStrictEqual(opts.KNOWN_CONTAINER_ENGINES, ["docker", "podman"]);
    assert.ok(opts.KNOWN_PLATFORMS.includes("linux/amd64"));
  });

  it("advertises allowed values in the option help text", () => {
    const help = optionsDefinition.generateHelpForOption("flavor");
    assert.match(help, /Allowed values:.*python/);
    const engineHelp = optionsDefinition.generateHelpForOption(
      "container-engine",
    );
    assert.match(engineHelp, /docker.*podman/);
  });
});

describe("CLI parsing — flavor and image", () => {
  it("parses --flavor with long form", () => {
    const o = parse(["--flavor", "python"]);
    assert.strictEqual(o.flavor, "python");
  });

  it("parses -f alias", () => {
    const o = parse(["-f", "java"]);
    assert.strictEqual(o.flavor, "java");
  });

  it("defaults flavor to all when not provided", () => {
    const o = parse([]);
    assert.strictEqual(o.flavor, "all");
  });

  it("parses --image with long form", () => {
    const o = parse(["--image", "my-registry.com/mega-linter-python:v9"]);
    assert.strictEqual(o.image, "my-registry.com/mega-linter-python:v9");
  });

  it("parses -d alias for image", () => {
    const o = parse(["-d", "ghcr.io/oxsecurity/megalinter:latest"]);
    assert.strictEqual(o.image, "ghcr.io/oxsecurity/megalinter:latest");
  });

  it("rejects --image and --flavor together (mutually exclusive)", () => {
    assert.throws(
      () => parse(["--image", "x:y", "--flavor", "python"]),
      /mutually exclusive/,
    );
  });
});

describe("CLI parsing — path", () => {
  it("parses --path long form", () => {
    const o = parse(["--path", "./some/dir"]);
    assert.ok(o.path.endsWith("some/dir") || o.path.endsWith("some\\dir"));
  });

  it("parses -p alias", () => {
    const o = parse(["-p", "./other"]);
    assert.ok(o.path.endsWith("other"));
  });

  it("defaults path to current dir when not provided", () => {
    const o = parse([]);
    assert.ok(o.path);
  });
});

describe("CLI parsing — boolean flags", () => {
  it("parses --fix", () => {
    assert.strictEqual(parse(["--fix"]).fix, true);
  });

  it("parses --filesonly", () => {
    assert.strictEqual(parse(["--filesonly"]).filesonly, true);
  });

  it("parses --json and -j alias", () => {
    assert.strictEqual(parse(["--json"]).json, true);
    assert.strictEqual(parse(["-j"]).json, true);
  });

  it("parses --nodockerpull and -n alias", () => {
    assert.strictEqual(parse(["--nodockerpull"]).nodockerpull, true);
    assert.strictEqual(parse(["-n"]).nodockerpull, true);
  });

  it("parses --debug", () => {
    assert.strictEqual(parse(["--debug"]).debug, true);
  });

  it("parses --install and -i alias", () => {
    assert.strictEqual(parse(["--install"]).install, true);
    assert.strictEqual(parse(["-i"]).install, true);
  });

  it("parses --custom-flavor-setup and --cfs alias", () => {
    assert.strictEqual(parse(["--custom-flavor-setup"]).customFlavorSetup, true);
    assert.strictEqual(parse(["--cfs"]).customFlavorSetup, true);
  });

  it("parses --upgrade and -u alias", () => {
    assert.strictEqual(parse(["--upgrade"]).upgrade, true);
    assert.strictEqual(parse(["-u"]).upgrade, true);
  });

  it("parses --codetotal", () => {
    assert.strictEqual(parse(["--codetotal"]).codetotal, true);
  });

  it("leaves boolean flags undefined when not passed", () => {
    const o = parse([]);
    assert.strictEqual(o.fix, undefined);
    assert.strictEqual(o.debug, undefined);
    assert.strictEqual(o.json, undefined);
    assert.strictEqual(o.upgrade, undefined);
  });
});

describe("CLI parsing — container options", () => {
  it("parses --container-name", () => {
    const o = parse(["--container-name", "my-megalinter-run"]);
    assert.strictEqual(o.containerName, "my-megalinter-run");
  });

  it("parses --containername alias", () => {
    const o = parse(["--containername", "alt-name"]);
    assert.strictEqual(o.containerName, "alt-name");
  });

  it("parses --container-engine", () => {
    const o = parse(["--container-engine", "podman"]);
    assert.strictEqual(o.containerEngine, "podman");
  });

  it("defaults container-engine to docker", () => {
    const o = parse([]);
    assert.strictEqual(o.containerEngine, "docker");
  });

  it("parses --remove-container", () => {
    const o = parse(["--remove-container"]);
    assert.strictEqual(o.removeContainer, true);
  });

  it("parses --no-remove-container as removeContainer:false", () => {
    const o = parse(["--no-remove-container"]);
    assert.strictEqual(o.removeContainer, false);
  });
});

describe("CLI parsing — platform", () => {
  it("parses --platform", () => {
    const o = parse(["--platform", "linux/arm64"]);
    assert.strictEqual(o.platform, "linux/arm64");
  });

  it("parses -z alias", () => {
    const o = parse(["-z", "linux/amd64"]);
    assert.strictEqual(o.platform, "linux/amd64");
  });

  it("defaults platform to linux/amd64", () => {
    const o = parse([]);
    assert.strictEqual(o.platform, "linux/amd64");
  });
});

describe("CLI parsing — codetotal-url", () => {
  it("parses --codetotal-url with custom value", () => {
    const o = parse(["--codetotal-url", "http://localhost:9000/"]);
    assert.strictEqual(o.codetotalUrl, "http://localhost:9000/");
  });

  it("defaults codetotal-url to http://localhost:8081/", () => {
    const o = parse([]);
    assert.strictEqual(o.codetotalUrl, "http://localhost:8081/");
  });
});

describe("CLI parsing — positional file arguments", () => {
  it("captures positional file arguments in _", () => {
    const o = parse(["--release", "beta", "file1.js", "src/file2.py"]);
    assert.deepStrictEqual(o._, ["file1.js", "src/file2.py"]);
  });

  it("returns empty _ when no positional args", () => {
    const o = parse(["--release", "beta"]);
    assert.deepStrictEqual(o._, []);
  });
});

describe("CLI parsing — mutual exclusivity", () => {
  it("rejects --help with --version", () => {
    assert.throws(() => parse(["--help", "--version"]), /mutually exclusive/);
  });

  it("rejects --help with --install", () => {
    assert.throws(() => parse(["--help", "--install"]), /mutually exclusive/);
  });

  it("rejects --help with --list-vars", () => {
    assert.throws(() => parse(["--help", "--list-vars"]), /mutually exclusive/);
  });

  it("rejects --version with --list-vars", () => {
    assert.throws(
      () => parse(["--version", "--list-vars"]),
      /mutually exclusive/,
    );
  });
});

describe("CLI parsing — defaults", () => {
  it("applies all documented defaults with empty argv", () => {
    const o = parse([]);
    assert.strictEqual(o.release, "v9");
    assert.strictEqual(o.flavor, "all");
    assert.strictEqual(o.platform, "linux/amd64");
    assert.strictEqual(o.containerEngine, "docker");
    assert.strictEqual(o.codetotalUrl, "http://localhost:8081/");
    assert.ok(o.path);
  });
});

describe("--list-vars", () => {
  it("returns an object with all variables and meta when no pattern", async () => {
    const { listVars } = await import("../lib/list-vars.js");
    const { stdout } = listVars({});
    assert.match(stdout, /MegaLinter variables/);
    assert.match(stdout, /LOG_LEVEL/);
    assert.match(stdout, /Reference: https:\/\/megalinter\.io/);
  });

  it("filters by case-insensitive substring", async () => {
    const { listVars } = await import("../lib/list-vars.js");
    const { stdout } = listVars({ pattern: "log_level" });
    assert.match(stdout, /LOG_LEVEL/);
    assert.match(stdout, /allowed: INFO, DEBUG, WARNING, ERROR/);
  });

  it("returns JSON when asJson is true", async () => {
    const { listVars } = await import("../lib/list-vars.js");
    const { stdout } = listVars({ pattern: "LOG_LEVEL", asJson: true });
    const parsed = JSON.parse(stdout);
    assert.strictEqual(parsed._meta.pattern, "LOG_LEVEL");
    const logLevel = parsed.variables.find((v) => v.name === "LOG_LEVEL");
    assert.ok(logLevel);
    assert.deepStrictEqual(logLevel.enum, [
      "INFO",
      "DEBUG",
      "WARNING",
      "ERROR",
    ]);
  });

  it("parses --list-vars option", () => {
    const o = parse(["--list-vars", "PYTHON_RUFF"]);
    assert.strictEqual(o.listVars, true);
    assert.deepStrictEqual(o._, ["PYTHON_RUFF"]);
  });
});
