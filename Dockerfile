FROM registry.cells.es/docker/python:3.12.6-slim-bullseye

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN rm -rf /var/cache/apt/archives /var/lib/apt/lists/*

WORKDIR /icat-pacer/app

RUN mkdir /icat-pacer/logs

COPY ./* /icat-pacer/app

RUN mkdir -p /icat-pacer/config/
COPY rabbitmq.json /icat-pacer/config/


RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "run.py"]
