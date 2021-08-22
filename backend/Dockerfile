FROM tiangolo/uvicorn-gunicorn:python3.8-slim

LABEL maintainer="Max Mecklin <max.mecklin@hewo.fi>"

ARG BUILD_VERSION


RUN apt-get update && apt-get install -y postgresql-client

COPY . /app

WORKDIR /app

RUN chmod +x /app/prestart.sh

RUN date +%Y.%m.%d > .build

ENV PYTHONPATH "${PYTHONPATH}:/app"
ENV VERSION=${BUILD_VERSION}

RUN pip install -r requirements.txt
