pipenv run python manage.py makemigrations --settings config.settings_local
pipenv run python manage.py migrate --settings config.settings_local
pipenv run python manage.py runserver 0.0.0.0:8000 --settings config.settings_local
