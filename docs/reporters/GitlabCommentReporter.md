<!-- markdownlint-disable MD013 MD033 MD041 -->
# Gitlab Comment Reporter

Posts Mega-Linter results summary in the comments of the related merge request (if existing)

## Usage

Click on hyperlinks to access detailed logs

![Screenshot](../assets/images/GitlabCommentReporter.jpg)

## Configuration

| Variable                | Description                                                                               | Default value            |
|-------------------------|-------------------------------------------------------------------------------------------|--------------------------|
| GITLAB_COMMENT_REPORTER | Activates/deactivates reporter                                                            | true                     |
| GITLAB_API_URL          | URL where the github API can be reached<br/>May be overridden if using self-hosted Gitlab | `https://api.gitlab.com` |
| GITLAB_SERVER_URL       | URL of the Gitlab instance<br/>May be overridden if using self-hosted Gitlab              | `https://gitlab.com`     |
