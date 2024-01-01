FROM python:3.11-slim

WORKDIR /app

RUN apt update && \
    apt install -y gcc libpq-dev

COPY Pipfile Pipfile.lock ./
RUN pip install --upgrade pip && \
    pip install pipenv && \
    pipenv install --system
