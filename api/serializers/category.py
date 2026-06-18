from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from api.models.category import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Category.objects.all(),
                fields=('company', 'name')
            )
        ]