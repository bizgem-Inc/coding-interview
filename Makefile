.PHONY: dev mm test db

dev:
	docker compose up

mm:
	docker compose exec app python manage.py makemigrations api

test:
	docker compose exec app python manage.py test -v 3 api

db:
	docker compose exec db psql -U postgres -d coding-test
