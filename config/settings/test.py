import os

from .base import *

INSTALLED_APPS = [
    "rest_framework",
    "item_api",
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
REST_FRAMEWORK = {
    'TEST_REQUEST_DEFAULT_FORMAT': 'json'
}