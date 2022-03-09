###
### Ubuntu 2004 with default Python 3.9
###

# -- Base --

FROM ubuntu:20.04 AS base

RUN apt-get update -y \
  && apt-get install --yes --no-upgrade --no-install-recommends \
    libmysqlclient-dev \
    mysql-client \
    python3.9 \
    python3-pip \
  && apt-get clean \
  && rm -rf \
    /tmp/* \
    /usr/share/doc/* \
    /var/cache/apt/* \
    /var/lib/apt/lists/* \
    /var/tmp/*

# -- Build --

FROM base AS build

RUN apt-get update -y \
  && apt-get install --yes --no-upgrade --no-install-recommends \
    gcc \
    python3.9-dev \
  && apt-get clean \
  && rm -rf \
    /tmp/* \
    /usr/share/doc/* \
    /var/cache/apt/* \
    /var/lib/apt/lists/* \
    /var/tmp/*

WORKDIR /srv/voyagesapi

RUN python3.9 -m pip install --user --no-cache-dir --upgrade \
    pip \
    setuptools \
    wheel

COPY src/requirements.txt .
RUN python3.9 -m pip install --user --no-cache-dir -r ./requirements.txt

# -- Release --

FROM base AS release

WORKDIR /srv/voyagesapi

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH=/root/.local/bin:$PATH

COPY --from=build /root/.local /root/.local
COPY . .

ARG GUNICORN_PORT="8000"
ARG GUNICORN_OPTS="--reload --workers 3 --threads 2 --worker-class gthread"

ENV GUNICORN_PORT=${GUNICORN_PORT}
ENV GUNICORN_OPTS=${GUNICORN_OPTS}

EXPOSE $GUNICORN_PORT

CMD gunicorn --bind 0.0.0.0:$GUNICORN_PORT $GUNICORN_OPTS voyages2021.wsgi
