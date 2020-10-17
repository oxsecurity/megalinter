# Mega-Linter Library

## Main script

The file `linter.sh` is the main script that is called for the process and loads all other scripts as functions.

## Functions

The additional files in the folder are functions to help streamline the main build process and allow for easier maintenance.

- `possum.sh`
  - Official mascot of the **Mega-Linter**
- `buildFileList.sh`
  - Functions to help find files that were modified, or need to be scanned
- `validation.sh`
  - Logic to see what linters are enabled
- `worker.sh`
  - Calls to the various linters and the test cases for each
