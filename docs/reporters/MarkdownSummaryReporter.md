---
title: Summary Reporter for MegaLinter
description: Generates a summary of SAST results in Markdown within a file named 'megalinter-report.md', located in the report folder.
---

# Summary Reporter

Generates a summary of SAST results in Markdown within a file named **megalinter-report.md**, located in the report folder.

This reporter **is deactivated by default**.

![Screenshot](../assets/images/MarkdownSummaryReporter_1.png)

![Screenshot](../assets/images/MarkdownSummaryReporter_2.png)

## Usage

Activate the reporter (`MARKDOWN_SUMMARY_REPORTER: true`) to generate summary report file.

## Configuration

| Variable                                | Description                                                                                                       | Default value              |
|-----------------------------------------|-------------------------------------------------------------------------------------------------------------------|----------------------------|
| MARKDOWN_SUMMARY_REPORTER                          | Activates/deactivates reporter                                                                                    | `false`                    |
| MARKDOWN_SUMMARY_REPORTER_FILE_NAME                | File name for SUMMARY report output file                                                                            | `megalinter-report.md` |
