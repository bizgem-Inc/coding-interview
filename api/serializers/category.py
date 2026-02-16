from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from ..models.category import Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            'id', 'company', 'name', 'parent_category', 
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
        
        # モデルのUniqueConstraintをDRF側でも明示的にバリデーションエラーとして扱う設定
        validators = [
            UniqueTogetherValidator(
                queryset=Category.objects.all(),
                fields=['company', 'name'],
                message="この会社では既に同じ名前のカテゴリが存在します。"
            )
        ]

    def validate(self, data):
        """
        フィールド単体では判定できない、複数フィールドにまたがる検証や
        ロジック上の矛盾（循環参照など）をチェックします。
        """
        # 更新時、自分自身を親カテゴリに設定しようとしていないかチェック
        if self.instance:
            # parent_category がリクエストに含まれている場合のみチェック
            parent = data.get('parent_category')
            if parent and parent.id == self.instance.id:
                raise serializers.ValidationError(
                    {"parent_category": "自分自身を親カテゴリに設定することはできません。"}
                )
        
        return data