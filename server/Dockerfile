##################
# Build wheel for megalinter python package
##################
FROM ghcr.io/astral-sh/uv:0.6.13 AS uv
FROM python:3.13.3-alpine3.21 AS build-ml-core
WORKDIR /
COPY pyproject.toml .
COPY --from=uv /uv /bin/uv
RUN --mount=type=cache,target=/root/.cache/uv \
     uv pip install --system -r pyproject.toml
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system .

FROM python:3.13-alpine

RUN apk add --upgrade --no-cache git

WORKDIR /

COPY logging.conf logging.conf

COPY --from=build-ml-core pyproject.toml README.md ./
COPY --from=build-ml-core megalinter /megalinter/
RUN --mount=type=cache,target=/root/.cache/uv,from=build-ml-core \
    --mount=from=uv,source=/uv,target=/bin/uv \
    uv pip install --system -e .

COPY server /server
COPY server/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

