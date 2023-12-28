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
ML_DOCKER_IMAGE = f"{ML_DOCKER_OWNER}/{ML_DOCKER_NAME}"
ML_DOCKER_IMAGE_LEGACY = "nvuillam/mega-linter"
ML_DOCKER_IMAGE_LEGACY_V5 = "megalinter/megalinter"

DEFAULT_DOCKER_WORKSPACE_DIR = "/tmp/lint"
DEFAULT_REPORT_FOLDER_NAME = "megalinter-reports"
DEFAULT_SARIF_REPORT_FILE_NAME = "megalinter-report.sarif"
DEFAULT_MARKDOWN_SUMMARY_REPORT_FILE_NAME = "megalinter-report.md"
DEFAULT_SARIF_SCHEMA_URI = "https://json.schemastore.org/sarif-2.1.0.json"
DEFAULT_SARIF_VERSION = "2.1.0"
DEFAULT_RELEASE = "v7"

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
