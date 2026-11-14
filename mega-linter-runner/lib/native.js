// cspell:ignore packagetype bdist (PyPI JSON API fields)
// Run MegaLinter natively (without Docker)
//
// The runner does not lint anything itself: it installs the `megalinter` Python package of the
// requested channel from PyPI in ~/.megalinter/core/<version>, then hands over to its `megalinter`
// command (`megalinter run`, `megalinter install-linters`).
//
// The package is verified before it is installed:
//   1. its sha256 must match the PyPI metadata
//   2. its PyPI attestation (PEP 740, sigstore) must prove it was published by the
//      deploy-megalinter-pypi.yml workflow of oxsecurity/megalinter
//   3. its dependencies are installed with --require-hashes from the lock it contains
import * as crypto from "crypto";
import * as fs from "fs";
import * as os from "os";
import * as path from "path";
import { spawnSync } from "child_process";
import { fileURLToPath } from "url";
import { expandEnvEntries } from "./env-parser.js";
import { which } from "./which.js";

const PYPI_PROJECT_URL = "https://pypi.org/pypi/megalinter";
const PYPI_INTEGRITY_URL = "https://pypi.org/integrity/megalinter";
const PUBLISHER_REPOSITORY = "oxsecurity/megalinter";
const PUBLISHER_WORKFLOW = "deploy-megalinter-pypi.yml";
const PUBLISHER_IDENTITY = `https://github.com/${PUBLISHER_REPOSITORY}/.github/workflows/${PUBLISHER_WORKFLOW}@refs/heads/main`;
const VERIFIER_LOCK = path.join(
  path.dirname(fileURLToPath(import.meta.url)),
  "native-verifier.requirements.lock",
);
const NATIVE_DEFAULT_RELEASE = "beta";
const RUNTIME_POLICIES = ["ask", "auto", "never"];
// Options that only make sense with a container
const DOCKER_ONLY_OPTIONS = [
  ["image", "--image"],
  ["platform", "--platform"],
  ["containerName", "--container-name"],
  ["nodockerpull", "--nodockerpull"],
  ["noRemoveContainer", "--no-remove-container"],
  ["userMap", "--user-map"],
  ["noUserMap", "--no-user-map"],
  ["flavor", "--flavor"],
];
const UV_INSTALL_HELP = {
  win32: "winget install --id astral-sh.uv -e",
  darwin: "brew install uv",
  linux:
    "pipx install uv (or see https://docs.astral.sh/uv/getting-started/installation/)",
};

export class NativeRunner {
  constructor({ spawnSyncFn, fetchFn, whichFn, home } = {}) {
    this.spawnSyncFn = spawnSyncFn || spawnSync;
    this.fetchFn = fetchFn || globalThis.fetch;
    this.whichFn = whichFn || which;
    this.home =
      home ||
      process.env.MEGALINTER_HOME ||
      path.join(os.homedir(), ".megalinter");
  }

  assertSupportedOptions(options) {
    for (const [key, flag] of DOCKER_ONLY_OPTIONS) {
      if (options[key]) {
        throw new Error(
          `${flag} is only available with Docker: it can not be used with --native or --install-linters`,
        );
      }
    }
    if (options.containerEngine && options.containerEngine !== "docker") {
      throw new Error(
        "--container-engine is only available with Docker: it can not be used with --native or --install-linters",
      );
    }
    if (options.runtimes && !RUNTIME_POLICIES.includes(options.runtimes)) {
      throw new Error(
        `Invalid --runtimes value: ${options.runtimes}. Allowed values: ${RUNTIME_POLICIES.join(", ")}`,
      );
    }
  }

  buildEnvironment(options) {
    const env = { ...process.env };
    if (options.fix === true) {
      env.APPLY_FIXES = "all";
    }
    if (options.filesonly === true) {
      env.SKIP_CLI_LINT_MODES = "project";
    }
    if (options.debug === true) {
      env.LOG_LEVEL = "DEBUG";
    }
    if (options.linter) {
      env.NATIVE_LINTERS = options.linter.toUpperCase();
    }
    if (options.trustRepoCommands === true) {
      env.NATIVE_TRUST_REPO_COMMANDS = "true";
    }
    // Files given as arguments (pre-commit hooks), relative to the workspace
    if (options.installLinters !== true && (options._ || []).length > 0) {
      env.MEGALINTER_FILES_TO_LINT = options._.map(String).join(",");
    }
    for (const rawEntry of expandEnvEntries(options.env || [])) {
      // Same quoting as with Docker, where a shell removes it: "'KEY=VALUE1,VALUE2'"
      const entry = String(rawEntry).replace(/^(['"])(.*)\1$/s, "$2");
      const separator = entry.indexOf("=");
      if (separator > 0) {
        env[entry.slice(0, separator)] = entry.slice(separator + 1);
      }
    }
    // NATIVE_TRUST_REPO_COMMANDS is only honored from the environment or --trust-repo-commands
    return env;
  }

  buildArguments(options) {
    const workspace = path.resolve(options.path || ".");
    const common = ["--input", workspace];
    if (options.runtimes) {
      common.push("--runtimes", options.runtimes);
    }
    if (options.installLinters === true) {
      const keys = (options._ || []).map(String);
      return [
        "install-linters",
        ...keys,
        ...(options.all === true ? ["--all"] : []),
        ...common,
      ];
    }
    return [
      "run",
      ...common,
      ...(options.trustRepoCommands === true ? ["--trust-repo-commands"] : []),
    ];
  }

  async fetchJson(url) {
    const response = await this.fetchFn(url, {
      headers: { "User-Agent": "mega-linter-runner" },
    });
    if (!response.ok) {
      throw new Error(`Unable to fetch ${url}: HTTP ${response.status}`);
    }
    return response.json();
  }

  // beta: latest pre-release | exact version | stable (not published while native mode is in beta)
  async resolveVersion(release) {
    const project = await this.fetchJson(`${PYPI_PROJECT_URL}/json`);
    const versions = Object.keys(project.releases).filter(
      (version) => project.releases[version].length > 0,
    );
    const uploaded = (version) =>
      Date.parse(project.releases[version][0].upload_time_iso_8601);
    const wanted = release || NATIVE_DEFAULT_RELEASE;
    if (wanted === "beta") {
      const betas = versions.filter((version) => version.includes(".dev"));
      if (betas.length === 0) {
        throw new Error("No MegaLinter native beta has been published yet");
      }
      return betas.sort((a, b) => uploaded(b) - uploaded(a))[0];
    }
    if (versions.includes(wanted)) {
      return wanted;
    }
    const stable = versions.filter((version) => !version.includes(".dev"));
    if (stable.length === 0) {
      throw new Error(
        `Native mode is in beta: no stable version has been published yet. Use --release beta (or an exact beta version).`,
      );
    }
    throw new Error(
      `MegaLinter ${wanted} not found on PyPI. Available stable versions: ${stable.join(", ")}`,
    );
  }

  run_(command, args, options = {}) {
    const result = this.spawnSyncFn(command, args, {
      stdio: "pipe",
      windowsHide: true,
      encoding: "utf8",
      ...options,
    });
    if (result.status !== 0) {
      throw new Error(
        `${command} ${args.join(" ")} failed (${result.status}):\n${result.stdout || ""}${result.stderr || ""}`,
      );
    }
    return result;
  }

  binDir(venv) {
    return path.join(venv, process.platform === "win32" ? "Scripts" : "bin");
  }

  pythonOf(venv) {
    return path.join(
      this.binDir(venv),
      process.platform === "win32" ? "python.exe" : "python",
    );
  }

  async findUv() {
    try {
      return await this.whichFn("uv");
    } catch {
      const hint = UV_INSTALL_HELP[process.platform] || UV_INSTALL_HELP.linux;
      throw new Error(
        `uv is required to run MegaLinter without Docker. Install it with: ${hint}`,
      );
    }
  }

  ensureVerifier(uv) {
    const lockHash = crypto
      .createHash("sha256")
      .update(fs.readFileSync(VERIFIER_LOCK))
      .digest("hex")
      .slice(0, 12);
    const venv = path.join(this.home, "tools", `verifier-${lockHash}`);
    const marker = path.join(venv, ".ok");
    if (!fs.existsSync(marker)) {
      fs.rmSync(venv, { recursive: true, force: true });
      this.run_(uv, ["venv", venv, "--no-config", "--python", ">=3.10"]);
      this.run_(uv, [
        "pip",
        "install",
        "--no-config",
        "--python",
        this.pythonOf(venv),
        "--require-hashes",
        "--no-deps",
        "--only-binary",
        ":all:",
        "-r",
        VERIFIER_LOCK,
      ]);
      fs.writeFileSync(marker, lockHash);
    }
    return this.pythonOf(venv);
  }

  async download(url, destination, expectedSha256) {
    if (new URL(url).protocol !== "https:") {
      throw new Error(`Refusing to download from a non-HTTPS URL: ${url}`);
    }
    const response = await this.fetchFn(url, {
      headers: { "User-Agent": "mega-linter-runner" },
    });
    if (!response.ok) {
      throw new Error(`Unable to download ${url}: HTTP ${response.status}`);
    }
    const content = Buffer.from(await response.arrayBuffer());
    const sha256 = crypto.createHash("sha256").update(content).digest("hex");
    if (sha256 !== expectedSha256) {
      throw new Error(
        `sha256 mismatch for ${url}: expected ${expectedSha256}, got ${sha256}`,
      );
    }
    fs.writeFileSync(destination, content);
  }

  // The PyPI attestation must come from the release workflow of this repository
  async fetchAttestation(version, filename, wheelPath) {
    const provenance = await this.fetchJson(
      `${PYPI_INTEGRITY_URL}/${version}/${filename}/provenance`,
    );
    const bundle = (provenance.attestation_bundles || []).find(
      (candidate) =>
        candidate.publisher &&
        candidate.publisher.kind === "GitHub" &&
        candidate.publisher.repository === PUBLISHER_REPOSITORY &&
        candidate.publisher.workflow === PUBLISHER_WORKFLOW &&
        (candidate.attestations || []).length > 0,
    );
    if (!bundle) {
      throw new Error(
        `${filename} has no attestation from ${PUBLISHER_REPOSITORY} (${PUBLISHER_WORKFLOW}): refusing to install it`,
      );
    }
    fs.writeFileSync(
      `${wheelPath}.publish.attestation`,
      JSON.stringify(bundle.attestations[0]),
    );
  }

  async ensureCore(release, uv) {
    const version = await this.resolveVersion(release);
    const coreDir = path.join(this.home, "core", version);
    const venv = path.join(coreDir, "venv");
    const marker = path.join(coreDir, ".ok");
    if (fs.existsSync(marker)) {
      return this.binDir(venv);
    }
    console.info(`Installing MegaLinter ${version} in ${coreDir} ...`);
    fs.rmSync(coreDir, { recursive: true, force: true });
    fs.mkdirSync(coreDir, { recursive: true, mode: 0o700 });
    const metadata = await this.fetchJson(
      `${PYPI_PROJECT_URL}/${version}/json`,
    );
    const wheel = metadata.urls.find(
      (file) => file.packagetype === "bdist_wheel",
    );
    if (!wheel) {
      throw new Error(`MegaLinter ${version} has no wheel on PyPI`);
    }
    const wheelPath = path.join(coreDir, wheel.filename);
    await this.download(wheel.url, wheelPath, wheel.digests.sha256);
    await this.fetchAttestation(version, wheel.filename, wheelPath);
    const verifierPython = this.ensureVerifier(uv);
    this.run_(verifierPython, [
      "-m",
      "pypi_attestations",
      "verify",
      "attestation",
      "--identity",
      PUBLISHER_IDENTITY,
      wheelPath,
    ]);
    const lockPath = path.join(coreDir, "core-requirements.lock");
    this.run_(verifierPython, [
      "-c",
      "import sys, zipfile; open(sys.argv[2], 'wb').write(zipfile.ZipFile(sys.argv[1]).read('megalinter/_core-requirements.lock'))",
      wheelPath,
      lockPath,
    ]);
    this.run_(uv, ["venv", venv, "--no-config", "--python", ">=3.12"]);
    const python = this.pythonOf(venv);
    this.run_(uv, [
      "pip",
      "install",
      "--no-config",
      "--python",
      python,
      "--require-hashes",
      "--no-deps",
      "--only-binary",
      ":all:",
      "-r",
      lockPath,
    ]);
    this.run_(uv, [
      "pip",
      "install",
      "--no-config",
      "--python",
      python,
      "--no-deps",
      wheelPath,
    ]);
    fs.writeFileSync(marker, wheel.digests.sha256);
    return this.binDir(venv);
  }

  async run(options) {
    this.assertSupportedOptions(options);
    const uv = await this.findUv();
    const binDir = await this.ensureCore(options.release, uv);
    const executable = path.join(
      binDir,
      process.platform === "win32" ? "megalinter.exe" : "megalinter",
    );
    const args = this.buildArguments(options);
    const timeoutSeconds = Number(options.timeout);
    const result = this.spawnSyncFn(executable, args, {
      stdio: "inherit",
      windowsHide: true,
      env: this.buildEnvironment(options),
      ...(timeoutSeconds > 0 ? { timeout: timeoutSeconds * 1000 } : {}),
    });
    if (result.error && result.error.code === "ETIMEDOUT") {
      return { status: 124 };
    }
    return { status: result.status === null ? 1 : result.status };
  }
}
