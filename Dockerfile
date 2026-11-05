FROM python:3.15.2-slim-trixie AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

ARG BROKER_TYPE=none

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt requirements_redis.txt requirements_sqs.txt ./

RUN pip install --no-cache-dir -r requirements.txt && \
    if [ "$BROKER_TYPE" = "redis" ]; then \
        pip install --no-cache-dir -r requirements_redis.txt; \
    elif [ "$BROKER_TYPE" = "sqs" ]; then \
        pip install --no-cache-dir -r requirements_sqs.txt; \
    fi

RUN rm -rf \
    /opt/venv/lib/python3.15/site-packages/pip \
    /opt/venv/lib/python3.15/site-packages/pip-*.dist-info \
    /opt/venv/lib/python3.15/site-packages/_pytest \
    /opt/venv/lib/python3.15/site-packages/pytest \
    /opt/venv/lib/python3.15/site-packages/pytest-*.dist-info \
    && find /opt/venv -type d -name __pycache__ -prune -exec rm -rf {} + \
    && find /opt/venv -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete

FROM python:3.15.2-slim-trixie AS runtime

ARG BROKER_TYPE=none
ARG NEW_UID=1000
ARG PRIMARY_GID=1000
ARG EXTRA_GIDS=1001,1002

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    BROKER_TYPE=${BROKER_TYPE} \
    TZ=Europe/Madrid \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /icat-pacer

RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2 \
    libxslt1.1 \
    zlib1g \
    tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid "$PRIMARY_GID" pacer \
    && useradd \
        --shell /bin/sh \
        --no-create-home \
        --uid "$NEW_UID" \
        --gid "$PRIMARY_GID" \
        --comment "" \
        pacer \
    && for gid in $(echo "$EXTRA_GIDS" | tr ',' ' '); do \
        group="g${gid}"; \
        getent group "$group" || groupadd --gid "$gid" "$group"; \
        usermod -aG "$group" pacer; \
    done \
    && mkdir -p /icat-pacer/logs \
    && chown -R pacer:pacer /icat-pacer

COPY --from=builder /opt/venv /opt/venv

COPY --chown=pacer:pacer . /icat-pacer/

USER pacer

CMD ["python", "run.py"]

