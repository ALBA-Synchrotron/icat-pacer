FROM python:3.15.2-slim-trixie

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV BROKER_TYPE=None
ENV TZ=Europe/Madrid

ARG NEW_UID=1000
ARG PRIMARY_GID=1000
ARG EXTRA_GIDS=1001,1002

WORKDIR /icat-pacer/

RUN addgroup --gid $PRIMARY_GID pacer
RUN adduser --shell /bin/sh --no-create-home --uid $NEW_UID --gid $PRIMARY_GID --disabled-login --gecos "" pacer

RUN set -eux; \
    for gid in $(echo "$EXTRA_GIDS" | tr ',' ' '); do \
        group="g${gid}"; \
        addgroup --gid "$gid" "$group" || true; \
        addgroup pacer "$group"; \
    done

RUN apt-get update && apt-get install -y build-essential \
    libxml2 \
    libxslt1.1 \
    zlib1g \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev

RUN mkdir /icat-pacer/logs

COPY . /icat-pacer/

RUN pip install --no-cache-dir -r requirements.txt

# Conditional installation if BROKER_TYPE is redis
RUN if [ "$BROKER_TYPE" = "redis" ]; then \
        pip install --no-cache-dir -r requirements_redis.txt; \
    fi

# Conditional installation if BROKER_TYPE is sqs
RUN if [ "$BROKER_TYPE" = "sqs" ]; then \
        pip install --no-cache-dir -r requirements_sqs.txt; \
    fi

RUN apt-get purge -y --auto-remove \
        build-essential \
        libxml2-dev \
        libxslt1-dev \
        zlib1g-dev \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*

USER pacer

CMD ["python", "run.py"]
