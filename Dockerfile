FROM registry.cells.es/docker/python:3.12.6-slim-bullseye

WORKDIR /icat-pacer/app

COPY ./* /icat-pacer/app

RUN mkdir -p /icat-pacer/config/
COPY rabbitmq.json /icat-pacer/config/

RUN pip install -r requirements.txt
