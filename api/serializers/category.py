from rest_framework import serializers
from django.db import IntegrityError
from ..models.category import Category


class CategorySerializer(serializers.ModelSerializer):
    """カテゴリのシリアライザー"""

    class Meta:
        model = Category
        fields = [
            "id",
            "company",
            "name",
            "parent_category",
            "created_at",
            "updated_at"
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at"
        ]
        
    def validate_parent_category(self, value):
        """親カテゴリのバリデーション"""
        if value:
            # 自分自身を親カテゴリに設定してないかチェック
            if self.instance and value.id == self.instance.id:
                raise serializers.ValidationError("自分自身を親カテゴリに設定することはできません。")

            # 循環参照のチェック
            if self.instance:
                current = value
                while current:
                    if current.id == self.instance.id:
                        raise serializers.ValidationError("循環参照が発生します。この親カテゴリは設定できません。")
                    current = current.parent_category

        return value

    def validate(self, attrs):
        """複合バリデーション"""
        name = attrs.get("name")
        company = attrs.get("company")
        parent_category = attrs.get("parent_category")

        # 更新する値がなく、登録済みの場合はインスタンスから取得する
        if self.instance:
            name = attrs.get("name", self.instance.name)
            company = attrs.get("company", self.instance.company)

        # 親カテゴリが指定されている場合、同じ企業に属しているかチェック
        if parent_category and company:
            if parent_category.company.id != company.id:
                raise serializers.ValidationError({
                    "parent_category": "親カテゴリは同じ企業に属している必要があります。"
                })

        # 企業とカテゴリ名の組み合わせがユニークかチェック（新規作成時）
        queryset = Category.objects.filter(company=company, name=name)
        if self.instance:
            # 更新時
            queryset = queryset.exclude(id=self.instance.id)

        if queryset.exists():
            raise serializers.ValidationError({
                "name": "この企業には既に同じ名前のカテゴリが存在します。"
            })

        return attrs
