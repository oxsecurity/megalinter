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
