# Kovaaks stat tracker


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
