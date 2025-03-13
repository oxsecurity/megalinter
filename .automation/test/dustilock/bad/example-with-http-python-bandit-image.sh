#!/bin/bash
# Example about how to call python bandit using its single-linter megalinter docker image

# DEFINE SCRIPT VARIABLES (you can do the same in your script)
ROOT_FOLDER="c:/git" # Always put an absolute path here. Must be the root of all your repositories
DOCKER_IMAGE="oxsecurity/megalinter-only-python_bandit:v6-alpha"
LINTER_NAME="PYTHON_BANDIT"
WORKSPACE_TO_LINT="demo-megalinter-security-flavor" #name of the folder you want to lint within root folder

# REMOVE PREVIOUS TEST CONTAINERS
echo "Removing previous tests containers..."
docker rm --force "$(docker ps --filter name=megalinter-server-PYTHON_BANDIT -q)" || true
echo ""
# docker container prune --filter name=megalinter-sshd --force

# PULL LATEST MEGALINTER IMAGE VERSION
echo "Pulling latest docker image $DOCKER_IMAGE..."
docker pull "$DOCKER_IMAGE" 

# START MEGALINTER SERVER CONTAINER
# Internal flask server runs on port 80
# MEGALINTER_SERVER is important,  so entrypoint.sh just runs flask server
# Remove -d if you want to see that the server if well started
START_TIME=$(date +%s%N)
echo "Starting MegaLinter container with volume $ROOT_FOLDER, using docker image $DOCKER_IMAGE..."
docker run \
       -p 1984:80 \
       --name "megalinter-server-$LINTER_NAME" \
       -v "$ROOT_FOLDER:/tmp/lint" \
       -e MEGALINTER_SERVER="true" \
       -d \
       "$DOCKER_IMAGE"

# STATS
echo ""
ELAPSED=$((($(date +%s%N) - $START_TIME)/1000000))
echo "MegaLinter server docker image $DOCKER_IMAGE has started in $ELAPSED ms"

# DISPLAY MEGALINTER CONTAINER
echo ""
docker ps
sleep 5s
echo ""

# Make first curl just to check server is running
echo "Make first curl: GET current processes. For now it can take 3 mn, it's probably a network thing"
START_TIME=$(date +%s%N)
curl http://127.0.0.1:1984/lint_request
ELAPSED=$((($(date +%s%N) - $START_TIME)/1000000))
echo "GET processed in $ELAPSED ms"
echo ""

# Request lint
echo "Request linting with curl POST"
START_TIME=$(date +%s%N)
curl -d "{ \"workspace\": \"/tmp/lint/${WORKSPACE_TO_LINT}\" }" -H "Content-Type: application/json" -X POST http://127.0.0.1:1984/lint_request
ELAPSED=$((($(date +%s%N) - $START_TIME)/1000000))
echo "LINT processed in $ELAPSED ms"
echo ""

# Request second lint in a row
echo "Request second linting with curl POST"
START_TIME=$(date +%s%N)
curl -d "{ \"workspace\": \"/tmp/lint/${WORKSPACE_TO_LINT}\" }" -H "Content-Type: application/json" -X POST http://127.0.0.1:1984/lint_request
ELAPSED=$((($(date +%s%N) - $START_TIME)/1000000))
echo "LINT processed in $ELAPSED ms"