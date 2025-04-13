from rest_framework import serializers
from api.models.category import Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate(self, data):
        """
        `parent_category`が指定されている場合、
        親カテゴリの`company`と`company`が同一であることを検証
        """
        # 新規作成の場合はdataから取得、更新の場合はinstanceの値も考慮
        company = data.get('company') or (self.instance.company if self.instance else None)
        parent = data.get('parent_category')
        if parent and company and parent.company != company:
            raise serializers.ValidationError(
                {"parent_category": "The parent category must belong to the same company."}
            )
        return data
