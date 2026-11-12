#!/usr/bin/env python3
# Generates megalinter/descriptors/native-locks/** from the `native_install` descriptor properties
# and the `provision` blocks of native-runtimes.yml.
#
# Every artifact is downloaded, verified with the strongest mechanism declared in its `provenance`
# (GitHub attestation, cosign, GPG, upstream checksums file), then pinned by sha256 in the lock.
# A version already locked whose artifact changed upstream is a hard failure (re-tagged release).
import argparse
import base64
import codecs
import gzip
import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

REPO_HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_HOME)

from megalinter.native import lock as native_lock  # noqa: E402
from megalinter.native.catalog import load_native_specs  # noqa: E402
from megalinter.native.context import NativeError  # noqa: E402
from megalinter.native.download import build_opener, check_https  # noqa: E402
from megalinter.native.resolve import (  # noqa: E402
    NATIVE_PLATFORMS,
    platform_native_install,
    resolve_native_install,
)
from megalinter.native.runtimes import load_runtime_catalog  # noqa: E402

KEYS_DIR = os.path.join(REPO_HOME, ".automation", "native-keys")
DOWNLOAD_WORKERS = 6
# Bump the version of a method when its lock content changes: existing locks are regenerated
GENERATOR_VERSIONS = {"npm": 2, "gem": 2}
# A frozen bundle only installs on a platform listed in Gemfile.lock: list every native one, Windows included
GEM_PLATFORMS = [
    "x86_64-linux",
    "aarch64-linux",
    "x86_64-darwin",
    "arm64-darwin",
    "x64-mingw-ucrt",
]
COMMAND_TIMEOUT_SECONDS = 1800
NPM_SIGNATURES_TIMEOUT_SECONDS = 900
# gh and cosign share a sigstore TUF cache that does not support concurrent refreshes
SIGSTORE_LOCK = threading.Lock()


def run(command, cwd=None, timeout=COMMAND_TIMEOUT_SECONDS):
    process = subprocess.run(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        check=False,
    )
    output = process.stdout.decode("utf-8", errors="replace")
    if process.returncode != 0:
        raise NativeError(
            f"{' '.join(command)} failed ({process.returncode}):\n{output}"
        )
    return output


def require_tool(name):
    found = shutil.which(name)
    if found is None:
        raise NativeError(f"{name} is required to generate native locks")
    return found


def render(template, version, asset_name=None):
    value = template.replace("{{VERSION}}", str(version)).replace(
        "{{VERSION_NO_V}}", str(version).lstrip("v")
    )
    if asset_name is not None:
        value = value.replace("{{ASSET_NAME}}", asset_name)
    return value


def download(url, folder, name=None):
    check_https(url)
    target = os.path.join(folder, name or os.path.basename(url.split("?")[0]) or "file")
    digest = hashlib.sha256()
    size = 0
    request = urllib.request.Request(
        url, headers={"User-Agent": "megalinter-native-lock"}
    )
    with (
        build_opener().open(request, timeout=120) as response,
        open(target, "wb") as out,
    ):
        for chunk in iter(lambda: response.read(1 << 18), b""):
            digest.update(chunk)
            size += len(chunk)
            out.write(chunk)
    return target, digest.hexdigest(), size


BARE_HASH_KEY = ""
HEX_DIGEST_REGEX = re.compile(r"^[0-9a-fA-F]{64,128}$")


def parse_checksums(path):
    with open(path, "rb") as f:
        raw = f.read()
    if raw.startswith((codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)):
        text = raw.decode("utf-16")
    else:
        text = raw.decode("utf-8-sig", errors="replace")
    entries = {}
    for line in text.splitlines():
        parts = line.strip().split(None, 1)
        if len(parts) == 2:
            entries[os.path.basename(parts[1].lstrip("*"))] = parts[0].lower()
        elif len(parts) == 1 and HEX_DIGEST_REGEX.match(parts[0]):
            entries[BARE_HASH_KEY] = parts[0].lower()
    return entries


def file_digest(path, algorithm):
    digest = hashlib.new(algorithm)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 18), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_cosign(provenance, version, target_file, folder, asset_name):
    cosign = require_tool("cosign")
    cosign_info = provenance["cosign"]
    if cosign_info.get("identity"):
        identity = render(cosign_info["identity"], version)
        command = [cosign, "verify-blob", "--certificate-identity", identity]
    else:
        identity = render(cosign_info["identity_regexp"], version)
        command = [cosign, "verify-blob", "--certificate-identity-regexp", identity]
    command += ["--certificate-oidc-issuer", cosign_info["issuer"]]
    for key, option, file_name in (
        ("bundle_url", "--bundle", "cosign.sigstore.json"),
        ("signature_url", "--signature", "cosign.sig"),
        ("certificate_url", "--certificate", "cosign.pem"),
    ):
        if cosign_info.get(key):
            downloaded, _, _ = download(
                render(cosign_info[key], version, asset_name), folder, file_name
            )
            command += [option, downloaded]
    run_sigstore([*command, target_file])
    return "cosign:" + identity


def verify_gpg(provenance, version, target_file, folder, asset_name):
    gpg = require_tool("gpg")
    gpg_info = provenance["gpg"]
    signature, _, _ = download(
        render(gpg_info["signature_url"], version, asset_name), folder, "gpg.sig"
    )
    keyring = os.path.join(KEYS_DIR, gpg_info["keyring"])
    if not os.path.isfile(keyring):
        raise NativeError(f"GPG keyring not found: {keyring}")
    home = tempfile.mkdtemp(dir=folder)
    run([gpg, "--homedir", home, "--batch", "--import", keyring])
    run(
        [
            gpg,
            "--homedir",
            home,
            "--batch",
            "--trust-model",
            "always",
            "--verify",
            signature,
            target_file,
        ]
    )
    return "gpg:" + gpg_info["keyring"]


SIGSTORE_RETRIES = 3
SIGSTORE_RETRY_DELAY_SECONDS = 15
RELEASE_TAG_REGEX = re.compile(r"/releases/download/([^/]+)/")


def run_sigstore(command):
    for attempt in range(1, SIGSTORE_RETRIES + 1):
        try:
            with SIGSTORE_LOCK:
                return run(command)
        except NativeError as e:
            # The sigstore trust root download (TUF) fails transiently on a cold cache
            if "Sigstore verifier" not in str(e) or attempt == SIGSTORE_RETRIES:
                raise
            time.sleep(SIGSTORE_RETRY_DELAY_SECONDS)


# Build provenance attestation (actions/attest-build-provenance), else attestation of an
# immutable GitHub release (gh release verify-asset): both are signed by GitHub
def verify_github_attestation(repository, asset_file, asset_url):
    gh = require_tool("gh")
    try:
        run_sigstore([gh, "attestation", "verify", asset_file, "--repo", repository])
        return "github_attestation:" + repository
    except NativeError as build_error:
        tag = RELEASE_TAG_REGEX.search(asset_url)
        if tag is None:
            raise
        try:
            run_sigstore(
                [
                    gh,
                    "release",
                    "verify-asset",
                    tag.group(1),
                    asset_file,
                    "--repo",
                    repository,
                ]
            )
        except NativeError as release_error:
            raise NativeError(f"{build_error}\n{release_error}") from release_error
        return f"github_release_attestation:{repository}@{tag.group(1)}"


def verify_asset(provenance, version, asset_file, asset_url, sha256, folder):
    verifications = []
    asset_name = os.path.basename(asset_url.split("?")[0])
    if provenance.get("unverified"):
        return ["unverified: " + provenance["unverified"]]
    checksums_file = None
    if provenance.get("checksums_url"):
        checksums_file, _, _ = download(
            render(provenance["checksums_url"], version, asset_name),
            folder,
            "checksums.txt",
        )
        algorithm = (
            "sha512" if provenance.get("checksums_format") == "sha512sum" else "sha256"
        )
        entries = parse_checksums(checksums_file)
        expected = entries.get(asset_name) or entries.get(BARE_HASH_KEY)
        if expected is None:
            raise NativeError(
                f"{asset_name} not listed in {provenance['checksums_url']}"
            )
        if file_digest(asset_file, algorithm) != expected:
            raise NativeError(
                f"{asset_url}: checksum differs from the upstream checksums file"
            )
        verifications.append("checksums_url")
    if provenance.get("cosign"):
        verifications.append(
            verify_cosign(
                provenance, version, checksums_file or asset_file, folder, asset_name
            )
        )
    if provenance.get("gpg"):
        verifications.append(
            verify_gpg(
                provenance, version, checksums_file or asset_file, folder, asset_name
            )
        )
    if provenance.get("github_attestation"):
        verifications.append(
            verify_github_attestation(
                provenance["github_attestation"], asset_file, asset_url
            )
        )
    if not verifications:
        raise NativeError("provenance declares no verification mechanism")
    return verifications


def lock_asset(asset, provenance, version, folder):
    url = render(asset["url"], version)
    asset_folder = tempfile.mkdtemp(dir=folder)
    path, sha256, size = download(url, asset_folder)
    verification = verify_asset(provenance, version, path, url, sha256, asset_folder)
    entry = {
        "url": url,
        "sha256": sha256,
        "size": size,
        "archive": asset.get("archive", "none"),
        "verification": verification,
    }
    if asset.get("strip_components"):
        entry["strip_components"] = asset["strip_components"]
    if asset.get("name"):
        entry["name"] = asset["name"]
    return entry


def assets_for_platform(effective, platform):
    assets = effective.get("assets") or {}
    return assets.get(platform) or assets.get("any")


def lock_binary(key, resolved, folder, previous):
    platforms = {}
    jobs = {}
    with ThreadPoolExecutor(max_workers=DOWNLOAD_WORKERS) as pool:
        for platform in resolved.get("platforms", []):
            effective = platform_native_install(resolved, platform)
            asset = assets_for_platform(effective, platform)
            jobs[platform] = pool.submit(
                lock_asset, asset, effective["provenance"], effective["version"], folder
            )
        for platform, job in jobs.items():
            entry = job.result()
            platforms[platform] = {"version": resolved["version"], "assets": [entry]}
            check_immutable(key, previous, platform, entry)
    return {"platforms": platforms}


def check_immutable(key, previous, platform, entry):
    if not previous:
        return
    old_platform = (previous.get("platforms") or {}).get(platform) or {}
    for old_asset in old_platform.get("assets", []):
        if old_asset["url"] == entry["url"] and old_asset["sha256"] != entry["sha256"]:
            raise NativeError(
                f"{key} {platform}: {entry['url']} changed upstream "
                f"({old_asset['sha256']} -> {entry['sha256']}). Review, then re-run with --accept-changes"
            )


def parse_npm_package(package):
    name, _, version = package.rpartition("@")
    if name == "":
        return package, "latest"
    return name, version


# Platform-specific packages reachable only through optionalDependencies are optional for npm, but
# packages vendored with their own shrinkwrap (esbuild in @salesforce/plugin-code-analyzer) are
# locked without the flag, and npm ci then fails with EBADPLATFORM on the other platforms
def mark_platform_packages_optional(package_lock):
    packages = package_lock.get("packages", {})
    optional_names = set()
    required_names = set()
    for entry in packages.values():
        optional_names.update((entry.get("optionalDependencies") or {}).keys())
        required_names.update((entry.get("dependencies") or {}).keys())
    for path, entry in packages.items():
        name = path.rsplit("node_modules/", 1)[-1]
        if (
            path
            and (entry.get("os") or entry.get("cpu"))
            and name in optional_names
            and name not in required_names
        ):
            entry["optional"] = True
    return package_lock


def lock_npm(key, resolved, folder, verify_signatures):
    work = tempfile.mkdtemp(dir=folder)
    dependencies = dict(parse_npm_package(package) for package in resolved["packages"])
    with open(os.path.join(work, "package.json"), "w", encoding="utf-8") as f:
        json.dump(
            {
                "name": "megalinter-native-" + key.lower(),
                "version": "0.0.0",
                "private": True,
                "dependencies": dependencies,
            },
            f,
        )
    npm = require_tool("npm")
    run(
        [
            npm,
            "install",
            "--package-lock-only",
            "--ignore-scripts",
            "--no-audit",
            "--no-fund",
        ],
        cwd=work,
    )
    if verify_signatures:
        run(
            [npm, "ci", "--ignore-scripts", "--no-audit", "--no-fund"],
            cwd=work,
            timeout=NPM_SIGNATURES_TIMEOUT_SECONDS,
        )
        run(
            [npm, "audit", "signatures"],
            cwd=work,
            timeout=NPM_SIGNATURES_TIMEOUT_SECONDS,
        )
    with open(os.path.join(work, "package.json"), "r", encoding="utf-8") as f:
        package_json = json.load(f)
    with open(os.path.join(work, "package-lock.json"), "r", encoding="utf-8") as f:
        package_lock = mark_platform_packages_optional(json.load(f))
    return {"common": {"package_json": package_json, "package_lock": package_lock}}


def python_version_floor(resolved):
    for requirement in resolved.get("requires", []):
        if requirement["runtime"] == "python" and requirement.get(
            "version", ""
        ).startswith(">="):
            return requirement["version"][2:]
    return None


def lock_pip(key, resolved, folder):
    work = tempfile.mkdtemp(dir=folder)
    requirements_in = os.path.join(work, "requirements.in")
    with open(requirements_in, "w", encoding="utf-8") as f:
        f.write("\n".join(resolved["packages"]) + "\n")
    command = [
        require_tool("uv"),
        "pip",
        "compile",
        "--universal",
        "--generate-hashes",
        "--no-header",
        "--no-annotate",
        "--no-config",
        requirements_in,
        "-o",
        os.path.join(work, "requirements.txt"),
    ]
    floor = python_version_floor(resolved)
    if resolved.get("allow_source_build") is None:
        command += ["--only-binary", ":all:"]
    if floor:
        command += ["--python-version", floor]
    run(command)
    with open(os.path.join(work, "requirements.txt"), "r", encoding="utf-8") as f:
        return {"common": {"requirements": f.read()}}


def lock_gem(key, resolved, folder):
    work = tempfile.mkdtemp(dir=folder)
    lines = ['source "https://rubygems.org"']
    for package in resolved["packages"]:
        name, _, version = package.partition(":")
        lines.append(f'gem "{name}"' + (f', "{version}"' if version else ""))
    with open(os.path.join(work, "Gemfile"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    bundle = require_tool("bundle")
    run([bundle, "lock", "--add-checksums", "--add-platform", *GEM_PLATFORMS], cwd=work)
    with open(os.path.join(work, "Gemfile"), "r", encoding="utf-8") as f:
        gemfile = f.read()
    with open(os.path.join(work, "Gemfile.lock"), "r", encoding="utf-8") as f:
        gemfile_lock = f.read()
    return {"common": {"gemfile": gemfile, "gemfile_lock": gemfile_lock}}


GZIP_MAGIC = bytes([0x1F, 0x8B])


def read_json_url(url):
    with build_opener().open(url, timeout=60) as response:
        content = response.read()
    # NuGet registration endpoints answer gzip-compressed documents
    if content[:2] == GZIP_MAGIC:
        content = gzip.decompress(content)
    return json.loads(content)


def nuget_package_hash(package, version):
    leaf = read_json_url(
        f"https://api.nuget.org/v3/registration5-gz-semver2/{package.lower()}/{version.lower()}.json"
    )
    return read_json_url(leaf["catalogEntry"])["packageHash"]


def lock_dotnet_tool(key, resolved, folder):
    package = resolved["packages"][0]
    version = resolved["version"]
    lower = package.lower()
    url = f"https://api.nuget.org/v3-flatcontainer/{lower}/{version.lower()}/{lower}.{version.lower()}.nupkg"
    work = tempfile.mkdtemp(dir=folder)
    path, sha256, size = download(url, work)
    registry_hash = base64.b64decode(nuget_package_hash(package, version)).hex()
    if file_digest(path, "sha512") != registry_hash:
        raise NativeError(
            f"{package} {version}: nupkg differs from the NuGet registry hash"
        )
    entry = {
        "package": package,
        "version": version,
        "assets": [
            {
                "url": url,
                "sha256": sha256,
                "size": size,
                "name": f"{lower}.{version.lower()}.nupkg",
                "verification": ["nuget_registry_sha512"],
            }
        ],
    }
    return {
        "platforms": {platform: entry for platform in resolved.get("platforms", [])}
    }


def lock_go(key, resolved, folder):
    go = require_tool("go")
    sums = {}
    env = {
        **os.environ,
        "GOFLAGS": "-mod=mod",
        "GOTOOLCHAIN": "local",
        "GONOSUMDB": "",
        "GOSUMDB": "sum.golang.org",
    }
    for package in resolved["packages"]:
        module = package.split("@")[0]
        version = package.split("@")[1]
        process = subprocess.run(
            [go, "mod", "download", "-json", f"{module}@{version}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            check=False,
            cwd=tempfile.mkdtemp(dir=folder),
        )
        if process.returncode != 0:
            raise NativeError(process.stdout.decode("utf-8", errors="replace"))
        sums[package] = json.loads(process.stdout)["Sum"]
    return {"common": {"packages": resolved["packages"], "sums": sums}}


def lock_powershell_module(key, resolved, folder):
    entries = []
    for package in resolved["packages"]:
        name, _, pinned = package.partition("@")
        version = pinned or resolved["version"]
        url = f"https://www.powershellgallery.com/api/v2/package/{name}/{version}"
        work = tempfile.mkdtemp(dir=folder)
        path, sha256, size = download(url, work, f"{name}.{version}.nupkg")
        entries.append(
            {
                "url": url,
                "sha256": sha256,
                "size": size,
                "module": name,
                "module_version": version,
                "verification": ["powershell_gallery_pinned_on_first_download"],
            }
        )
    entry = {"assets": entries}
    return {
        "platforms": {platform: entry for platform in resolved.get("platforms", [])}
    }


LOCKERS = {
    "binary": lambda key, resolved, folder, previous, options: lock_binary(
        key, resolved, folder, previous
    ),
    "npm": lambda key, resolved, folder, previous, options: lock_npm(
        key, resolved, folder, options.verify_signatures
    ),
    "pip": lambda key, resolved, folder, previous, options: lock_pip(
        key, resolved, folder
    ),
    "gem": lambda key, resolved, folder, previous, options: lock_gem(
        key, resolved, folder
    ),
    "dotnet_tool": lambda key, resolved, folder, previous, options: lock_dotnet_tool(
        key, resolved, folder
    ),
    "go": lambda key, resolved, folder, previous, options: lock_go(
        key, resolved, folder
    ),
    "powershell_module": lambda key, resolved, folder, previous, options: lock_powershell_module(
        key, resolved, folder
    ),
    "runtime_provided": lambda key, resolved, folder, previous, options: {},
}


def read_previous(key):
    try:
        return native_lock.load_lock(key)
    except NativeError:
        return None


def lock_linter(spec, options, folder):
    if spec.linter.get("disabled") is True:
        return "skipped (disabled linter)"
    resolved = resolve_native_install(spec)
    previous = read_previous(spec.key)
    spec_hash = native_lock.compute_spec_hash(resolved)
    generator = GENERATOR_VERSIONS.get(resolved["method"], 1)
    if (
        previous
        and previous.get("spec_hash") == spec_hash
        and previous.get("generator", 1) >= generator
        and not options.force
    ):
        return "unchanged"
    if options.accept_changes:
        previous = None
    method = resolved["method"]
    if method not in LOCKERS:
        raise NativeError(f"{spec.key}: no lock generator for method {method}")
    content = LOCKERS[method](spec.key, resolved, folder, previous, options)
    native_lock.write_lock(
        spec.key,
        {
            "linter": spec.key,
            "method": method,
            "spec_hash": spec_hash,
            "generator": generator,
            **content,
        },
    )
    return "locked"


def runtime_provision_resolved(definition):
    provision = definition["provision"]
    platforms = [p for p in NATIVE_PLATFORMS if p in (provision.get("assets") or {})]
    return {
        "version": provision["version"],
        "assets": provision["assets"],
        "provenance": provision.get("provenance") or {},
        "platforms": platforms,
    }


def lock_runtime(name, definition, options, folder):
    provision = definition.get("provision") or {}
    if not provision.get("assets"):
        return "skipped"
    resolved = runtime_provision_resolved(definition)
    path = native_lock.runtime_lock_path(name)
    spec_hash = native_lock.compute_spec_hash(resolved)
    if os.path.isfile(path) and not options.force:
        with open(path, "r", encoding="utf-8") as f:
            if json.load(f).get("spec_hash") == spec_hash:
                return "unchanged"
    content = lock_binary("runtime " + name, resolved, folder, None)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(
            {
                "@generated": native_lock.LOCK_HEADER,
                "format": native_lock.LOCK_FORMAT_VERSION,
                "runtime": name,
                "spec_hash": spec_hash,
                **content,
            },
            f,
            indent=2,
            sort_keys=True,
        )
        f.write("\n")
    return "locked"


def check_locks(specs):
    stale = []
    for spec in specs:
        if spec.linter.get("disabled") is True:
            continue
        previous = read_previous(spec.key)
        resolved = resolve_native_install(spec)
        if previous is None or previous.get(
            "spec_hash"
        ) != native_lock.compute_spec_hash(resolved):
            stale.append(spec.key)
    return stale


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate native install locks")
    parser.add_argument(
        "only", nargs="*", help="Linter keys or descriptor ids (default: all)"
    )
    parser.add_argument(
        "--check", action="store_true", help="Only report missing or stale locks"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate even when the descriptor did not change",
    )
    parser.add_argument(
        "--accept-changes",
        action="store_true",
        help="Accept upstream changes of an already locked version",
    )
    parser.add_argument(
        "--verify-signatures",
        action="store_true",
        help="Run npm audit signatures on npm locks",
    )
    parser.add_argument(
        "--runtimes",
        action="store_true",
        help="Also lock the runtimes of native-runtimes.yml",
    )
    options = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    specs = load_native_specs(only=set(options.only) or None)
    if options.check:
        stale = check_locks(specs)
        for key in stale:
            logging.error(f"{key}: native lock missing or stale")
        return 1 if stale else 0
    failures = []
    folder = tempfile.mkdtemp(prefix="native-lock-")
    try:
        for spec in specs:
            try:
                logging.info(f"{spec.key}: {lock_linter(spec, options, folder)}")
            except (
                Exception
            ) as e:  # noqa: BLE001 - report every failing lock and continue
                logging.error(f"{spec.key}: FAILED: {e}")
                failures.append(spec.key)
        if options.runtimes:
            for name, definition in load_runtime_catalog().items():
                try:
                    logging.info(
                        f"runtime {name}: {lock_runtime(name, definition, options, folder)}"
                    )
                except (
                    Exception
                ) as e:  # noqa: BLE001 - report every failing lock and continue
                    logging.error(f"runtime {name}: FAILED: {e}")
                    failures.append("runtime " + name)
    finally:
        shutil.rmtree(folder, ignore_errors=True)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
