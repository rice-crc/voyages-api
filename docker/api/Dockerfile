###
### Python 3.9 slim
###

# -- Base --

FROM python:3.9-slim AS base

RUN apt-get update -y

# -- Build --

FROM base AS build

RUN apt-get install -y \
	default-libmysqlclient-dev \
	gcc

WORKDIR /srv/voyages-api

RUN python3 -m pip install --user --no-cache-dir --upgrade \
    pip \
    setuptools \
    wheel

COPY api/requirements.txt .

RUN pip install --user --no-cache-dir -r ./requirements.txt

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
