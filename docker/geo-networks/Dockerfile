# -- Build --

FROM python:3.9-slim AS build

WORKDIR /srv/voyages-geo-networks

COPY requirements.txt .

RUN pip install --user --no-cache-dir -r ./requirements.txt

# -- Release

FROM python:3.9-slim AS release

WORKDIR /srv/voyages-geo-networks

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH=/root/.local/bin:$PATH

COPY --from=build /root/.local /root/.local

COPY . .

ARG FLASK_PORT=5005

ENV FLASK_PORT=$FLASK_PORT

EXPOSE $FLASK_PORT

CMD flask run --host=0.0.0.0 --port=$FLASK_PORT