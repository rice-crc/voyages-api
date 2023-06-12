###
### Python 3.9 slim
###

# -- Base --

FROM python:3.9-slim AS base

RUN apt-get update -y

# 
#   && apt-get install --yes --no-install-recommends \
#     build-essential \
#   && apt-get clean \
#   && rm -rf \
#     /tmp/* \
#     /usr/share/doc/* \
#     /var/cache/apt/* \
#     /var/lib/apt/lists/* \
#     /var/tmp/*

# 
# FROM ubuntu:20.04 AS base
# 
# RUN apt-get update -y \
#   && apt-get install --yes --no-upgrade --no-install-recommends \
#     libmysqlclient-dev \
#     mysql-client \
#     python3.9 \
#     python3-pip \
#     python3.9-dev \
#     libpq-dev \
#   && apt-get clean \
#   && rm -rf \
#     /tmp/* \
#     /usr/share/doc/* \
#     /var/cache/apt/* \
#     /var/lib/apt/lists/* \
#     /var/tmp/*

# -- Build --

FROM base AS build

RUN apt-get install -y  --no-install-recommends \
    gcc \
	default-libmysqlclient-dev
#   && apt-get clean 
#   && rm -rf \
#     /tmp/* \
#     /usr/share/doc/* \
#     /var/cache/apt/* \
#     /var/lib/apt/lists/* \
#     /var/tmp/*

WORKDIR /srv/voyages-api

RUN python3.9 -m pip install --user --no-cache-dir --upgrade \
    pip \
    setuptools \
    wheel

COPY api/requirements.txt .

RUN python3.9 -m pip install --user --no-cache-dir -r ./requirements.txt

# -- Release --

FROM build AS release

WORKDIR /srv/voyages-api

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH=/root/.local/bin:$PATH

COPY --from=build /root/.local /root/.local

ARG GUNICORN_PORT="8000"
ARG GUNICORN_OPTS="--reload --workers 3 --threads 2 --worker-class gthread"

ENV GUNICORN_PORT=${GUNICORN_PORT}
ENV GUNICORN_OPTS=${GUNICORN_OPTS}

EXPOSE $GUNICORN_PORT

CMD gunicorn --bind 0.0.0.0:$GUNICORN_PORT $GUNICORN_OPTS voyages3.wsgi
