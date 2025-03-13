---
title: file.io Reporter for MegaLinter
description: If you don't use artifacts upload to read MegaLinter reports, you can access them with an hyperlink to file.io
---
# File.io Reporter

If you don't use artifacts upload to read MegaLinter reports, you can access them with an hyperlink to file.io

**important**: MegaLinter has no affiliation with file.io, but it's supposed to be secured, and only one download is available for a report (snapchat for files, basically)

This reporter **is deactivated by default**.

## Usage

Activate the reporter (`FILEIO_REPORTER: true`) to see link to reports zip on file.io

- Get the file.io hyperlink at the end of Mega-linter console output

![Screenshot](../assets/images/FileIOReporter_1.jpg)

- Download file on file.io: it's immediately deleted on the server so it can be downloaded only once

![Screenshot](../assets/images/FileIOReporter_2.jpg)

- Browse reports

![Screenshot](../assets/images/FileIOReporter_3.jpg)

## Configuration

| Variable                     | Description                                              | Default value |
|------------------------------|----------------------------------------------------------|---------------|
| FILEIO_REPORTER              | Activates/deactivates reporter                           | `false`       |
| FILEIO_REPORTER_SEND_SUCCESS | Skip sending report to file.io if the lint is in success | `false`       |
