<!-- markdownlint-disable MD013 MD033 MD041 -->
# Azure Comment Reporter

Posts Mega-Linter results summary in the comments of the related Azure Pipelines pull request (if existing)

## Usage

Click on **MegaLinter-reports** artifact from the main job log to view or download results.

![Screenshot](../assets/images/AzureCommentReporter.jpg)

## Configuration

- The following variables must be sent to docker run command

Example:

```yaml
      - script: |
          docker run -v $(System.DefaultWorkingDirectory):/tmp/lint \
            -e GIT_AUTHORIZATION_BEARER=$(System.AccessToken) \
            -e CI=true \
            -e TF_BUILD=true \
            -e SYSTEM_ACCESSTOKEN=$(System.AccessToken) \
            -e SYSTEM_COLLECTIONURI=$(System.CollectionUri) \
            -e SYSTEM_PULLREQUEST_PULLREQUESTID=$(System.PullRequest.PullRequestId) \
            -e SYSTEM_TEAMPROJECT=$(System.TeamProject) \
            -e BUILD_BUILD_ID=$(Build.BuildId) \
            -e BUILD_REPOSITORY_ID=$(Build.Repository.ID) \
            oxsecurity/megalinter:v6
        displayName: Run MegaLinter
```

- A build policy must be defined

  - See <https://docs.microsoft.com/en-US/azure/devops/repos/git/branch-policies?view=azure-devops&tabs=browser#build-validation>

- You must allow **Contribute** and **Contribute to Pull Requests** on your Build Service (Settings -> Repositories -> Select your build service)

![Screenshot](../assets/images/AzureReporterConfigContribute.jpg)

| Variable               | Description                    | Default value |
|------------------------|--------------------------------|---------------|
| AZURE_COMMENT_REPORTER | Activates/deactivates reporter | true          |
