from rest_framework import status, viewsets
from rest_framework.response import Response

from api.models.category import Category
from api.serializers.category import (
    CategoryCreateSerializer,
    CategoryDetailSerializer,
    CategoryListSerializer,
    CategoryUpdateSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return CategoryListSerializer
        if self.action == "create":
            return CategoryCreateSerializer
        if self.action in ["update", "partial_update"]:
            return CategoryUpdateSerializer
        return CategoryDetailSerializer

    def list(self, request, *args, **kwargs):
        company = request.query_params.get("company")
        if not company:
            return Response(
                {"company": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        queryset = self.queryset.filter(company=company)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(CategoryDetailSerializer(instance).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(CategoryDetailSerializer(instance).data)
