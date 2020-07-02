FROM python:3.8.3-alpine3.12

ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt /app/
RUN apk add --no-cache \
    postgresql-libs \
    && apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    postgresql-dev \
    && pip install -r requirements.txt --no-cache-dir \
    && apk del .build-deps

COPY . /app
RUN pip install -e .
