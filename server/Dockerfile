FROM python:3.12-alpine

RUN apk add --upgrade --no-cache git

WORKDIR /

COPY logging.conf logging.conf

COPY megalinter /megalinter
RUN PYTHONDONTWRITEBYTECODE=1 python /megalinter/setup.py install \
    && PYTHONDONTWRITEBYTECODE=1 python /megalinter/setup.py clean --all \
    && rm -rf /var/cache/apk/* \
    && find . | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf 

COPY server /server
COPY server/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

