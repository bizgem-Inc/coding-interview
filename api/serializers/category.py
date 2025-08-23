# Author: abe
# Date: 2025-08-23
# Description: Category API serializers for coding interview

from rest_framework import serializers
from api.models.category import Category
from api.models.company import Company


class CategoryListSerializer(serializers.ModelSerializer):
    """カテゴリ一覧・詳細取得用シリアライザー"""
    company_name = serializers.CharField(source='company.name', read_only=True)
    parent_category_name = serializers.CharField(source='parent_category.name', read_only=True)
    
    class Meta:
        model = Category
        fields = [
            'id', 'company', 'company_name', 'name', 
            'parent_category', 'parent_category_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CategoryCreateUpdateSerializer(serializers.ModelSerializer):
    """カテゴリ作成・更新用シリアライザー"""
    
    class Meta:
        model = Category
        fields = ['company', 'name', 'parent_category']
    
    def validate_parent_category(self, value):
        if value is not None:
            # 親カテゴリが同じ企業に属しているかチェック
            company = self.initial_data.get('company')
            if company and str(value.company.pk) != str(company):
                raise serializers.ValidationError("Parent category must belong to the same company.")
        return value
    
    def validate(self, data):
        company = data.get('company')
        name = data.get('name')
        instance = getattr(self, 'instance', None)
        
        if company and name:
            # 同じ企業内での名前重複チェック
            existing_category = Category.objects.filter(
                company=company, 
                name=name
            ).exclude(id=instance.id if instance else None).first()
            
            if existing_category:
                raise serializers.ValidationError(
                    f"Category name '{name}' already exists in this company."
                )
        
        return data
