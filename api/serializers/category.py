from django.conf import settings
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from api.models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'company', 'parent_category', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        validators = [
            UniqueTogetherValidator(
                queryset=Category.objects.all(),
                fields=['company', 'name'],
                message='この企業には既に同じ名前のカテゴリが存在します。'
            )
        ]
    
    def validate_name(self, value):
        """カテゴリ名のバリデーション"""
        max_length = getattr(settings, 'CATEGORY_NAME_MAX_LENGTH', 255)
        if len(value) > max_length:
            raise serializers.ValidationError(f'カテゴリ名は{max_length}文字以内で入力してください。')
        return value
    
    def validate_parent_category(self, value):
        """親カテゴリのバリデーション"""
        if value:
            # 自分自身を親に設定できない（更新時のみ）
            if self.instance and value.id == self.instance.id:
                raise serializers.ValidationError('自分自身を親カテゴリに設定することはできません。')
            
            # 作成時のcompanyと親カテゴリのcompanyが一致するか確認
            if 'company' in self.initial_data:
                company_id = self.initial_data['company']
                if str(value.company.id) != company_id:
                    raise serializers.ValidationError('親カテゴリは同じ企業のカテゴリである必要があります。')
            
            # 階層の深さをチェック
            max_depth = getattr(settings, 'CATEGORY_MAX_DEPTH', 3)
            
            # 更新時は子孫を含めた階層をチェック
            if self.instance:
                # 新しい親の深さ + 自分の子孫の深さ + 1（自分自身）
                new_total_depth = self.get_depth(value) + self.get_max_descendant_depth(self.instance) + 2
                if new_total_depth > max_depth:
                    raise serializers.ValidationError(
                        f'この変更により階層が{new_total_depth}階層となり、'
                        f'最大階層数（{max_depth}階層）を超えてしまいます。'
                    )
            else:
                # 作成時は親の深さのみチェック
                if self.get_depth(value) >= max_depth - 1:
                    raise serializers.ValidationError(f'カテゴリの階層は{max_depth}階層までです。')
        
        return value
    
    def get_depth(self, category):
        """カテゴリの階層の深さを取得"""
        depth = 0
        current = category
        while current.parent_category:
            depth += 1
            current = current.parent_category
            # 無限ループ防止
            if depth > 10:
                break
        return depth
    
    def get_max_descendant_depth(self, category):
        """カテゴリの子孫の最大深さを取得"""
        from api.models import Category
        
        def get_descendants_depth(cat, current_depth=0):
            max_depth = current_depth
            children = Category.objects.filter(parent_category=cat)
            for child in children:
                child_depth = get_descendants_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
            return max_depth
        
        return get_descendants_depth(category)