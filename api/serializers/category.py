from rest_framework import serializers
from api.models.category import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

    # def validate_title(self, value):
    #     if "Django" not in value:
    #         raise serializers.ValidationError(
    #             "タイトルには'Django'を含める必要があります。"
    #         )
    #     return value
