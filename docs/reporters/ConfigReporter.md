---
title: Linters Configuration Files Reporter for MegaLinter
description: Generates a folder IDE-config located in report folder that contains configuration files used by MegaLinter so they can be reused locally
---
# IDE Configuration Reporter

Generates a folder **IDE-config** located in report folder.

It contains:

- All default MegaLinter configuration files used during the linting
- Updated `.vscode/extensions.json` containing VsCode extensions corresponding to the linters used during MegaLinter run
- Updated `.idea/externalDependencies.xml` containing IntelliJ extensions corresponding to the linters used during MegaLinter run

This reporter **activated by default**.

![Screenshot](../assets/images/ConfigReporter_1.jpg)

![Screenshot](../assets/images/ConfigReporter_2.jpg)

![Screenshot](../assets/images/ConfigReporter_3.jpg)

## Usage

- Copy the content of `report/IDE-config` at the root of your repository
  - _You can copy all IDE_Config folder, or select config files and IDE extensions recommendations that you are interested into_
- Restart your IDE



## Configuration

| Variable                   | Description                                                    | Default value |
|----------------------------|----------------------------------------------------------------|---------------|
| CONFIG_REPORTER            | Activates/deactivates reporter                                 | true          |
| CONFIG_REPORTER_SUB_FOLDER | Output folder for IDE configuration files within report folder | `IDE-config`  |
