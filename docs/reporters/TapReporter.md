# TAP Reporter

Posts a pack of TAP logs , zipped as a GitHub Action artifact

- A separate TAP file for each processed linter

## Usage

Access GitHub action run

![Screenshot](../assets/images/AccessActionRun.jpg)

Click on Artifacts then click on **Mega-Linter reports**

![Screenshot](../assets/images/TextReporter_1.jpg)

Open the downloaded zip file and browse linters TAP reports

### Other CI tools

If you are not using GitHub Actions, you can export `mega-linter.log` and folder `<WORKSPACE>/report`

## Configuration

| Variable                | Description                                      | Default value |
|-------------------------|--------------------------------------------------|---------------|
| TAP_REPORTER            | Activates/deactivates reporter                   | `true`        |
| TAP_REPORTER_SUB_FOLDER | Sub-folder of reports folder containing tap logs | `tap`         |
