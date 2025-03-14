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
  pip install pytest-cov pytest-timeout pytest-rerunfailures
  # Run only get_linter_version test methods
  pytest --reruns 3 --reruns-delay 1 -v --durations=0 -k _get_linter_version megalinter/
  # Run only get_linter_help test methods
  pytest --reruns 3 --reruns-delay 1 -v --durations=0 -k _get_linter_help megalinter/
  # Reinstall mkdocs-material because of broken dependency
  pip3 install --upgrade markdown mike mkdocs-material pymdown-extensions "mkdocs-glightbox==0.3.2" mdx_truly_sane_lists jsonschema json-schema-for-humans giturlparse webpreview github-dependents-info
  cd /tmp/lint || exit 1
  chmod +x build.sh
  GITHUB_TOKEN="${GITHUB_TOKEN}" bash build.sh --doc --dependents --stats
  exit $?
fi

# Run test cases with pytest
if [ "${TEST_CASE_RUN}" == "true" ]; then
  echo "[MegaLinter init] RUNNING TEST CASES"
  pip install pytest-cov codecov-cli pytest-timeout pytest-xdist pytest-rerunfailures
  if [ -z "${TEST_KEYWORDS}" ]; then
    pytest --reruns 3 --reruns-delay 10 -v --timeout=300 --durations=0 --cov=megalinter --cov-report=xml --numprocesses auto --dist loadscope megalinter/
  else
    pytest --reruns 3 --reruns-delay 10 -v --timeout=300 --durations=0 --numprocesses auto --dist loadscope -k "${TEST_KEYWORDS}" megalinter/
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
    codecov
    exit $?
  fi
  exit $?
fi

if [ "${MEGALINTER_SERVER}" == "true" ]; then
  # MegaLinter Server Worker, listens to redis queues using python RQ -> https://github.com/rq/rq
  set -eu
  echo "[MegaLinter init] MEGALINTER SERVER WORKER"
  # Install python dependencies used by server to avoid to make bigger docker images
  # pip install -r /server/requirements.txt <-- Now managed from Dockerfile-worker
  MEGALINTER_SERVER_REDIS_HOST="${MEGALINTER_SERVER_REDIS_HOST:-megalinter_server_redis}" # Default host
  MEGALINTER_SERVER_REDIS_PORT="${MEGALINTER_SERVER_REDIS_PORT:-6379}"                    # Default port
  MEGALINTER_SERVER_REDIS_QUEUE="${MEGALINTER_SERVER_REDIS_QUEUE:-megalinter:queue:requests}"
  if [ "${MEGALINTER_SERVER_WORKER_POOL}" == "true" ]; then
    # Use RQ worker pool (beta)
    MEGALINTER_SERVER_WORKER_POOL_NUMBER="${MEGALINTER_SERVER_WORKER_POOL_NUMBER:-10}" # Default number of worker threads
    echo "[MegaLinter Worker] Init Redis Queue Worker pool (${MEGALINTER_SERVER_WORKER_POOL_NUMBER} processes)"
    rq worker-pool --num-workers "${MEGALINTER_SERVER_WORKER_POOL_NUMBER}" --url "redis://${MEGALINTER_SERVER_REDIS_HOST}:${MEGALINTER_SERVER_REDIS_PORT}" "${MEGALINTER_SERVER_REDIS_QUEUE}"
  else
    # Use RQ worker (a worker can execute a single job parallelly)
    echo "[MegaLinter Worker] Init Redis Queue Single worker"
    rq worker --url "redis://${MEGALINTER_SERVER_REDIS_HOST}:${MEGALINTER_SERVER_REDIS_PORT}" "${MEGALINTER_SERVER_REDIS_QUEUE}"
  fi
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
