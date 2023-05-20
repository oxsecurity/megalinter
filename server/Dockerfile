FROM python:3.11-alpine

RUN apk add --upgrade --no-cache git

WORKDIR /

COPY megalinter /megalinter
COPY server /server
COPY server/requirements.txt requirements.txt
COPY logging.conf logging.conf

RUN PYTHONDONTWRITEBYTECODE=1 python /megalinter/setup.py install \
    && PYTHONDONTWRITEBYTECODE=1 python /megalinter/setup.py clean --all \
    && rm -rf /var/cache/apk/* \
    && find . | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf \
    pip install -r requirements.txt

