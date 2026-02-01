from rest_framework import serializers
from api.models.category import Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate(self, data):
        """
        カテゴリの作成・更新時のバリデーションを行う。
        """
        company = data.get('company') or getattr(self.instance, 'company', None)
        
        # 親カテゴリがリクエストデータに含まれている場合はその値を使用する。含まれていない場合はインスタンスの値を使用する。
        if 'parent_category' in data:
            parent_category = data['parent_category']
        else:
            parent_category = getattr(self.instance, 'parent_category', None)

        # 親カテゴリの整合性チェック
        if parent_category:
            self._validate_parent_category(parent_category, company)

        return data

    def _validate_parent_category(self, parent_category, company):
        """
        親カテゴリに関する整合性を検証する
        """
        # 親カテゴリが同じ会社に属しているか確認する
        if company and parent_category.company_id != company.id:
            raise serializers.ValidationError({
                "parent_category": "The parent category must belong to the same company."
            })
        
        # 自分自身を親に設定していないか確認する
        if self.instance and parent_category.id == self.instance.id:
            raise serializers.ValidationError({
                "parent_category": "A category cannot be its own parent."
            })