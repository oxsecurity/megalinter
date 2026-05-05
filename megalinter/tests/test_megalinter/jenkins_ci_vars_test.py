import unittest
from uuid import uuid1

from megalinter import config
from megalinter.reporters.jenkins_ci_vars import apply_jenkins_ci_vars


class JenkinsCiVarsTest(unittest.TestCase):
    def setUp(self):
        self.request_id = str(uuid1())
        config.init_config(self.request_id, None, {})

    def tearDown(self):
        config.delete(self.request_id)

    def _set(self, var, value):
        config.set_value(self.request_id, var, value)

    def _get(self, var, default=None):
        return config.get(self.request_id, var, default)

    def _set_jenkins(self):
        self._set("JENKINS_URL", "http://jenkins.example.com:8080")

    # ---- No-op cases ----

    def test_no_jenkins_env(self):
        self._set("GIT_URL", "https://github.com/owner/repo.git")
        apply_jenkins_ci_vars(self.request_id)
        assert not config.exists(self.request_id, "GITHUB_REPOSITORY")

    def test_no_git_url(self):
        self._set_jenkins()
        apply_jenkins_ci_vars(self.request_id)
        assert not config.exists(self.request_id, "GITHUB_REPOSITORY")
        assert not config.exists(self.request_id, "CI_PROJECT_NAME")

    def test_unknown_platform(self):
        self._set_jenkins()
        self._set("GIT_URL", "https://git.mycompany.com/owner/repo.git")
        apply_jenkins_ci_vars(self.request_id)
        assert not config.exists(self.request_id, "GITHUB_REPOSITORY")
        assert not config.exists(self.request_id, "CI_PROJECT_NAME")

    # ---- GitHub ----

    def test_github_https(self):
        self._set_jenkins()
        self._set("GIT_URL", "https://github.com/owner/repo.git")
        self._set("GIT_COMMIT", "abc123def456")
        self._set("CHANGE_ID", "42")
        apply_jenkins_ci_vars(self.request_id)
        assert self._get("GITHUB_REPOSITORY") == "owner/repo"
        assert self._get("GITHUB_SHA") == "abc123def456"
        assert self._get("GITHUB_SERVER_URL") == "https://github.com"
        assert self._get("GITHUB_API_URL") == "https://api.github.com"
        assert self._get("GITHUB_REF") == "refs/pull/42/merge"

    def test_github_ssh(self):
        self._set_jenkins()
        self._set("GIT_URL", "git@github.com:owner/repo.git")
        self._set("CHANGE_ID", "7")
        apply_jenkins_ci_vars(self.request_id)
        assert self._get("GITHUB_REPOSITORY") == "owner/repo"
        assert self._get("GITHUB_SERVER_URL") == "https://github.com"
        assert self._get("GITHUB_API_URL") == "https://api.github.com"
        assert self._get("GITHUB_REF") == "refs/pull/7/merge"

    def test_github_enterprise(self):
        self._set_jenkins()
        self._set("GIT_URL", "https://github.mycompany.com/team/project.git")
        self._set("GIT_COMMIT", "sha256")
        apply_jenkins_ci_vars(self.request_id)
        assert self._get("GITHUB_REPOSITORY") == "team/project"
        assert self._get("GITHUB_SERVER_URL") == "https://github.mycompany.com"
        assert (
            self._get("GITHUB_API_URL") == "https://github.mycompany.com/api/v3"
        )

    def test_github_no_change_id(self):
        self._set_jenkins()
        self._set("GIT_URL", "https://github.com/owner/repo.git")
        apply_jenkins_ci_vars(self.request_id)
        assert self._get("GITHUB_REPOSITORY") == "owner/repo"
        assert not config.exists(self.request_id, "GITHUB_REF")

    def test_github_no_overwrite(self):
        self._set_jenkins()
        self._set("GIT_URL", "https://github.com/owner/repo.git")
        self._set("GITHUB_REPOSITORY", "already/set")
        apply_jenkins_ci_vars(self.request_id)
        assert self._get("GITHUB_REPOSITORY") == "already/set"

    # ---- GitLab ----

    def test_gitlab_https(self):
        self._set_jenkins()
        self._set("GIT_URL", "https://gitlab.com/group/project.git")
        self._set("CHANGE_ID", "15")
        self._set("BUILD_URL", "http://jenkins:8080/job/test/1/")
        apply_jenkins_ci_vars(self.request_id)
        assert self._get("CI_SERVER_URL") == "https://gitlab.com"
        assert self._get("CI_PROJECT_NAME") == "project"
        assert self._get("CI_PROJECT_ID") == "group/project"
        assert self._get("CI_MERGE_REQUEST_IID") == "15"
        assert self._get("CI_JOB_URL") == "http://jenkins:8080/job/test/1/"

    def test_gitlab_subgroups(self):
        self._set_jenkins()
        self._set("GIT_URL", "https://gitlab.com/group/sub/project.git")
        apply_jenkins_ci_vars(self.request_id)
        assert self._get("CI_PROJECT_NAME") == "project"
        assert self._get("CI_PROJECT_ID") == "group/sub/project"

    def test_gitlab_self_hosted(self):
        self._set_jenkins()
        self._set("GIT_URL", "https://gitlab.hardis.com/team/repo.git")
        apply_jenkins_ci_vars(self.request_id)
        assert self._get("CI_SERVER_URL") == "https://gitlab.hardis.com"
        assert self._get("CI_PROJECT_NAME") == "repo"

    # ---- Azure DevOps ----

    def test_azure_dev_azure_com(self):
        self._set_jenkins()
        self._set(
            "GIT_URL", "https://dev.azure.com/myorg/myproject/_git/myrepo"
        )
        self._set("CHANGE_ID", "99")
        self._set("BUILD_ID", "5678")
        apply_jenkins_ci_vars(self.request_id)
        assert self._get("SYSTEM_COLLECTIONURI") == "https://dev.azure.com/myorg/"
        assert self._get("SYSTEM_TEAMPROJECT") == "myproject"
        assert self._get("BUILD_REPOSITORY_ID") == "myrepo"
        assert self._get("SYSTEM_PULLREQUEST_PULLREQUESTID") == "99"
        assert self._get("BUILD_BUILDID") == "5678"

    def test_azure_visualstudio_com(self):
        self._set_jenkins()
        self._set(
            "GIT_URL",
            "https://myorg.visualstudio.com/myproject/_git/myrepo",
        )
        self._set("CHANGE_ID", "10")
        apply_jenkins_ci_vars(self.request_id)
        assert self._get("SYSTEM_COLLECTIONURI") == "https://dev.azure.com/myorg/"
        assert self._get("SYSTEM_TEAMPROJECT") == "myproject"
        assert self._get("BUILD_REPOSITORY_ID") == "myrepo"
        assert self._get("SYSTEM_PULLREQUEST_PULLREQUESTID") == "10"

    # ---- Bitbucket ----

    def test_bitbucket_https(self):
        self._set_jenkins()
        self._set("GIT_URL", "https://bitbucket.org/workspace/repo.git")
        self._set("CHANGE_ID", "55")
        self._set("BUILD_NUMBER", "101")
        self._set("BUILD_TAG", "jenkins-job-101")
        apply_jenkins_ci_vars(self.request_id)
        assert self._get("BITBUCKET_REPO_FULL_NAME") == "workspace/repo"
        assert self._get("BITBUCKET_PR_ID") == "55"
        assert (
            self._get("BITBUCKET_GIT_HTTP_ORIGIN")
            == "https://bitbucket.org/workspace/repo"
        )
        assert self._get("BITBUCKET_BUILD_NUMBER") == "101"
        assert self._get("BITBUCKET_STEP_UUID") == "jenkins-job-101"

    def test_bitbucket_ssh(self):
        self._set_jenkins()
        self._set("GIT_URL", "git@bitbucket.org:workspace/repo.git")
        self._set("CHANGE_ID", "12")
        self._set("BUILD_NUMBER", "50")
        self._set("BUILD_TAG", "jenkins-job-50")
        apply_jenkins_ci_vars(self.request_id)
        assert self._get("BITBUCKET_REPO_FULL_NAME") == "workspace/repo"
        assert self._get("BITBUCKET_PR_ID") == "12"
        assert (
            self._get("BITBUCKET_GIT_HTTP_ORIGIN")
            == "https://bitbucket.org/workspace/repo"
        )

    def test_bitbucket_self_hosted(self):
        self._set_jenkins()
        self._set(
            "GIT_URL", "https://bitbucket.mycompany.com/scm/proj/repo.git"
        )
        self._set("CHANGE_ID", "3")
        apply_jenkins_ci_vars(self.request_id)
        assert self._get("BITBUCKET_REPO_FULL_NAME") == "scm/proj"
        assert self._get("BITBUCKET_PR_ID") == "3"

    # ---- Activation variants ----

    def test_jenkins_home_only(self):
        self._set("JENKINS_HOME", "/var/lib/jenkins")
        self._set("GIT_URL", "https://github.com/owner/repo.git")
        self._set("CHANGE_ID", "1")
        apply_jenkins_ci_vars(self.request_id)
        assert self._get("GITHUB_REPOSITORY") == "owner/repo"
        assert self._get("GITHUB_REF") == "refs/pull/1/merge"

    # ---- Platform override ----

    def test_explicit_platform_override(self):
        self._set_jenkins()
        self._set("GIT_URL", "https://git.mycompany.com/team/repo.git")
        self._set("JENKINS_REPO_PLATFORM", "gitlab")
        self._set("CHANGE_ID", "8")
        apply_jenkins_ci_vars(self.request_id)
        assert self._get("CI_SERVER_URL") == "https://git.mycompany.com"
        assert self._get("CI_PROJECT_NAME") == "repo"
        assert self._get("CI_MERGE_REQUEST_IID") == "8"

    def test_change_url_fallback_detection(self):
        self._set_jenkins()
        self._set("GIT_URL", "https://git.mycompany.com/team/repo.git")
        self._set("CHANGE_URL", "https://github.com/team/repo/pull/5")
        self._set("CHANGE_ID", "5")
        apply_jenkins_ci_vars(self.request_id)
        assert self._get("GITHUB_REPOSITORY") == "team/repo"
