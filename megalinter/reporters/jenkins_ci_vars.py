import logging
import re
import urllib.parse

from megalinter import config

PLATFORM_KEYWORDS = {
    "github": "github",
    "gitlab": "gitlab",
    "dev.azure.com": "azure",
    "visualstudio.com": "azure",
    "bitbucket": "bitbucket",
}


def apply_jenkins_ci_vars(request_id):
    if (
        config.get(request_id, "JENKINS_URL") is None
        and config.get(request_id, "JENKINS_HOME") is None
    ):
        return

    git_url = config.get(request_id, "GIT_URL", "")
    if git_url == "":
        logging.debug(
            "[Jenkins CI Vars] GIT_URL not found, cannot map Jenkins env vars"
        )
        return

    platform = _detect_platform(request_id, git_url)
    if platform is None:
        logging.warning(
            "[Jenkins CI Vars] Could not detect repository platform from GIT_URL. "
            "Set JENKINS_REPO_PLATFORM to github, gitlab, azure, or bitbucket "
            "to enable comment reporters."
        )
        return

    parsed = _parse_git_url(git_url)
    if parsed is None:
        logging.warning(f"[Jenkins CI Vars] Could not parse GIT_URL: {git_url}")
        return

    mappers = {
        "github": _map_github_vars,
        "gitlab": _map_gitlab_vars,
        "azure": _map_azure_vars,
        "bitbucket": _map_bitbucket_vars,
    }
    mappers[platform](request_id, parsed)
    logging.info(
        f"[Jenkins CI Vars] Mapped Jenkins env vars for {platform} comment reporting"
    )


def _detect_platform(request_id, git_url):
    explicit = config.get(request_id, "JENKINS_REPO_PLATFORM", "")
    if explicit != "":
        platform = explicit.lower().strip()
        if platform in ("github", "gitlab", "azure", "bitbucket"):
            return platform
        logging.warning(
            f"[Jenkins CI Vars] Unknown JENKINS_REPO_PLATFORM value: {explicit}. "
            "Expected: github, gitlab, azure, or bitbucket."
        )
        return None

    hostname = _extract_hostname(git_url).lower()

    for keyword, platform in PLATFORM_KEYWORDS.items():
        if keyword in hostname:
            return platform

    # Also check CHANGE_URL as a fallback signal
    change_url = config.get(request_id, "CHANGE_URL", "")
    if change_url != "":
        change_hostname = _extract_hostname(change_url).lower()
        for keyword, platform in PLATFORM_KEYWORDS.items():
            if keyword in change_hostname:
                return platform

    return None


def _extract_hostname(url):
    # Handle SSH URLs: git@hostname:path
    ssh_match = re.match(r"^[\w.-]+@([\w.-]+):", url)
    if ssh_match:
        return ssh_match.group(1)

    # Handle HTTPS URLs
    parsed = urllib.parse.urlparse(url)
    if parsed.hostname:
        return parsed.hostname

    return ""


def _parse_git_url(git_url):
    # Handle SSH URLs: git@hostname:owner/repo.git
    ssh_match = re.match(r"^[\w.-]+@([\w.-]+):(.+?)(?:\.git)?$", git_url)
    if ssh_match:
        hostname = ssh_match.group(1)
        path = ssh_match.group(2)
        path_parts = [p for p in path.split("/") if p]
        return {
            "scheme": "https",
            "hostname": hostname,
            "path": path,
            "path_parts": path_parts,
            "raw_url": git_url,
        }

    # Handle HTTPS URLs
    parsed = urllib.parse.urlparse(git_url)
    if not parsed.hostname:
        return None

    # Strip .git suffix and leading/trailing slashes from path
    path = parsed.path.strip("/")
    if path.endswith(".git"):
        path = path[:-4]
    path_parts = [p for p in path.split("/") if p]

    return {
        "scheme": parsed.scheme or "https",
        "hostname": parsed.hostname,
        "path": path,
        "path_parts": path_parts,
        "raw_url": git_url,
    }


def _safe_set(request_id, var_name, value):
    if value is None or value == "":
        return
    if not config.exists(request_id, var_name):
        config.set_value(request_id, var_name, value)
        logging.debug(f"[Jenkins CI Vars] Set {var_name} = {value}")


def _map_github_vars(request_id, parsed):
    # GITHUB_REPOSITORY = owner/repo
    if len(parsed["path_parts"]) >= 2:
        owner_repo = "/".join(parsed["path_parts"][:2])
        _safe_set(request_id, "GITHUB_REPOSITORY", owner_repo)

    # GITHUB_SHA from GIT_COMMIT
    git_commit = config.get(request_id, "GIT_COMMIT", "")
    if git_commit:
        _safe_set(request_id, "GITHUB_SHA", git_commit)

    # GITHUB_SERVER_URL
    server_url = f"{parsed['scheme']}://{parsed['hostname']}"
    _safe_set(request_id, "GITHUB_SERVER_URL", server_url)

    # GITHUB_API_URL: api.github.com for public, {server}/api/v3 for GHE
    if parsed["hostname"].lower() == "github.com":
        _safe_set(request_id, "GITHUB_API_URL", "https://api.github.com")
    else:
        _safe_set(request_id, "GITHUB_API_URL", f"{server_url}/api/v3")

    # GITHUB_REF from CHANGE_ID (PR number)
    change_id = config.get(request_id, "CHANGE_ID", "")
    if change_id:
        _safe_set(request_id, "GITHUB_REF", f"refs/pull/{change_id}/merge")


def _map_gitlab_vars(request_id, parsed):
    # CI_SERVER_URL
    server_url = f"{parsed['scheme']}://{parsed['hostname']}"
    _safe_set(request_id, "CI_SERVER_URL", server_url)

    # CI_PROJECT_NAME = last path segment
    if parsed["path_parts"]:
        _safe_set(request_id, "CI_PROJECT_NAME", parsed["path_parts"][-1])

    # CI_PROJECT_ID = full namespace/project path (GitLab API accepts path strings)
    if len(parsed["path_parts"]) >= 2:
        project_path = "/".join(parsed["path_parts"])
        _safe_set(request_id, "CI_PROJECT_ID", project_path)

    # CI_MERGE_REQUEST_IID from CHANGE_ID
    change_id = config.get(request_id, "CHANGE_ID", "")
    if change_id:
        _safe_set(request_id, "CI_MERGE_REQUEST_IID", change_id)

    # CI_JOB_URL from BUILD_URL
    build_url = config.get(request_id, "BUILD_URL", "")
    if build_url:
        _safe_set(request_id, "CI_JOB_URL", build_url)


def _map_azure_vars(request_id, parsed):
    hostname = parsed["hostname"].lower()
    path_parts = parsed["path_parts"]

    org = None
    project = None
    repo = None

    # Format 1: https://dev.azure.com/{org}/{project}/_git/{repo}
    if "dev.azure.com" in hostname:
        if len(path_parts) >= 4 and "_git" in path_parts:
            git_idx = path_parts.index("_git")
            org = path_parts[0]
            project = path_parts[git_idx - 1]
            repo = path_parts[git_idx + 1] if git_idx + 1 < len(path_parts) else None

    # Format 2: https://{org}.visualstudio.com/{project}/_git/{repo}
    elif "visualstudio.com" in hostname:
        org = hostname.split(".")[0]
        if len(path_parts) >= 3 and "_git" in path_parts:
            git_idx = path_parts.index("_git")
            project = path_parts[0]
            repo = path_parts[git_idx + 1] if git_idx + 1 < len(path_parts) else None

    if org is None:
        logging.warning(
            f"[Jenkins CI Vars] Could not parse Azure DevOps URL: {parsed['raw_url']}"
        )
        return

    # SYSTEM_COLLECTIONURI (with trailing slash, as Azure provides it)
    _safe_set(request_id, "SYSTEM_COLLECTIONURI", f"https://dev.azure.com/{org}/")

    if project:
        _safe_set(request_id, "SYSTEM_TEAMPROJECT", project)

    if repo:
        _safe_set(request_id, "BUILD_REPOSITORY_ID", repo)

    # SYSTEM_PULLREQUEST_PULLREQUESTID from CHANGE_ID
    change_id = config.get(request_id, "CHANGE_ID", "")
    if change_id:
        _safe_set(request_id, "SYSTEM_PULLREQUEST_PULLREQUESTID", change_id)

    # BUILD_BUILDID from Jenkins BUILD_ID
    build_id = config.get(request_id, "BUILD_ID", "")
    if build_id:
        _safe_set(request_id, "BUILD_BUILDID", build_id)


def _map_bitbucket_vars(request_id, parsed):
    # BITBUCKET_REPO_FULL_NAME = workspace/repo
    if len(parsed["path_parts"]) >= 2:
        full_name = "/".join(parsed["path_parts"][:2])
        _safe_set(request_id, "BITBUCKET_REPO_FULL_NAME", full_name)

    # BITBUCKET_PR_ID from CHANGE_ID
    change_id = config.get(request_id, "CHANGE_ID", "")
    if change_id:
        _safe_set(request_id, "BITBUCKET_PR_ID", change_id)

    # BITBUCKET_GIT_HTTP_ORIGIN - always construct as HTTPS URL
    http_origin = f"{parsed['scheme']}://{parsed['hostname']}/{parsed['path']}"
    _safe_set(request_id, "BITBUCKET_GIT_HTTP_ORIGIN", http_origin)

    # BITBUCKET_BUILD_NUMBER from Jenkins BUILD_NUMBER
    build_number = config.get(
        request_id,
        "BUILD_NUMBER",
        config.get(request_id, "BUILD_ID", ""),
    )
    if build_number:
        _safe_set(request_id, "BITBUCKET_BUILD_NUMBER", build_number)

    # BITBUCKET_STEP_UUID - placeholder from Jenkins BUILD_TAG or BUILD_URL
    step_uuid = config.get(
        request_id,
        "BUILD_TAG",
        config.get(request_id, "BUILD_URL", ""),
    )
    if step_uuid:
        _safe_set(request_id, "BITBUCKET_STEP_UUID", step_uuid)
