from rest_framework import status, viewsets
from rest_framework.response import Response

from api.models.category import Category
from api.serializers.category import CategoryDetailSerializer, CategoryListSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return CategoryListSerializer
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
