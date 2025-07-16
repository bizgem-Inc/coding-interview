from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from api.models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'company', 'parent_category', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        validators = [
            UniqueTogetherValidator(
                queryset=Category.objects.all(),
                fields=['company', 'name'],
                message='この企業には既に同じ名前のカテゴリが存在します。'
            )
        ]
    
    def validate_parent_category(self, value):
        """親カテゴリのバリデーション"""
        if value:
            # 作成時のcompanyと親カテゴリのcompanyが一致するか確認
            if 'company' in self.initial_data:
                company_id = self.initial_data['company']
                if str(value.company.id) != company_id:
                    raise serializers.ValidationError('親カテゴリは同じ企業のカテゴリである必要があります。')
        return value