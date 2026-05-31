from rest_framework import viewsets, exceptions

from api.models.category import Category
from api.serializers.category import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.action == "list":
            company_id = self.request.query_params.get("company")
            if not company_id:
                raise exceptions.ValidationError({"company": "This query parameter is required for listing categories."})
            queryset = queryset.filter(company_id=company_id)

        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if Category.objects.filter(parent_category=instance).exists():
            from rest_framework import status
            from rest_framework.response import Response
            return Response(
                {"detail": "Cannot delete this category because it has child categories."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)
