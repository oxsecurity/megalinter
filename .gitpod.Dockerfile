# This image should be the last one to be used inside an workspace container. In this cause, we use an varation of
# the official Gitpod workspace image as the final image.
# Source Dockerfile: https://gitlab.com/gitpodify/gitpodified-workspace-images/-/blob/recaptime-dev-mainline/full/Dockerfile
FROM quay.io/gitpodified-workspace-images/full

COPY requirements.dev.txt /tmp/deps-dev.txt

RUN pip3 install -r /tmp/dev-deps.txt \
    && rm /tmp/deps-dev.txt; \
    brew install shellcheck hadolint shfmt