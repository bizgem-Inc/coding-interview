from rest_framework import serializers
from api.models import Category, Company


class CategorySerializer(serializers.ModelSerializer):
    # UUIDを適切な形式で処理
    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(),
        pk_field=serializers.UUIDField(format='hex_verbose')
    )

    class Meta:
        model = Category
        fields = '__all__'
