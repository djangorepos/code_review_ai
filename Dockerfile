FROM python:3.13.0-alpine

WORKDIR /app
COPY . /app

RUN pip install poetry && poetry install

CMD ["/usr/local/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
