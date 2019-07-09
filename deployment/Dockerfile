FROM python:3.7.4-alpine3.9

RUN mkdir /app

WORKDIR app

COPY ./requirements.txt requirements.txt

RUN apk add --no-cache --virtual .build-deps \
    gcc \
    python3-dev \
    musl-dev \
    postgresql-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del --no-cache .build-deps

RUN apk --no-cache add libpq
COPY . /app