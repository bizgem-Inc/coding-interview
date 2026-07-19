from django.db import IntegrityError, transaction
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ModelViewSet

from api.models import Category
from api.serializers import CategorySerializer


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def perform_create(self, serializer):
        self._save_serializer(serializer)

    def perform_update(self, serializer):
        self._save_serializer(serializer)

    @staticmethod
    def _save_serializer(serializer):
        try:
            with transaction.atomic():
                serializer.save()
        except IntegrityError as error:
            constraint_name = getattr(getattr(error.__cause__, "diag", None), "constraint_name", None)
            if constraint_name == "unique_company_category_combination":
                raise ValidationError({"non_field_errors": "同じ企業内に同名のカテゴリは作成できません。"}) from error
            raise
