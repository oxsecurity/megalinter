---
title: Azure Pipelines Reporter for MegaLinter
description: Posts MegaLinter SAST results summary in the comments of the related Azure Pipelines pull request (if existing)
---
<!-- markdownlint-disable MD013 MD033 MD041 -->
# Azure Comment Reporter

Posts Mega-Linter results summary in the comments of the related Azure Pipelines pull request (if existing)

## Usage

Click on **MegaLinter-reports** artifact from the main job log to view or download results.

If [LLM Advisor](../llm-advisor.md) is activated, it will also show its suggestions to fix linter errors.

![Screenshot](../assets/images/AzureCommentReporter.jpg)

## Configuration

- The following variables must be sent to the docker run command

Example:

<!-- # MAJOR-RELEASE-IMPACTED -->

```yaml
      - script: |
          docker run -v $(System.DefaultWorkingDirectory):/tmp/lint \
            --env-file <(env | grep -e SYSTEM_ -e BUILD_ -e TF_ -e AGENT_) \
            -e SYSTEM_ACCESSTOKEN=$(System.AccessToken) \
            -e SYSTEM_COLLECTIONURI=$(System.CollectionUri) \
            -e SYSTEM_PULLREQUEST_PULLREQUESTID=$(System.PullRequest.PullRequestId) \
            -e SYSTEM_PULLREQUEST_SOURCEREPOSITORYURI=$(System.PullRequest.SourceRepositoryURI) \
            -e SYSTEM_TEAMPROJECT="$(System.TeamProject)" \
            -e BUILD_BUILD_ID=$(Build.BuildId) \
            -e BUILD_REPOSITORY_ID=$(Build.Repository.ID) \
            -e GIT_AUTHORIZATION_BEARER=$(System.AccessToken) \
            oxsecurity/megalinter:v9
        displayName: Run MegaLinter
```

- A build policy must be defined

  - See <https://docs.microsoft.com/en-US/azure/devops/repos/git/branch-policies?view=azure-devops&tabs=browser#build-validation>

- You must allow **Contribute** and **Contribute to Pull Requests** on your Build Service (Settings -> Repositories -> Select your build service)

![Screenshot](../assets/images/AzureReporterConfigContribute.jpg)

| Variable                                   | Description                                                                                             | Default value    |
|--------------------------------------------|---------------------------------------------------------------------------------------------------------|------------------|
| AZURE_COMMENT_REPORTER                     | Activates/deactivates reporter                                                                          | `true`           |
| AZURE_COMMENT_REPORTER_LINKS_TYPE          | Set to `build` if you want comments linking to target Build and not artifacts page                      | `artifacts`      |
| AZURE_COMMENT_REPORTER_REPLACE_WITH_SPACES | Do not replaces %20 by spaces in repo name if set to false                                              | `true`           |
| REPORTERS_MARKDOWN_TYPE                    | Set to `simple` to avoid external images in generated markdown                                          | `advanced`       |
| REPORTERS_MARKDOWN_SUMMARY_TYPE            | Display summary in PR/MR comments as `sections`, `table` or both (`sections-table` or `table-sections`) | `table-sections` |
| REPORTERS_ACTION_RUN_URL                   | Override default URL of the CI job visualization page                                                   | <!-- -->         |
| JOB_SUMMARY_ADDITIONAL_MARKDOWN            | Custom markdown to add at the end of the summary message                                                | <!-- -->         |
| MEGALINTER_MULTIRUN_KEY                    | Key to identify multirun when multiple MegaLinter runs are executed in the same pipeline (ex: `java`)   | <!-- -->         |
