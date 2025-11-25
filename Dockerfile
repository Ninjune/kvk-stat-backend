FROM python:3.13
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

#RUN mkdir -p /app/certs
CMD ["gunicorn", "-b", "0.0.0.0:80", "--chdir", "src", "-w", "4", "app:app"]
