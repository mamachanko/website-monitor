FROM python:3.9.0

WORKDIR /src

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY website_monitor /src/website_monitor
