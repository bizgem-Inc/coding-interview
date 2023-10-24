from rest_framework import serializers
from ..models.category import Category
from ..models.company import Company

class ApiCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('id','name')

class ApiParentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id','name')

class ApiCategorySerializer(serializers.ModelSerializer):
    company = ApiCompanySerializer()
    parent_category = ApiParentCategorySerializer(required=False, allow_null=True)
    class Meta:
        model = Category
        fields = ('id', 'company', 'name', 'parent_category', 'created_at', 'updated_at')

    def create(self, validated_data):
        company = Company.objects.get(name=validated_data["company"]["name"])
        if 'parent_category' in validated_data:
            if validated_data["parent_category"] is None:
                parent_category = None
            else:
                parent_category = Category.objects.get(name=validated_data["parent_category"]["name"])
        else:
            parent_category = None    
        return Category.objects.create(
            name = validated_data["name"],
            company = company,
            parent_category = parent_category
        )

    def update(self, instance, validated_data):
        company = Company.objects.get(name=validated_data["company"]["name"])
        instance.name = validated_data["name"]
        instance.company = company
        if 'parent_category' in validated_data:
            if validated_data["parent_category"] is not None:
                instance.parent_category = Category.objects.get(name=validated_data["parent_category"]["name"])
            else:
                instance.parent_category = None
        else:
            instance.parent_category = None
        instance.save()
        return instance
