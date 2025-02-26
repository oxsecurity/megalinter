---
title: Console Reporter for MegaLinter
description: Posts MegaLinter SAST results execution logs in the terminal console
---
# Console Reporter

Posts MegaLinter results execution logs in the console

## Usage

Open GitHub action (or other CI tool) logs and look in MegaLinter step

![Screenshot](../assets/images/ConsoleReporter.jpg)

## Configuration

| Variable                  | Description                                             | Default value |
|---------------------------|---------------------------------------------------------|---------------|
| CONSOLE_REPORTER          | Activates/deactivates reporter                          | true          |
| CONSOLE_REPORTER_SECTIONS | Activates/deactivates sections for console logs         | true          |
| OUTPUT_DETAIL             | `simple` for only error files, `detailed` for all files | `simple`      |