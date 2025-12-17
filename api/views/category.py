# -*- coding: utf-8 -*-
import sys

sys.dont_write_bytecode = True
from rest_framework import status
from rest_framework import views
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from api.models.category import Category
from api.serializers.category import CategorySerializer

import logging

logger = logging.getLogger(__name__)


class CategoryAPIView(views.APIView):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def patch(self, request, pk, *args, **kwargs):
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk, *args, **kwargs):
        category = get_object_or_404(Category, pk=pk)
        # 削除対象のカテゴリを親にしている子カテゴリが1件でも存在するか？
        if Category.objects.filter(parent_category=category).exists():
            raise ValidationError("子カテゴリを持つカテゴリは削除できません")
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
