# Kovaaks stat tracker

## About

This is a server that caches and provides an api to
the count of ranks for Kovaaks benchmarks. Every time the cache is generated,
set to 1 day currently, it will create graphs of the counts, cumulative counts,
and percentiles for the ranks (see https://ninjune.dev/rank-percentiles/). The API
is hosted at https://ninjune.dev/kvk-api.

## Self Hosting

It is suggested to host with docker b/c I have not tested without.

probably run:
```Bash
pip install --no-cache-dir -r requirements.txt
cd src
python -m flask --port 5000 --host=127.0.0.1
```
to run without docker.

Note that this will be on port 5000 @ localhost. Host at 0.0.0.0 to allow public access through public ip.

Uses:
- flask
- msgpack (json->bytes)
- gunicorn (for prod)
- plotly
- kaleido

### Compose files:
Local version:
```YAML
services:
  kvk-stat-backend:
    build: ./kvk-stat-backend
    stop_grace_period: 0.5s
    environment:
      - TZ=America/Chicago
      - USE_FLASK=true
    volumes:
      - ./kvk-stat-backend:/app
    ports:
      - 80:80
```


Hosted version:
```YAML
services:
  kvk-stat-backend:
    container_name: kvk-stat-backend
    image: ghcr.io/ninjune/kvk-stat-backend:latest
    stop_grace_period: 0.5s
    environment:
      - TZ=America/Chicago
    volumes:
      - ./logs:/app/logs
      - ./data/cached:/app/data/cached
    ports:
      - 8030:80
```
