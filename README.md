# Coding Interview — Django Categories API

This repository is a small Django project used for a coding interview task.

What this does
- Implements a simple Category model (with Company relation and optional parent).
- Exposes a REST API to list, create, retrieve, update and delete categories.

Quickstart (recommended: Docker)
1. Start services (Postgres + web):

```bash
docker compose up --build -d
```

2. Run the test suite:

```bash
docker compose exec web python manage.py test
```

3. Open the API browsable UI in your browser at http://localhost:8000/api/

API endpoints
- List / Create: `GET` or `POST` http://localhost:8000/api/categories/
- Retrieve / Update / Delete: `GET`, `PATCH` or `DELETE` http://localhost:8000/api/categories/{id}/

Examples (curl)
- Create:

```bash
curl -sS -X POST http://localhost:8000/api/categories/ \
	-H 'Content-Type: application/json' \
	-d '{"company":"<company-uuid>","name":"Example"}'
```

- Update (partial):

```bash
curl -sS -X PATCH http://localhost:8000/api/categories/<id>/ \
	-H 'Content-Type: application/json' \
	-d '{"name":"Renamed"}'
```