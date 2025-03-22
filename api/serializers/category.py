from rest_framework import serializers
from api.models.category import Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "company", "name", "parent_category", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_parent_category(self, value):
        if not self.instance:
            return value

        if not value:
            return value

        if self.instance.id == value.id:
            raise serializers.ValidationError("自分自身を親カテゴリとして登録はできません")

        return value