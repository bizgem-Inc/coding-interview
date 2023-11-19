# /bin/bash
docker compose run --rm api sh -c 'python -m coverage run manage.py test && python -m coverage html'