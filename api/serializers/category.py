from rest_framework import serializers
from api.models.category import Category
# from api.models.company import Company

class CategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields='__all__' # 全項目
        # fields = ['id','company','name','parent_category','created_at','updated_at',]