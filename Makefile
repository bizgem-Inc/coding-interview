setup:
	pipenv install --deploy --system
	pipenv run python manage.py migrate
run:
	# TODO: to python manage.py ...
	pipenv run python manage.py runserver 0.0.0.0:8000

