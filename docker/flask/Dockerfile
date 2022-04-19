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

WORKDIR /srv/voyages-flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1
COPY flask/requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
CMD ["flask", "run"]
