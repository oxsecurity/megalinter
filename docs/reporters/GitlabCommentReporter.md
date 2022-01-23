<!-- markdownlint-disable MD013 MD033 MD041 -->
# Gitlab Comment Reporter

Posts Mega-Linter results summary in the comments of the related merge request (if existing)

## Usage

Click on hyperlinks to access detailed logs

![Screenshot](../assets/images/GitlabCommentReporter.jpg)

## Configuration

- Create an [access token](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html#create-a-personal-access-token) with scope **api**
- Paste the access token in a [masked CI/CD variable](https://docs.gitlab.com/ee/ci/variables/#add-a-cicd-variable-to-a-project) named **GITLAB_ACCESS_TOKEN_MEGALINTER** in your project (repository)

| Variable                | Description                                                                               | Default value            |
|-------------------------|-------------------------------------------------------------------------------------------|--------------------------|
| GITLAB_COMMENT_REPORTER | Activates/deactivates reporter                                                            | true                     |
| GITLAB_API_URL          | URL where the github API can be reached<br/>May be overridden if using self-hosted Gitlab | `https://api.gitlab.com` |
| GITLAB_SERVER_URL       | URL of the Gitlab instance<br/>May be overridden if using self-hosted Gitlab              | `https://gitlab.com`     |
| GITLAB_ACCESS_TOKEN_MEGALINTER     | Must contain a Gitlab private access token defined with api access                        | <!-- -->                 |
