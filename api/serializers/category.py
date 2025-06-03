from rest_framework import serializers
from api.models.category import Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'company', 'name', 'parent_category', 'created_at', 'updated_at']

    def validate(self, attrs):
        company = attrs.get('company')
        name = attrs.get('name')
        instance = getattr(self, 'instance', None)

        if instance:
            if instance.company == company and instance.name == name:
                return attrs

        qs = Category.objects.filter(company=company, name=name)
        if instance:
            qs = qs.exclude(pk=instance.pk)

        if qs.exists():
            raise serializers.ValidationError("同じ企業内に同じカテゴリ名が既に存在します。")

        return attrs
