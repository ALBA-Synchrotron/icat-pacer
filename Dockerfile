FROM registry.cells.es/docker/python:3.12.6-slim-bullseye

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV BROKER_TYPE=None

RUN rm -rf /var/cache/apt/archives /var/lib/apt/lists/*

WORKDIR /icat-pacer/

RUN mkdir /icat-pacer/logs

COPY . /icat-pacer/

RUN pip install --no-cache-dir -r requirements.txt

# Conditional installation if BROKER_TYPE is redis
RUN if [ "$BROKER_TYPE" = "redis" ]; then \
        pip install --no-cache-dir -r requirements_redis.txt; \
    fi

# Conditional installation if BROKER_TYPE is sqs
RUN if [ "$BROKER_TYPE" = "sqs" ]; then \
        pip install --no-cache-dir -r requirements_redis.txt; \
    fi


CMD ["python", "run.py"]
