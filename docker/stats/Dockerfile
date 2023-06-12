FROM python:3.9-slim AS base

RUN apt-get update -y \
  && apt-get install --yes --no-upgrade --no-install-recommends \
    python3.9 \
    python3-pip \
  && apt-get clean \
  && rm -rf \
    /tmp/* \
    /usr/share/doc/* \
    /var/cache/apt/* \
    /var/lib/apt/lists/* \
    /var/tmp/*

WORKDIR /srv/voyages-stats
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1
COPY stats/requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
CMD ["flask", "run"]
