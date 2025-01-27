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
DEFAULT_RELEASE = "v8"

DEFAULT_DOCKERFILE_ARGS = [
    "# renovate: datasource=repology depName=alpine_3_21/bash\nARG APK_BASH_VERSION=5.2.37-r0",
    "# renovate: datasource=repology depName=alpine_3_21/ca-certificates\nARG APK_CA_CERTIFICATES_VERSION=20241121-r1",
    "# renovate: datasource=repology depName=alpine_3_21/curl\nARG APK_CURL_VERSION=8.11.1-r0",
    "# renovate: datasource=repology depName=alpine_3_21/gcc\nARG APK_GCC_VERSION=14.2.0-r4",
    "# renovate: datasource=repology depName=alpine_3_21/git\nARG APK_GIT_VERSION=2.47.2-r0",
    "# renovate: datasource=repology depName=alpine_3_21/git-lfs\nARG APK_GIT_LFS_VERSION=3.6.0-r0",
    "# renovate: datasource=repology depName=alpine_3_21/libffi-dev\nARG APK_LIBFFI_DEV_VERSION=3.4.6-r0",
    "# renovate: datasource=repology depName=alpine_3_21/make\nARG APK_MAKE_VERSION=4.4.1-r2",
    "# renovate: datasource=repology depName=alpine_3_21/musl-dev\nARG APK_MUSL_DEV_VERSION=1.2.5-r8",
    "# renovate: datasource=repology depName=alpine_3_21/openssh\nARG APK_OPENSSH_VERSION=9.9_p1-r2",
]

DEFAULT_DOCKERFILE_APK_PACKAGES = [
    "bash=${APK_BASH_VERSION}",
    "ca-certificates=${APK_CA_CERTIFICATES_VERSION}",
    "curl=${APK_CURL_VERSION}",
    "gcc=${APK_GCC_VERSION}",
    "git=${APK_GIT_VERSION}",
    "git-lfs=${APK_GIT_LFS_VERSION}",
    "libffi-dev=${APK_LIBFFI_DEV_VERSION}",
    "make=${APK_MAKE_VERSION}",
    "musl-dev=${APK_MUSL_DEV_VERSION}",
    "openssh=${APK_OPENSSH_VERSION}",
]

DEFAULT_DOCKERFILE_DOCKER_ARGS = [
    "# renovate: datasource=repology depName=alpine_3_21/docker\nARG APK_DOCKER_VERSION=27.3.1-r0",
    "# renovate: datasource=repology depName=alpine_3_21/openrc\nARG APK_OPENRC_VERSION=0.55.1-r2",
]

DEFAULT_DOCKERFILE_DOCKER_APK_PACKAGES = [
    "docker=${APK_DOCKER_VERSION}",
    "openrc=${APK_OPENRC_VERSION}"
]

DEFAULT_DOCKERFILE_NPM_ARGS = [
    "# renovate: datasource=repology depName=alpine_3_21/npm\nARG APK_NPM_VERSION=10.9.1-r0",
    "# renovate: datasource=repology depName=alpine_3_21/nodejs-current\nARG APK_NODEJS_CURRENT_VERSION=23.2.0-r1",
    "# renovate: datasource=repology depName=alpine_3_21/yarn\nARG APK_YARN_VERSION=1.22.22-r1",
]

DEFAULT_DOCKERFILE_NPM_APK_PACKAGES = [
    "npm=${APK_NPM_VERSION}",
    "nodejs-current=${APK_NODEJS_CURRENT_VERSION}",
    "yarn=${APK_YARN_VERSION}"
]

DEFAULT_DOCKERFILE_GEM_ARGS = [
    "# renovate: datasource=repology depName=alpine_3_21/ruby\nARG APK_RUBY_VERSION=3.3.6-r0",
    "# renovate: datasource=repology depName=alpine_3_21/ruby-dev\nARG APK_RUBY_DEV_VERSION=3.3.6-r0",
    "# renovate: datasource=repology depName=alpine_3_21/ruby-bundler\nARG APK_RUBY_BUNDLER_VERSION=2.5.23-r0",
    "# renovate: datasource=repology depName=alpine_3_21/ruby-rdoc\nARG APK_RUBY_RDOC_VERSION=3.3.6-r0",
]

DEFAULT_DOCKERFILE_GEM_APK_PACKAGES = [
    "ruby=${APK_RUBY_VERSION}",
    "ruby-dev=${APK_RUBY_DEV_VERSION}",
    "ruby-bundler=${APK_RUBY_BUNDLER_VERSION}",
    "ruby-rdoc=${APK_RUBY_RDOC_VERSION}"
]

DEFAULT_DOCKERFILE_PIP_ARGS = [
    "# renovate: datasource=pypi depName=pip\nARG PIP_PIP_VERSION=25.0",
]

DEFAULT_DOCKERFILE_PIPENV_ARGS = [
    "# renovate: datasource=pypi depName=virtualenv\nARG PIP_VIRTUALENV_VERSION=20.29.1",
]

DEFAULT_DOCKERFILE_FLAVOR_ARGS = [
    "# renovate: datasource=crate depName=sarif-fmt\nARG CARGO_SARIF_FMT_VERSION=0.7.0",
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
