# Text Reporter

Posts a pack of text logs , zipped as a GitHub Action artifact

- General execution log `mega-linter.log` (same as [ConsoleReporter](ConsoleReporter.md) log)
- A separate log file for each processed linter

## Usage

Access GitHub action run

![Screenshot](../assets/images/AccessActionRun.jpg)

Click on Artifacts then click on **Mega-Linter reports**

![Screenshot](../assets/images/TextReporter_1.jpg)

Open the downloaded zip file and browse **linters_logs** folder for reports

![Screenshot](../assets/images/TextReporter_2.jpg)

![Screenshot](../assets/images/TextReporter_3.jpg)

![Screenshot](../assets/images/TextReporter_4.jpg)

### Other CI tools

If you are not using GitHub Actions, you can export `mega-linter.log` and folder `<WORKSPACE>/report`

## Configuration

| Variable | Description | Default value |
| ----------------- | -------------- | :--------------: |
| TEXT_REPORTER | Activates/deactivates reporter | true |
| TEXT_REPORTER_SUB_FOLDER | Sub-folder of reports folder containing text logs | text |
