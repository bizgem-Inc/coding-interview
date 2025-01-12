import uuid
from typing import Optional

from rest_framework import serializers

from item_api.util import uuid_of
from item_api.exception.custom_exceptions import RequiredException

DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f+00:00"

def create_error_message(message: str) -> dict[str, str]:
    return { 'message' : message }

def validate_require(value: Optional[str], key_name:str, item_name: str) -> str:
    if value is None or value == '':
        raise RequiredException(item_name=item_name)
    return value


