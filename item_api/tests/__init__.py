import json
from datetime import datetime
from typing import List, Dict, Any
from uuid import UUID
from django.db import models

from item_api.models import Category, Company
from item_api.serializers.category import CategorySerializer
from item_api.serializers.company import CompanySerializer


def test_support_serializer(obj: Any) -> str:
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


def convert_model_to_category_list(categories: List[Category]) -> List[Dict[str, str]]:
    return [convert_to_category_dict(model) for model in categories]

def convert_to_category_dict(model: Category) -> Dict[str, str]:
    return {
        'id' : test_support_serializer(model.id),
        'name' : model.name,
        'company': test_support_serializer(model.company.id),
        'parent_category' : None if model.parent_category is None else test_support_serializer(model.parent_category.id),
        'created_at' : test_support_serializer(model.created_at),
        'updated_at': test_support_serializer(model.updated_at),
    }

def convert_model_to_company_list(companies: List[Company]) -> List[Dict[str, str]]:
    return [convert_to_company_dict(model) for model in companies]

def convert_to_company_dict(model: models.Model) -> Dict[str, str]:
    return CompanySerializer(model).data

