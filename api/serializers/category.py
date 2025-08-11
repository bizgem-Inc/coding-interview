from rest_framework import serializers

from api.models import Category

class CategorySerializer(serializers.ModelSerializer):
    company_name = serializers.StringRelatedField(source='company.name', read_only=True)
    parent_category_name = serializers.StringRelatedField(source='parent_category.name', read_only=True, allow_null=True)

    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        """
            親カテゴリがある場合に、親カテゴリの企業IDと企業IDが一致しない場合はエラーとする
        """
        if attrs['parent_category'] and attrs['company'].id != attrs['parent_category'].company.id:
            raise serializers.ValidationError("Parent category must belong to the same company.")
        return attrs
