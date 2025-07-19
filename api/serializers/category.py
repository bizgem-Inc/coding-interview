from rest_framework import serializers
from api.models.category import Category
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'company', 'name', 'parent_category', 'created_at', 'updated_at')
        validators = [] # カスタムバリデーションを追加するための設定

    def validate(self, data):
        company = data.get('company') or getattr(self.instance, 'company', None)
        name = data.get('name') or getattr(self.instance, 'name', None)
        # company + name の組み合わせがユニークか確認
        if Category.objects.filter(company=company, name=name).exclude(id=getattr(self.instance, 'id', None)).exists():
            raise serializers.ValidationError("同じ企業内でカテゴリ名は一意である必要があります。")

        # parent_categoryが同じcompany内であることを確認
        parent = data.get('parent_category')
        if parent and parent.company != company:
            raise serializers.ValidationError("親カテゴリは同じ企業に属している必要があります。")

        return data