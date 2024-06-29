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
ARG NPM_VERSION=10.8.0
ARG UNGIT_VERSION=1.5.26
ARG MEGA_LINTER_RUNNER_VERSION=7.11.1
ARG MARKDOWN_TABLE_FORMATTER_VERSION=1.6.0

# hadolint ignore=DL3008
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
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
# hadolint ignore=SC1090,SC1091
RUN curl  -LsSf https://astral.sh/uv/install.sh | sh \
    && source "$HOME/.cargo/env"

# Disabled the final stage, as it ends up being longer to launch overall
# #########################
# #         final         #
# #########################
# FROM ubuntu:jammy

# COPY --from=gitpod-user / /

# USER gitpod
