ML_REPO_OWNER = "megalinter"
ML_REPO_NAME = "megalinter"
ML_REPO = f"{ML_REPO_OWNER}/{ML_REPO_NAME}"
ML_REPO_URL = f"https://github.com/{ML_REPO_OWNER}/{ML_REPO_NAME}"
ML_DOC_URL = "https://megalinter.github.io/v6-alpha"  # TODOv6: remove v6-alpha, replace by latest
ML_REPO_ISSUES_URL = f"https://github.com/{ML_REPO_OWNER}/{ML_REPO_NAME}/issues"
ML_DOC_URL_DESCRIPTORS_ROOT = f"{ML_DOC_URL}/descriptors"

ML_DOCKER_OWNER = "megalinter"
ML_DOCKER_NAME = "megalinter"
ML_DOCKER_IMAGE = f"{ML_DOCKER_OWNER}/{ML_DOCKER_NAME}"
ML_DOCKER_IMAGE_LEGACY = "nvuillam/mega-linter"

DEFAULT_DOCKER_WORKSPACE_DIR = "/tmp/lint"
DEFAULT_REPORT_FOLDER_NAME = "megalinter-reports"
DEFAULT_SARIF_REPORT_FILE_NAME = "megalinter-report.sarif"
DEFAULT_SARIF_SCHEMA_URI = "https://schemastore.azurewebsites.net/schemas/json/sarif-2.1.0-rtm.5.json"
DEFAULT_SARIF_VERSION = "2.1.0"
DEFAULT_RELEASE = "v6-alpha"  # TODOv6 : replace with v6
