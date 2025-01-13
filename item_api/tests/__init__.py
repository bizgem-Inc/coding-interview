import json
from datetime import datetime
from typing import List, Dict, Any
from uuid import UUID
from django.db import models

from item_api.serializers.company import CompanySerializer


def test_support_serializer(obj: models.Model) -> str:
    """
    django の model の
     * UUID を文字列
     * datetime を +00:00
     に変換して値を返します。
    """
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def convert_to_list(queryset: Any) -> List[Dict[str, str]]:
    return json.loads(json.dumps(list(queryset.values()), default=test_support_serializer))

def convert_model_to_list(django_models: List[models.Model]) -> List[Dict[str, str]]:
    return [convert_to_dict(model) for model in django_models]

def convert_to_dict(model: models.Model) -> Dict[str, str]:
    return CompanySerializer(model).data
