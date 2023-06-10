###################
#     builder     #
###################
# First stage: Install build-time dependencies
FROM ubuntu:jammy as builder

# hadolint ignore=DL3002
USER root

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Copy Python version config file
COPY .config/python_version.config /tmp/

# Set a variable for the npm version
ARG NPM_VERSION=9.6.7
# Set a variable for the ungit version
ARG UNGIT_VERSION=1.5.23

# Update system and install packages
# hadolint ignore=DL3008,DL3009,DL3013
RUN PYTHON_VERSION=$(cut -d '=' -f 2 /tmp/python_version.config) \
    && apt-get update \
    && apt-get upgrade -y \
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
    wget \
    && python3 -m pip install --no-cache-dir --upgrade pip \
    && python3 -m pip install --no-cache-dir virtualenv

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

# hadolint ignore=DL3008
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install  -y --no-install-recommends nodejs \
    && npm install -g "npm@${NPM_VERSION}" \
    && npm install -g \
    "ungit@${UNGIT_VERSION}"

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

#########################
#         final         #
#########################
FROM ubuntu:jammy

COPY --from=gitpod-user / /

USER gitpod