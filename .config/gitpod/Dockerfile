###################
#     builder     #
###################
# First stage: Install build-time dependencies
FROM ubuntu:noble as builder

# hadolint ignore=DL3002
USER root

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Copy Python version config file
COPY .python-version /tmp/

# Update system and install packages
# hadolint ignore=DL3008,DL3009,DL3013
RUN PYTHON_VERSION=$(cut -d '.' -f 1,2 /tmp/.python-version) \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    bash-completion \
    ca-certificates \
    curl \
    git \
    git-lfs \
    gnupg \
    htop \
    iproute2 \
    lsb-release \
    make \
    nano \
    python3-pip \
    "python${PYTHON_VERSION}" \
    "python${PYTHON_VERSION}-venv" \
    sudo \
    tree \
    vim \
    wget

############################
#     docker-installer     #
############################
FROM builder as docker-installer

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# hadolint ignore=DL3008,DL3009
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update \
    && apt-get install -y --no-install-recommends docker-ce docker-ce-cli containerd.io

###########################
#      npm-installer      #
###########################
FROM docker-installer as npm-installer

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Set a variable for packages version
# renovate: datasource=npm depName=npm
ARG NPM_VERSION=11.2.0
# renovate: datasource=npm depName=ungit
ARG UNGIT_VERSION=1.5.28
# renovate: datasource=npm depName=mega-linter-runner
ARG MEGA_LINTER_RUNNER_VERSION=8.5.0
# renovate: datasource=npm depName=markdown-table-formatter
ARG MARKDOWN_TABLE_FORMATTER_VERSION=1.6.1

# Adapted from instructions in 
# https://github.com/nodesource/distributions?tab=readme-ov-file#using-ubuntu-nodejs-22
# hadolint ignore=DL3008
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install  -y --no-install-recommends nodejs \
    && npm install -g "npm@${NPM_VERSION}" \
    && npm install -g \
    "ungit@${UNGIT_VERSION}" \
    "mega-linter-runner@${MEGA_LINTER_RUNNER_VERSION}" \
    "markdown-table-formatter@${MARKDOWN_TABLE_FORMATTER_VERSION}"

###########################
#         cleanup         #
###########################
FROM npm-installer as cleanup

RUN apt-get clean && rm -rf /var/lib/apt/lists/* tmp/* 

###########################
#       gitpod-user       #
###########################
FROM cleanup as gitpod-user

# UID must be 33333.
RUN useradd -l -u 33333 -G sudo -md /home/gitpod -s /bin/bash -p gitpod gitpod

USER gitpod

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
# renovate: datasource=github-releases depName=astral-sh/uv
ARG UV_VERSION=0.6.6
# hadolint ignore=SC1090,SC1091
RUN curl -LsSf "https://astral.sh/uv/${UV_VERSION}/install.sh" | sh \
    && source "$HOME/.local/bin/env"
ENV PATH="~/.local/bin/:$PATH"

# Disabled the final stage, as it ends up being longer to launch overall
# #########################
# #         final         #
# #########################
# FROM ubuntu:noble

# COPY --from=gitpod-user / /

# USER gitpod
