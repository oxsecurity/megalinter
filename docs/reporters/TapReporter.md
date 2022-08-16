# TAP Reporter

Posts a pack of TAP logs , zipped as a GitHub Action artifact

- A separate TAP file for each processed linter

**Warning**: When TAP_REPORTER is `true`:

- Performances: all linters with CLI lint mode `list_of_files` are switched to `file` mode, so linter is called ont time per file to analyze
- Scope: all linters with CLI lint mode `project` are deactivated

For those reasons... why not having a look at [SARIF reporter](https://oxsecurity.github.io/megalinter/latest/reporters/SarifReporter/), that does not have those issues ?

## Usage

Access GitHub action run

![Screenshot](../assets/images/AccessActionRun.jpg)

Click on Artifacts then click on **MegaLinter reports**

![Screenshot](../assets/images/TextReporter_1.jpg)

Open the downloaded zip file and browse linters TAP reports

### Other CI tools

If you are not using GitHub Actions, you can export `mega-linter.log` and folder `<WORKSPACE>/megalinter-reports`

## Configuration

| Variable                   | Description                                                                                 | Default value |
|----------------------------|---------------------------------------------------------------------------------------------|---------------|
| TAP_REPORTER               | Activates/deactivates reporter                                                              | `false`       |
| TAP_REPORTER_OUTPUT_DETAIL | If `detailed`, all files will be in TAP output, else only files with issues will be present | `simple`      |
| TAP_REPORTER_SUB_FOLDER    | Sub-folder of reports folder containing tap logs                                            | `tap`         |
