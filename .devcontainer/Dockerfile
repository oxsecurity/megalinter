FROM mcr.microsoft.com/devcontainers/python:1-3.13-bullseye

# renovate: datasource=npm depName=markdown-table-formatter
ARG NPM_MARKDOWN_TABLE_FORMATTER_VERSION=1.6.1

# renovate: datasource=node-version depName=node
ARG NODE_VERSION="23.11.0"

RUN if [ "${NODE_VERSION}" != "none" ]; then \
    su vscode -c "umask 0002 && . /usr/local/share/nvm/nvm.sh && nvm install ${NODE_VERSION} 2>&1"; fi

COPY .config/python/dev/requirements.txt /tmp/pip-tmp/

RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
   && rm -rf /tmp/pip-tmp \
   && npm install markdown-table-formatter@${NPM_MARKDOWN_TABLE_FORMATTER_VERSION} -g
