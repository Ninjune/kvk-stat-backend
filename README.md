# Kovaaks stat tracker


```
services:
  kvk-stat-backend:
    build: ./kvk-stat-backend
    network_mode: host
    stop_grace_period: 0.5s
    environment:
      - TZ=America/Chicago
    volumes:
      - ./kvk-stat-backend:/app
    ports:
      - 80:80
      - 443:443
```
