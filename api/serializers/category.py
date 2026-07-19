from rest_framework import serializers

from api.models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "company", "name", "parent_category", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        company = attrs.get("company", getattr(self.instance, "company", None))
        name = attrs.get("name", getattr(self.instance, "name", None))
        parent_category = attrs.get("parent_category", getattr(self.instance, "parent_category", None))

        if "\x00" in name:
            raise serializers.ValidationError({"name": "NUL文字は使用できません。"})

        duplicate_categories = Category.objects.filter(company=company, name=name)
        if self.instance is not None:
            duplicate_categories = duplicate_categories.exclude(id=self.instance.id)
        if duplicate_categories.exists():
            raise serializers.ValidationError({"non_field_errors": "同じ企業内に同名のカテゴリは作成できません。"})

        if parent_category is None:
            return attrs

        if parent_category.company_id != company.id:
            raise serializers.ValidationError({"parent_category": "親カテゴリは同じ企業に属している必要があります。"})

        if self.instance is None:
            return attrs

        current_category = parent_category
        while current_category is not None:
            if current_category.id == self.instance.id:
                raise serializers.ValidationError({"parent_category": "親カテゴリに自分自身または子孫は指定できません。"})
            current_category = current_category.parent_category

        return attrs
