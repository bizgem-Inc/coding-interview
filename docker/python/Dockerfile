FROM python:3.11

WORKDIR /app

COPY test_app/Pipfile test_app/Pipfile.lock /app/

RUN pip install pipenv
RUN pipenv install --deploy --system

COPY . /app
