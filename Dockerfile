FROM python:3.11-slim

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml ./
RUN uv pip install --system -e ".[dev]"

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
