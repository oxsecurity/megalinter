#!/usr/bin/env bash

PYTHONPATH=$PYTHONPATH:$(pwd)
export PYTHONPATH

if [ "${TEST_CASE_RUN}" == "true" ]; then
  # Run test cases with pytest
  echo "RUNNING TEST CASES"
  pytest -v --durations=0 --cov=megalinter --cov-report=xml megalinter/
  PYTEST_STATUS=$?
  echo Pytest exited $PYTEST_STATUS
  # Manage return code
  if [ $PYTEST_STATUS -eq 0 ]; then
    echo "Successfully executed Pytest"
  else
    echo "Error(s) found by Pytest"
    exit 1
  fi
  # Upload to codecov.io
  bash <(curl -s https://codecov.io/bash)

else
  # Normal run
  LOG_LEVEL="${LOG_LEVEL:-INFO}"        # Default log level (VERBOSE, DEBUG, TRACE)
  if [[ ${LOG_LEVEL} == "DEBUG" ]]; then
        printenv
  fi
  python -m megalinter.run
fi
