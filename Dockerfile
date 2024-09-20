FROM python:3.11.3-slim

COPY Pipfile .
COPY Pipfile.lock .

RUN pip install pipenv
RUN pipenv install --system
