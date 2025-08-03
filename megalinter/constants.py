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
GHCR_PACKAGES_ROOT_URL = "https://github.com/oxsecurity/megalinter/pkgs/container"
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
DEFAULT_RELEASE = "v8"

DEFAULT_DOCKERFILE_ARGS: list[str] = []

DEFAULT_DOCKERFILE_APK_PACKAGES = [
    "bash",
    "ca-certificates",
    "curl",
    "gcc",
    "git",
    "git-lfs",
    "libffi-dev",
    "make",
    "musl-dev",
    "openssh",
]

DEFAULT_DOCKERFILE_DOCKER_ARGS: list[str] = []

DEFAULT_DOCKERFILE_DOCKER_APK_PACKAGES = [
    "docker",
    "openrc",
]

DEFAULT_DOCKERFILE_NPM_ARGS: list[str] = []

DEFAULT_DOCKERFILE_NPM_APK_PACKAGES = [
    "npm",
    "nodejs-current",
    "yarn",
]

DEFAULT_DOCKERFILE_GEM_ARGS: list[str] = []

DEFAULT_DOCKERFILE_GEM_APK_PACKAGES = [
    "ruby",
    "ruby-dev",
    "ruby-bundler",
    "ruby-rdoc",
]

DEFAULT_DOCKERFILE_PIP_ARGS = [
    "# renovate: datasource=pypi depName=pip\nARG PIP_PIP_VERSION=25.2",
]

DEFAULT_DOCKERFILE_PIPENV_ARGS = [
    "# renovate: datasource=pypi depName=virtualenv\nARG PIP_VIRTUALENV_VERSION=20.33.0",
]

DEFAULT_DOCKERFILE_RUST_ARGS = [
    "# renovate: datasource=github-tags depName=rust-lang/rust\nARG RUST_RUST_VERSION=1.88.0",
]

DEFAULT_DOCKERFILE_FLAVOR_ARGS = [
    "# renovate: datasource=crate depName=sarif-fmt\nARG CARGO_SARIF_FMT_VERSION=0.8.0",
]

DEFAULT_DOCKERFILE_FLAVOR_CARGO_PACKAGES = [
    "sarif-fmt@${CARGO_SARIF_FMT_VERSION}",
]

OX_MARKDOWN_LINK = (
    "[![MegaLinter is graciously provided by OX Security]"
    + "(https://raw.githubusercontent.com/oxsecurity/megalinter/main/"
    + "docs/assets/images/ox-banner.png)]"
    + "(https://www.ox.security/?ref=megalinter)"
)
