FROM python:3.13.0-alpine

WORKDIR /app
COPY . /app

RUN pip install poetry && poetry install
