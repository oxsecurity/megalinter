#!/usr/bin/env bash

PYTHONPATH=$PYTHONPATH:$(pwd)
export PYTHONPATH

# Manage debug mode
LOG_LEVEL="${LOG_LEVEL:-INFO}" # Default log level (VERBOSE, DEBUG, TRACE)

# Manage newest git versions (related to CVE https://github.blog/2022-04-12-git-security-vulnerability-announced/)
#
if [[ "${WORKSPACE_AS_SAFE_DIR}" != 'false' && "${DEFAULT_WORKSPACE}" && -d "${DEFAULT_WORKSPACE}" ]]; then
  echo "Setting git safe.directory DEFAULT_WORKSPACE: ${DEFAULT_WORKSPACE} ..."
  git config --global --add safe.directory "${DEFAULT_WORKSPACE}"
else
  echo "Skipped setting git safe.directory DEFAULT_WORKSPACE: ${DEFAULT_WORKSPACE} ..."
fi

if [ -z ${GITHUB_WORKSPACE+x} ]; then
  echo "Setting git safe.directory default: /github/workspace ..."
  git config --global --add safe.directory /github/workspace
else
  echo "Setting git safe.directory GITHUB_WORKSPACE: $GITHUB_WORKSPACE ..."
  git config --global --add safe.directory "$GITHUB_WORKSPACE"
fi

echo "Setting git safe.directory to /tmp/lint ..."
git config --global --add safe.directory /tmp/lint

# Called by Auto-update CI job
if [ "${UPGRADE_LINTERS_VERSION}" == "true" ]; then
  echo "[MegaLinter init] UPGRADING LINTER VERSION"
  pip install pytest-cov pytest-timeout
  # Run only get_linter_version test methods
  pytest -v --durations=0 -k _get_linter_version megalinter/
  # Run only get_linter_help test methods
  pytest -v --durations=0 -k _get_linter_help megalinter/
  # Reinstall mkdocs-material because of broken dependency
  pip3 install --upgrade "markdown==3.3.7" mike mkdocs-material "pymdown-extensions==9.11" "mkdocs-glightbox==0.3.2" mdx_truly_sane_lists jsonschema json-schema-for-humans giturlparse webpreview "github-dependents-info==0.10.0"
  cd /tmp/lint || exit 1
  chmod +x build.sh
  GITHUB_TOKEN="${GITHUB_TOKEN}" bash build.sh --doc --dependents --stats
  exit $?
fi

# Run test cases with pytest
if [ "${TEST_CASE_RUN}" == "true" ]; then
  echo "[MegaLinter init] RUNNING TEST CASES"
  pip install pytest-cov pytest-timeout pytest-xdist
  if [ -z "${TEST_KEYWORDS}" ]; then
    pytest -v --timeout=300 --durations=0 --cov=megalinter --cov-report=xml megalinter/
  else
    pytest -v --timeout=300 --durations=0 -k "${TEST_KEYWORDS}" megalinter/
  fi
  PYTEST_STATUS=$?
  echo Pytest exited $PYTEST_STATUS
  # Manage return code
  if [ $PYTEST_STATUS -eq 0 ]; then
    echo "Successfully executed Pytest"
  else
    echo "Error(s) found by Pytest"
    exit 1
  fi
  # Upload to codecov.io if all tests run
  if [ -z "${TEST_KEYWORDS}" ]; then
    bash <(curl -s https://codecov.io/bash)
    exit $?
  fi
  exit $?
fi

if [ "${MEGALINTER_SERVER}" == "true" ]; then
  # MegaLinter HTTP server run
  set -eu
  echo "[MegaLinter init] MEGALINTER SERVER"
  # Install python dependencies used by server to avoid to make bigger docker images
  pip install fastapi pygments "uvicorn[standard]"
  HOST="${HOST:-0.0.0.0}" # Default host
  PORT="${PORT:-8000}"    # Default port
  uvicorn megalinter.server:app --host "$HOST" --port "$PORT"
else
  if [ "${MEGALINTER_SSH}" == "true" ]; then
    # MegaLinter SSH server
    set -eu
    SSH_VOLUME_FOLDER=/root/docker_ssh
    if [ -d "$SSH_VOLUME_FOLDER" ]; then
      # SSH key copy from local volume
      echo "Docker ssh folder content:"
      ls "$SSH_VOLUME_FOLDER"
      mkdir ~/.ssh
      chmod 700 ~/.ssh
      touch ~/.ssh/authorized_keys
      chmod 600 ~/.ssh/authorized_keys
      cat $SSH_VOLUME_FOLDER/id_rsa.pub >>~/.ssh/authorized_keys
      chmod 644 /root/.ssh/authorized_keys
      mkdir -p /var/run/sshd
      ssh-keygen -A
      sed -i s/^#PasswordAuthentication\ yes/PasswordAuthentication\ no/ /etc/ssh/sshd_config
      sed -i s/^#PermitRootLogin\ prohibit-password/PermitRootLogin\ yes/ /etc/ssh/sshd_config
      sed -i s/^#PermitUserEnvironment\ no/PermitUserEnvironment\ yes/ /etc/ssh/sshd_config
      echo "root:root" | chpasswd
    fi
    # SSH startup
    echo "[MegaLinter init] SSH"
    export -p >/var/ml-env-vars # save all environment variables configured during Dockerfile creation
    /usr/sbin/sshd -D
  else
    # Normal  (run megalinter)
    echo "[MegaLinter init] ONE-SHOT RUN"
    python -m megalinter.run
  fi
fi
