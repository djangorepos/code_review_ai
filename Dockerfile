FROM python:3.13.0-alpine

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN pip install poetry==1.8.4 && poetry install --no-root

COPY . .