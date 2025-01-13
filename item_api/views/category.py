from typing import List, Dict

from item_api.util import uuid_of
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from item_api.models import Category
from item_api.serializers.category import CategorySerializer
from rest_framework.viewsets import ModelViewSet

from item_api.views import CustomPageNumberPagination, extract_uuid


class CategoryAPIView(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        """
        クエリパラメータに基づいてフィルタリングする
        """
        queryset = super().get_queryset()  # デフォルトのクエリセットを取得
        name = self.request.query_params.get('name', None)  # `name` パラメータを取得
        company = self.request.query_params.get('company', None)  # `company` パラメータを取得

        # `name` で曖昧検索
        if name:
            queryset = queryset.filter(name__icontains=name)

        # `company` で完全一致
        if company and uuid_of(company):
            queryset = queryset.filter(company=company)
        return queryset

    def list(self, request, *args, **kwargs):
        result = super().list(request, *args, **kwargs)
        result['results'] = format_response_body(result.data['results'])
        return result


    def retrieve(self, request, *args, **kwargs):
        result = super().retrieve(request, *args, **kwargs)
        return Response(format_response_body_by_dict(result.data))

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        result = super().create(request, *args,**kwargs)
        return Response(format_response_body_by_dict(response_body=result.data), status=status.HTTP_201_CREATED)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        result = super().update(request, *args, **kwargs)
        return Response(format_response_body_by_dict(result.data))

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

def format_response_body(response_body: List[Dict[str, str]]) -> List[Dict[str, str]]:
    for current in response_body:
        format_response_body_by_dict(response_body=current)
    return response_body

def format_response_body_by_dict(response_body: Dict[str, str]) -> Dict[str, str]:
    response_body['company'] = extract_uuid(response_body['company'])
    response_body['parent_category'] = extract_uuid(response_body.get('parent_category', None))
    return response_body
