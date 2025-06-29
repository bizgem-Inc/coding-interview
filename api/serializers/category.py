from rest_framework import serializers
from api.models import Category, Company
from rest_framework.fields import UUIDField
from django.utils.translation import gettext_lazy as _


class CategorySerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(),
        pk_field=UUIDField(),
        error_messages={
            'required': 'この項目は必須です',
            'null': 'この項目は必須です',
            'does_not_exist': 'この項目は必須です',
        }
    )
    parent_category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        pk_field=UUIDField(),
        required=False,
        allow_null=True
    )
    name = serializers.CharField(
        max_length=50,
        error_messages={
            'required': 'この項目は必須です',
            'null': 'この項目は必須です',
            'blank': 'この項目は必須です',
            'max_length': 'カテゴリ名は50文字以下である必要があります',
        }
    )

    class Meta:
        model = Category
        fields = ['id', 'company', 'name', 'parent_category', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        validators = []  # UniqueTogetherValidatorを無効化

    def validate(self, data):
        """
        複合バリデーション
        - 親カテゴリは同じ会社のカテゴリのみ指定可能
        - 循環参照の防止
        - 同じ会社内での名前の重複チェック
        """
        company = data.get('company')
        parent_category = data.get('parent_category')
        name = data.get('name')

        # 親カテゴリの会社チェック
        if parent_category and parent_category.company != company:
            raise serializers.ValidationError({
                "parent_category": "親カテゴリは同じ会社のカテゴリのみ指定できます"
            })

        # 循環参照チェック（更新時のみ）
        if parent_category and self.instance:
            current = parent_category
            while current:
                if current.id == self.instance.id:
                    raise serializers.ValidationError({
                        "parent_category": "カテゴリの参照が循環しています"
                    })
                current = current.parent_category

        # 同じ会社内での名前の重複チェック
        if name and company:
            existing = Category.objects.filter(company=company, name=name)
            if self.instance:
                existing = existing.exclude(id=self.instance.id)
            if existing.exists():
                raise serializers.ValidationError({
                    "name": "同じ会社内で同じ名前のカテゴリは作成できません"
                })

        return data

    def to_representation(self, instance):
        """
        シリアライズ時のデータ変換
        - UUIDオブジェクトを文字列に変換
        """
        data = super().to_representation(instance)
        data['company'] = str(instance.company.id)
        if instance.parent_category:
            data['parent_category'] = str(instance.parent_category.id)
        return data