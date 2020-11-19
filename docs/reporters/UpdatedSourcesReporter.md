# Updated Sources Reporter

Posts a pack of files containing only the sources fixed by linters
This folder can be unpacked to currently repository to apply automated fixes on the repository

## Usage

Access GitHub action run

![Screenshot](../assets/images/AccessActionRun.jpg)

Click on Artifacts then click on **Mega-Linter reports**

![Screenshot](../assets/images/TextReporter_1.jpg)

Open the downloaded zip file and copy the content of folder **updated_sources**

![Screenshot](../assets/images/UpdatedSourcesReporter_1.jpg)

![Screenshot](../assets/images/UpdatedSourcesReporter_2.jpg)

Paste the result in your repository

### Other CI tools

If you are not using GitHub Actions, you can export folder `<WORKSPACE>/report/updated_sources`

## Configuration

| Variable | Description | Default value |
| ----------------- | -------------- | :--------------: |
| UPDATED_SOURCES_REPORTER | Activates/deactivates reporter | true |
| UPDATED_SOURCES_REPORTER_DIR | Sub-folder of reports folder containing updated sources | updated_sources |
