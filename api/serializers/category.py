from rest_framework import serializers
from django.db import IntegrityError
from ..models import Category, Company


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
       model = Company
       fields = '__all__'

class ParentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'created_at', 'updated_at']

class CategorySerializer(serializers.ModelSerializer):
    # create、update時にはparent_category_id, company_idを指定してもらう想定
    parent_category = ParentCategorySerializer(read_only=True)
    parent_category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.filter(), write_only=True, allow_null=True, required=False)
    company = CompanySerializer(read_only=True)
    company_id = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), write_only=True)

    def validate_parent_category_id(self, value):
        if value is not None:
            # とりあえず親子間の階層のみに限定
            if value.parent_category is not None:
                raise serializers.ValidationError("parent_category is invalid.")
            # 自身のidをparent_category_idに設定も不可
            if self.instance is not None and self.instance.id == value.id:
                raise serializers.ValidationError("can not set self.id to parent_category_id.")
        return value

    def create(self, validated_data):
        validated_data['company'] = validated_data.get('company_id')
        del validated_data['company_id']

        if 'parent_category_id' in validated_data:
            validated_data['parent_category'] = validated_data.get('parent_category_id', None)
            del validated_data['parent_category_id']

        try:
            return Category.objects.create(**validated_data)
        except IntegrityError as e:
            # uniqueフィールドの重複エラーは400エラーとする
            raise serializers.ValidationError(str(e))

    def update(self, instance, validated_data):
        if 'company_id' in validated_data:
            validated_data['company'] = validated_data.get('company_id')
            del validated_data['company_id']

        if 'parent_category_id' in validated_data:
            validated_data['parent_category'] = validated_data.get('parent_category_id', None)
            del validated_data['parent_category_id']

        try:
            return super().update(instance, validated_data)
        except IntegrityError as e:
            raise serializers.ValidationError(str(e))

    class Meta:
        model = Category
        fields = '__all__'
