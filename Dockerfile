
# syntax=docker/dockerfile:1
FROM python:3.10.1-slim-buster
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8050
CMD gunicorn --workers 5 --threads 2 -b 0.0.0.0:8050 --timeout 0 app:server

#docker build -t azurscd/barometre-science-ouverte-uca:latest .
#docker run --name barometre-science-ouverte-uca -p 8050:8050 azurscd/barometre-science-ouverte-uca:latest