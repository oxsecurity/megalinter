import assert from "assert";
import { spawnSync } from "child_process";
import fs from "fs-extra";
import os from "os";
import path from "path";
import { fileURLToPath } from "url";

const image = process.env.MEGALINTER_IMAGE;
const release = process.env.MEGALINTER_RELEASE || "beta";
const nodockerpull =
  process.env.MEGALINTER_NO_DOCKER_PULL === "true" ? true : false;
const testDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(testDir, "..", "..");
const runnerCli = path.join(repoRoot, "mega-linter-runner", "lib", "index.js");
const supportsUserMap =
  typeof process.getuid === "function" && typeof process.getgid === "function";
const runtimeModes = [
  {
    id: "root",
    label: "root",
    dockerArgs: [],
    envArgs: [],
    sshPort: "22",
    sshUser: "root",
    sshExpectedUid: "0",
  },
  ...(supportsUserMap
    ? [
        {
          id: "non-root",
          label: "non-root",
          dockerArgs: [],
          envArgs: [
            "-e",
            `MEGALINTER_UID=${process.getuid()}`,
            "-e",
            `MEGALINTER_GID=${process.getgid()}`,
            "-e",
            "HOME=/home/megalinter",
          ],
          sshPort: "2222",
          sshUser: "megalinter",
          sshExpectedUid: `${process.getuid()}`,
        },
      ]
    : []),
];

function runCommand(command, args, options = {}) {
  return spawnSync(command, args, {
    encoding: "utf8",
    ...options,
  });
}

function assertSuccess(result, message) {
  const details = [result.stderr, result.stdout].filter(Boolean).join("\n");
  assert.strictEqual(
    result.status,
    0,
    details ? `${message}\n${details}` : message,
  );
}

function readDockerLogs(containerName) {
  const res = runCommand("docker", ["logs", containerName]);
  return [res.stderr, res.stdout].filter(Boolean).join("\n");
}

function cleanupPathWithDocker(targetPath) {
  runCommand("docker", [
    "run",
    "--rm",
    "-v",
    `${targetPath}:/work`,
    "alpine:3.24",
    "sh",
    "-lc",
    "chmod -R u+w /work 2>/dev/null || true; rm -rf /work/* /work/.[!.]* /work/..?* 2>/dev/null || true",
  ]);
}

async function prepareFixtureDir(prefix, sourceRelativeDir) {
  const tempDir = await fs.mkdtemp(path.join(os.tmpdir(), prefix));
  await fs.copy(path.join(repoRoot, sourceRelativeDir), tempDir);
  return tempDir;
}

async function preparePhpFixture() {
  const tempDir = await fs.mkdtemp(path.join(os.tmpdir(), "megalinter-php-"));
  await fs.copy(
    path.join(repoRoot, ".automation", "test", "php", ".php-cs-fixer.risky.php"),
    path.join(tempDir, ".php-cs-fixer.risky.php"),
  );
  await fs.copy(
    path.join(repoRoot, ".automation", "test", "php", "php_good_1.php"),
    path.join(tempDir, "php_good_1.php"),
  );
  await fs.copy(
    path.join(repoRoot, ".automation", "test", "php", "php_good_2.php"),
    path.join(tempDir, "php_good_2.php"),
  );
  return tempDir;
}

async function runFixture(pathToLint, enabledLinter, runtimeMode) {
  const res = runCommand("docker", [
    "run",
    "--rm",
    ...runtimeMode.dockerArgs,
    "-v",
    `${pathToLint}:/tmp/lint:rw`,
    "-e",
    "DEFAULT_WORKSPACE=/tmp/lint",
    "-e",
    `ENABLE_LINTERS=${enabledLinter}`,
    "-e",
    "PLUGINS=",
    ...runtimeMode.envArgs,
    image,
  ]);
  const details = [res.stderr, res.stdout].filter(Boolean).join("\n");
  assert.strictEqual(
    res.status,
    0,
    details
      ? `status is 0 (${res.status} returned)\n${details}`
      : `status is 0 (${res.status} returned)`,
  );
  return details;
}

async function runFixtureWithRunner(pathToLint, enabledLinter) {
  const args = [
    runnerCli,
    "--path",
    pathToLint,
    "--release",
    release,
    "--env",
    `ENABLE_LINTERS=${enabledLinter}`,
    "--env",
    "PLUGINS=",
  ];
  if (nodockerpull) {
    args.push("--nodockerpull");
  }
  if (image) {
    args.push("--image", image);
  }
  const res = runCommand("node", args, { cwd: repoRoot });
  const details = [res.stderr, res.stdout].filter(Boolean).join("\n");
  assert.strictEqual(
    res.status,
    0,
    details
      ? `status is 0 (${res.status} returned)\n${details}`
      : `status is 0 (${res.status} returned)`,
  );
}

async function withFixtureDir(prepare, callback) {
  const tempDir = await prepare();
  try {
    await callback(tempDir);
  } finally {
    cleanupPathWithDocker(tempDir);
    await fs.remove(tempDir);
  }
}

const runtimeFixtureCases = [
  {
    title: "PHP_PHPCSFIXER",
    prepare: preparePhpFixture,
    enabledLinter: "PHP_PHPCSFIXER",
    successPattern:
      /✅ Linted \[PHP\] files with \[php-cs-fixer\] successfully/,
  },
  {
    title: "CSHARP_CSHARPIER",
    prepare: () =>
      prepareFixtureDir(
        "megalinter-csharp-",
        path.join(".automation", "test", "csharp_csharpier", "good"),
      ),
    enabledLinter: "CSHARP_CSHARPIER",
    successPattern:
      /✅ Linted \[CSHARP\] files with \[csharpier\] successfully/,
  },
  {
    title: "RUST_CLIPPY",
    prepare: () =>
      prepareFixtureDir(
        "megalinter-rust-",
        path.join(".automation", "test", "rust", "good"),
      ),
    enabledLinter: "RUST_CLIPPY",
    successPattern: /✅ Linted \[RUST\] files with \[clippy\] successfully/,
  },
  {
    title: "JSON_NPM_PACKAGE_JSON_LINT",
    prepare: () =>
      prepareFixtureDir(
        "megalinter-npm-pkg-",
        path.join(".automation", "test", "npm_package_json_lint", "good"),
      ),
    enabledLinter: "JSON_NPM_PACKAGE_JSON_LINT",
    successPattern:
      /✅ Linted \[JSON\] files with \[npm-package-json-lint\] successfully/,
  },
  {
    title: "SALESFORCE_CODE_ANALYZER_APEX",
    prepare: () =>
      prepareFixtureDir(
        "megalinter-salesforce-",
        path.join(".automation", "test", "salesforce", "good"),
      ),
    enabledLinter: "SALESFORCE_CODE_ANALYZER_APEX",
    successPattern:
      /✅ Linted \[SALESFORCE\] files with \[code-analyzer-apex\] successfully/,
  },
];

describe("Runtime image", function () {
  if (!image) {
    it("requires MEGALINTER_IMAGE for runtime coverage", function () {
      this.skip();
    });
    return;
  }

  for (const runtimeMode of runtimeModes) {
    for (const testCase of runtimeFixtureCases) {
      it(`runs ${testCase.title} on the good fixture in ${runtimeMode.label} mode`, async () => {
        await withFixtureDir(testCase.prepare, async (tempDir) => {
          const details = await runFixture(
            tempDir,
            testCase.enabledLinter,
            runtimeMode,
          );
          assert.match(details, testCase.successPattern);
        });
      }).timeout(600000);
    }
  }

  for (const testCase of runtimeFixtureCases) {
    it(`runs ${testCase.title} on the good fixture with mega-linter-runner`, async () => {
      await withFixtureDir(testCase.prepare, async (tempDir) => {
        await runFixtureWithRunner(tempDir, testCase.enabledLinter);
      });
    }).timeout(600000);
  }

  for (const runtimeMode of runtimeModes) {
    it(`accepts an SSH connection in ${runtimeMode.label} mode`, async () => {
      const tempDir = await fs.mkdtemp(path.join(os.tmpdir(), "megalinter-ssh-"));
      const containerName = `megalinter-ssh-${runtimeMode.id}-${Date.now()}`;
      const privateKey = path.join(tempDir, "id_rsa");
      const publicKey = path.join(tempDir, "id_rsa.pub");
      try {
        assertSuccess(
          runCommand("ssh-keygen", [
            "-q",
            "-t",
            "ed25519",
            "-N",
            "",
            "-f",
            privateKey,
          ]),
          "expected ssh-keygen to create a temporary test key",
        );

        const runRes = runCommand("docker", [
          "run",
          "-d",
          "--rm",
          "--name",
          containerName,
          ...runtimeMode.dockerArgs,
          "-e",
          "MEGALINTER_SSH=true",
          ...runtimeMode.envArgs,
          "-v",
          `${tempDir}:/tmp/docker_ssh:ro`,
          "-p",
          `127.0.0.1::${runtimeMode.sshPort}`,
          image,
        ]);
        if (runRes.status !== 0) {
          const details = [runRes.stderr, runRes.stdout].filter(Boolean).join("\n");
          const logs = readDockerLogs(containerName);
          assert.strictEqual(
            runRes.status,
            0,
            [details, logs].filter(Boolean).join("\n"),
          );
        }

        const portRes = runCommand("docker", [
          "port",
          containerName,
          `${runtimeMode.sshPort}/tcp`,
        ]);
        if (portRes.status !== 0) {
          const details = [portRes.stderr, portRes.stdout].filter(Boolean).join("\n");
          const logs = readDockerLogs(containerName);
          assert.strictEqual(
            portRes.status,
            0,
            [
              `expected SSH test container to publish port ${runtimeMode.sshPort}`,
              details,
              logs,
            ]
              .filter(Boolean)
              .join("\n"),
          );
        }
        const publishedPort = portRes.stdout.trim().split(":").pop();
        assert(publishedPort, "expected a published SSH port");

        let sshResult = null;
        for (let attempt = 0; attempt < 30; attempt += 1) {
          sshResult = runCommand("ssh", [
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "UserKnownHostsFile=/dev/null",
            "-i",
            privateKey,
            "-p",
            publishedPort,
            `${runtimeMode.sshUser}@127.0.0.1`,
            "id -u",
          ]);
          if (sshResult.status === 0) {
            break;
          }
          await new Promise((resolve) => setTimeout(resolve, 1000));
        }

        if (sshResult.status !== 0) {
          assert.strictEqual(
            sshResult.status,
            0,
            [
              "expected SSH login to succeed",
              [sshResult.stderr, sshResult.stdout].filter(Boolean).join("\n"),
              readDockerLogs(containerName),
            ]
              .filter(Boolean)
              .join("\n"),
          );
        }
        assert.strictEqual(sshResult.stdout.trim(), runtimeMode.sshExpectedUid);
        assert(await fs.pathExists(publicKey), "expected SSH public key to exist");
      } finally {
        runCommand("docker", ["rm", "-f", containerName]);
        cleanupPathWithDocker(tempDir);
        await fs.remove(tempDir);
      }
    }).timeout(180000);
  }
});
