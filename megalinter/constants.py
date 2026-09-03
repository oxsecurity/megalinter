from megalinter import config

ML_REPO_OWNER = "oxsecurity"
ML_REPO_NAME = "megalinter"
ML_REPO = f"{ML_REPO_OWNER}/{ML_REPO_NAME}"
ML_REPO_URL = f"https://github.com/{ML_REPO_OWNER}/{ML_REPO_NAME}"
ML_DOC_URL_BASE = "https://megalinter.io/"
ML_VERSION = config.get(None, "BUILD_VERSION", "latest").replace("v", "")
ML_DOC_URL = ML_DOC_URL_BASE + (ML_VERSION if len(ML_VERSION) > 1 else "latest")
ML_REPO_ISSUES_URL = f"https://github.com/{ML_REPO_OWNER}/{ML_REPO_NAME}/issues"
ML_DOC_URL_DESCRIPTORS_ROOT = f"{ML_DOC_URL}/descriptors"


ML_DOCKER_OWNER = "oxsecurity"
ML_DOCKER_NAME = "megalinter"
ML_DOCKER_IMAGE_HOST = "ghcr.io"
DOCKER_PACKAGES_ROOT_URL = "https://hub.docker.com/v2/repositories"
ML_DOCKER_IMAGE_WITH_HOST = f"{ML_DOCKER_IMAGE_HOST}/{ML_DOCKER_OWNER}/{ML_DOCKER_NAME}"
ML_DOCKER_IMAGE = f"{ML_DOCKER_OWNER}/{ML_DOCKER_NAME}"
ML_DOCKER_IMAGE_LEGACY = "nvuillam/mega-linter"
ML_DOCKER_IMAGE_LEGACY_V5 = "megalinter/megalinter"

DEFAULT_DOCKER_WORKSPACE_DIR = "/tmp/lint"
DEFAULT_REPORT_FOLDER_NAME = "megalinter-reports"
DEFAULT_SARIF_REPORT_FILE_NAME = "megalinter-report.sarif"
DEFAULT_MARKDOWN_SUMMARY_REPORT_FILE_NAME = "megalinter-report.md"
DEFAULT_SARIF_SCHEMA_URI = "https://json.schemastore.org/sarif-2.1.0.json"
DEFAULT_SARIF_VERSION = "2.1.0"
# MAJOR-RELEASE-IMPACTED
DEFAULT_RELEASE = "v10"

# Ruleset used to mask secrets in linter outputs. Vendored from the pinned tag
# by .automation/vendor_betterleaks_ruleset.py during documentation builds.
BETTERLEAKS_RULESET_FILE_NAME = "betterleaks-default.toml"
BETTERLEAKS_RULESET_REPO = "betterleaks/betterleaks"
# renovate: datasource=github-tags depName=betterleaks/betterleaks
BETTERLEAKS_RULESET_VERSION = "v1.8.1"

DEFAULT_DOCKERFILE_ARGS: list[str] = [
    "ARG TARGETPLATFORM",
    "ARG TARGETARCH",
]

DEFAULT_DOCKERFILE_APK_PACKAGES = [
    "bash",
    "ca-certificates",
    "curl",
    # glibc compatibility shim so prebuilt linux-x86_64-unknown-linux-gnu
    # binaries (zizmor, sarif-fmt, shellcheck-sarif, …) run on the Alpine
    # base, including in standalone per-linter images.
    "gcompat",
    "git",
    "git-lfs",
    # runtime libraries (libgcc_s.so.1, libstdc++.so.6) needed by Rust and C++
    # prebuilt binaries (sarif-fmt, shellcheck-sarif, zizmor, vale, …); they
    # were previously pulled in transitively by the gcc package, which is now
    # evicted from final layers
    "libgcc",
    "libstdc++",
    "openssh",
    # su-exec for user switch in entrypoint
    "su-exec",
]

# Compilation toolchain needed only while pip/npm/gem install steps build native
# extensions: installed as an apk virtual package at the beginning of those steps
# and removed at their end, so it never weighs in the final image layers.
# A descriptor whose linter needs the toolchain at RUNTIME must declare the
# packages in its own install.apk list.
DEFAULT_DOCKERFILE_BUILD_APK_PACKAGES = [
    "gcc",
    "libffi-dev",
    "make",
    "musl-dev",
    # native gem extensions need the ruby headers at build time only
    "ruby-dev",
]

DEFAULT_DOCKERFILE_NPM_ARGS: list[str] = []

DEFAULT_DOCKERFILE_NPM_APK_PACKAGES = [
    "npm",
    "nodejs-current",
    "yarn",
]

DEFAULT_DOCKERFILE_GEM_ARGS: list[str] = []

# gems are installed with --no-document, so rdoc is not needed; ruby-dev is
# only needed while native extensions compile and lives in the build list
DEFAULT_DOCKERFILE_GEM_APK_PACKAGES = [
    "ruby",
    "ruby-bundler",
]

DEFAULT_DOCKERFILE_PIP_ARGS = [
    "# renovate: datasource=pypi depName=pip\nARG PIP_PIP_VERSION=26.2.1",
]

DEFAULT_DOCKERFILE_PIPENV_ARGS = [
    "# renovate: datasource=pypi depName=virtualenv\nARG PIP_VIRTUALENV_VERSION=21.7.5",
]

DEFAULT_DOCKERFILE_RUST_ARGS = [
    "# renovate: datasource=github-tags depName=rust-lang/rust\nARG RUST_RUST_VERSION=1.98.0",
]

DEFAULT_DOCKERFILE_FLAVOR_ARGS = [
    "# renovate: datasource=crate depName=sarif-fmt\nARG CARGO_SARIF_FMT_VERSION=0.8.0",
]

# sarif-fmt: always build from source on Alpine so the resulting binary is
# linked against musl libc and runs reliably in the Alpine-based runtime image.
# Upstream only ships a glibc x86_64 prebuilt, which segfaults under gcompat.
DEFAULT_DOCKERFILE_FLAVOR_FROM_STAGES = [
    "FROM alpine:3.24 AS cargo-bin-sarif-fmt\n"
    "ARG CARGO_SARIF_FMT_VERSION\n"
    "RUN set -eu; \\\n"
    "    apk add --no-cache build-base musl-dev openssl-dev"
    " openssl-libs-static pkgconfig bash perl rust cargo && \\\n"
    "    mkdir -p /out/bin && \\\n"
    "    cargo install --force --locked --root /out"
    ' "sarif-fmt@${CARGO_SARIF_FMT_VERSION}"; \\\n'
    "    chmod +x /out/bin/sarif-fmt",
]

DEFAULT_DOCKERFILE_FLAVOR_COPY_LINES = [
    "COPY --link --from=cargo-bin-sarif-fmt /out/bin/sarif-fmt /usr/bin/sarif-fmt",
]

DEFAULT_DOCKERFILE_FLAVOR_CARGO_PACKAGES: list[str] = []

OX_MARKDOWN_LINK = (
    "[![MegaLinter is provided by OX Security]"
    + "(https://raw.githubusercontent.com/oxsecurity/megalinter/main/"
    + "docs/assets/images/ox-banner.png)]"
    + "(https://www.ox.security/?ref=megalinter)"
)
