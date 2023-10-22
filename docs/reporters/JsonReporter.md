---
title: JSON Reporter for MegaLinter
description: Generates a full execution and SAST results log in JSON format within a file named mega-linter-report.json, located in report folder
---
# JSON Reporter

Generates a full execution log in JSON format within a file named **mega-linter-report.json** , located in report folder

This reporter **is deactivated by default**.

![Screenshot](../assets/images/JsonReporter.jpg)

## Usage

Activate the reporter (`JSON_REPORTER: true`) to generate JSON report file

## Configuration

| Variable                    | Description                           | Default value           |
|-----------------------------|---------------------------------------|-------------------------|
| JSON_REPORTER               | Activates/deactivates reporter        | false                   |
| JSON_REPORTER_OUTPUT_DETAIL | "simple" or "detailed"                | simple                  |
| JSON_REPORTER_FILE_NAME     | File name for JSON report output file | mega-linter-report.json |
