FROM python:3.13
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

#RUN mkdir -p /app/certs
CMD ["gunicorn", "--certfile=/app/certs/cert.pem", "--keyfile=/app/certs/key.pem", "-b", "127.0.0.1:443", "--chdir", "src", "-w", "4", "app:app"]
