import json

from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from api.base import APIViewBase, ResourceNotFoundException
from domain.service.category import CategoryDomainService


# RESTfulにするならクラスをまとめる
class CategoryCreateAPIView(APIViewBase):
    def __init__(self):
        super().__init__()

    @classmethod
    def schema(cls):
        VALID_SCHEMA = {
            "name": {"type": "string", "required": True, "empty": False, "maxlength": 255},
            "parent_category_id": {"type": "string", "required": False, "empty": False, "maxlength": 36},
            "company": {
                "type": "dict",
                "required": True,
                "empty": False,
                "schema": {
                    "name": {"type": "string", "required": True, "empty": False, "maxlength": 255},
                }
            }
        }

        return VALID_SCHEMA


    def post_business_logic(self) -> Response:

        request_body = json.loads(self.request.body)
        service = CategoryDomainService()

        service.create(
            request_body.get("name"),
            request_body.get("parent_category_id"),
            request_body.get("company").get("name"),
        )

        return Response(
            data={
                "message": "success"
            },
            status=HTTP_200_OK,
        )


class CategoryListAPIView(APIViewBase):
    def __init__(self):
        super().__init__()

    def get_business_logic(self) -> Response:

        service = CategoryDomainService()
        entities = service.list_all()

        serialized_entities = []

        for entity in entities:
            serialized_entities.append(entity.to_dict())

        return Response(
            data={
                "entities": serialized_entities
                },
            status=HTTP_200_OK,
        )


class CategoryDetailAPIView(APIViewBase):
    def __init__(self):
        super().__init__()

    def get_business_logic(self) -> Response:

        id = self.kwargs["id"]

        service = CategoryDomainService()
        entity = service.fetch(id)

        if entity is None:
            raise ResourceNotFoundException

        return Response(
            data={
                "entity": entity.to_dict()
            },
            status=HTTP_200_OK,
        )


class CategoryUpdateAPIView(APIViewBase):
    def __init__(self):
        super().__init__()

    @classmethod
    def schema(self):
        VALID_SCHEMA = {
            "id": {"type": "string", "required": True, "empty": False, "maxlength": 36},
            "name": {"type": "string", "required": False, "empty": False, "maxlength": 255},
            "parent_category_id": {"type": "string", "required": False, "empty": False, "maxlength": 36},
            "company_name": {"type": "string", "required": False, "empty": False, "maxlength": 255},
        }

        return VALID_SCHEMA

    def put_business_logic(self) -> Response:

        request_body = json.loads(self.request.body)

        service = CategoryDomainService()
        service.update(
            request_body.get("id"),
            request_body.get("name"),
            request_body.get("parent_category_id"),
            request_body.get("company_id"),
        )

        return Response(
            data={
                "message": "success"
            },
            status=HTTP_200_OK,
        )

class CategoryDeleteAPIView(APIViewBase):
    def __init__(self):
        super().__init__()

    def delete_business_logic(self) -> Response:

        id = self.kwargs["id"]

        service = CategoryDomainService()
        service.delete(id)

        return Response(
            data={
                "message": "success"
            },
            status=HTTP_200_OK,
        )
