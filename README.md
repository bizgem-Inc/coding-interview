# coding-interview

## Requirements

- Docker

## Tech Stack

- Python 3
- [pipenv](https://pipenv.pypa.io/)
- PostgreSQL 18

## Setup

Build and start the services:

```bash
docker compose up --build
```

```bash
docker compose run --rm webapi make setup
```

The API is then available at http://localhost:8000/api/.


## Running tests

```bash
docker compose run --rm webapi pipenv run python manage.py test
```
