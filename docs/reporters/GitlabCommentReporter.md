---
title: Gitlab Merge Request Comments Reporter for MegaLinter
description: Posts MegaLinter SAST results summary in the comments of the related Gitlab Merge Request (if existing)
---
<!-- markdownlint-disable MD013 MD033 MD041 -->
# Gitlab Comment Reporter

Posts MegaLinter results summary in the comments of the related Gitlab merge request (if existing)

## Usage

Click on hyperlinks to access detailed logs (click on **Download** in **Artifacts section** at the left of a CI job page)

![Screenshot](../assets/images/GitlabCommentReporter.jpg)

After a first MegaLinter run, a comment is posted on the MR. To avoid multiplicating MegaLinter MR comments, future MegaLinter runs will update the existing MR comment instead of posting a new one.

If you really want a new MR comment for each MegaLinter run, define variable `GITLAB_COMMENT_REPORTER_OVERWRITE_COMMENT` to `false`.

## Configuration

- Create an [access token](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html#create-a-personal-access-token) with scope **api**
- Paste the access token in a [masked CI/CD variable](https://docs.gitlab.com/ee/ci/variables/#add-a-cicd-variable-to-a-project) named **GITLAB_ACCESS_TOKEN_MEGALINTER** in your project (repository)

![config-gitlab-access-token](https://user-images.githubusercontent.com/17500430/151674446-1bcb1420-d9aa-4ae1-aaae-dcf51afb36ab.gif)

| Variable                                  | Description                                                                                            | Default value |
|-------------------------------------------|--------------------------------------------------------------------------------------------------------|---------------|
| GITLAB_COMMENT_REPORTER                   | Activates/deactivates reporter                                                                         | `true`        |
| GITLAB_ACCESS_TOKEN_MEGALINTER            | Must contain a Gitlab private access token defined with api access                                     | <!-- -->      |
| GITLAB_COMMENT_REPORTER_OVERWRITE_COMMENT | Set to false to not overwrite existing comments in case of new runs on the same Merge Request          | `true`        |
| GITLAB_CUSTOM_CERTIFICATE                 | SSL certificate value to connect to Gitlab                                                             | <!-- -->      |
| GITLAB_CERTIFICATE_PATH                   | Path to SSL certificate to connect to Gitlab (if SSL cert has been manually defined with PRE_COMMANDS) | <!-- -->      |
| REPORTERS_MARKDOWN_TYPE                   | Set to `simple` to avoid external images in generated markdown                                         | `advanced`    |

## Special Thanks

- Special thanks to [John Berkers](https://github.com/jberkers42) for his assistance in making Gitlab reporter work with self-hosted gitlab instances secured by certificates :)