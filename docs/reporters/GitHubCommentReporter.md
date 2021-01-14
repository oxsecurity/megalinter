<!-- markdownlint-disable MD013 MD033 MD041 -->
# GitHub Comment Reporter

Posts Mega-Linter results summary in the comments of the related pull request (if existing)

## Usage

Click on hyperlinks to access detailed logs

![Screenshot](../assets/images/GitHubCommentReporter.jpg)

## Configuration

| Variable                | Description                                                                               | Default value            |
|-------------------------|-------------------------------------------------------------------------------------------|--------------------------|
| GITHUB_COMMENT_REPORTER | Activates/deactivates reporter                                                            | true                     |
| GITHUB_API_URL          | URL where the github API can be reached<br/>Must be overridden if using GitHub Enterprise | `https://api.github.com` |
| GITHUB_SERVER_URL       | URL of the GitHub instance<br/>Must be overridden if using GitHub Enterprise              | `https://github.com`     |
