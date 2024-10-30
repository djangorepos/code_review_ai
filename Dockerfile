FROM python:3.13.0-alpine

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN pip install poetry && poetry install --no-root

COPY . .