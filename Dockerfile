FROM python:3.11

WORKDIR /app

RUN pip install pipenv

COPY Pipfile Pipfile.lock /app/

RUN pipenv sync --system

COPY . /app/
