FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev gcc netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency manifest(s) first for better caching
COPY Pipfile Pipfile.lock* /app/

RUN pip install --upgrade pip \
    && pip install django djangorestframework psycopg2-binary

# Copy project
COPY . /app/

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8000"]
