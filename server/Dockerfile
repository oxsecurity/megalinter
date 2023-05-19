FROM python:3.11-alpine

#RUN apk add --update --no-cache \
#            git
RUN apk add git

# Core MegaLinter
COPY megalinter /megalinter
RUN PYTHONDONTWRITEBYTECODE=1 python /megalinter/setup.py install \
    && PYTHONDONTWRITEBYTECODE=1 python /megalinter/setup.py clean --all \
    && rm -rf /var/cache/apk/* \
    && find . | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf

COPY megalinter/descriptors /megalinter-descriptors
COPY TEMPLATES /action/lib/.automation

# MegaLinter Server
COPY server /server
COPY server/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY logging.conf logging.conf

CMD REDIS_HOST=localhost uvicorn server.server:app