from rest_framework import serializers
from api.models.category import Category
from rest_framework.validators import UniqueTogetherValidator


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "company", "name", "parent_category", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
        validators = [
            UniqueTogetherValidator(
                queryset=Category.objects.all(),
                fields=["company", "name"],
                message="同じ企業内に同名のカテゴリが既に存在します。",
            )
        ]
        
    def validate(self, attrs): #バリデーション
            # PATCH（部分更新）も考慮し、attrs に無ければ既存値を見る
            company = attrs.get("company") or getattr(self.instance, "company", None)
            parent = attrs.get("parent_category")

            # ① 親の同一company検証
            if parent is not None and parent.company != company:
                raise serializers.ValidationError(
                    {"parent_category": "親カテゴリは同じ企業に属している必要があります。"}
                )

            # ② 自己参照の禁止
            if self.instance is not None and parent is not None and self.instance.id == parent.id:
                raise serializers.ValidationError(
                    {"parent_category": "自分自身を親カテゴリに指定できません。"}
                )

            return attrs