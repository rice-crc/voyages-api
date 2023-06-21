FROM python:3.9-slim AS base

RUN apt-get update -y \
  && apt-get install --yes --no-upgrade --no-install-recommends \
    python3 \
    python3-pip \
  && apt-get clean \
  && rm -rf \
    /tmp/* \
    /usr/share/doc/* \
    /var/cache/apt/* \
    /var/lib/apt/lists/* \
    /var/tmp/*

WORKDIR /srv/voyages-networks
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1
COPY networks/requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5005
COPY . .
CMD ["flask", "run", "--host=0.0.0.0", "--port=5005"]]
