from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
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
        API特有のバリデーション
        - モデルのバリデーションを実行
        - API特有のエラーメッセージにマッピング
        """
        instance = self.instance or Category()
        for key, value in data.items():
            setattr(instance, key, value)

        try:
            instance.clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)

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
