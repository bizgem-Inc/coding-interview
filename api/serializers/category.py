from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.models.category import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "company", "name", "parent_category", "created_at", "updated_at"]
        # DRF 3.14 は UniqueConstraint からバリデータを自動生成しないため明示する。
        # 無いと重複時に DB の IntegrityError となり 500 が返る。
        validators = [
            UniqueTogetherValidator(
                queryset=Category.objects.all(),
                fields=["company", "name"],
                message="同じ企業内に同じ名前のカテゴリが既に存在します。",
            )
        ]

    def validate_company(self, value):
        # 作成後に企業を変えると、子カテゴリとの間で企業がずれるため変更を禁止する
        if self.instance is not None and value != self.instance.company:
            raise serializers.ValidationError("作成後に企業を変更することはできません。")
        return value

    def validate_parent_category(self, value):
        # 自分自身や子孫を親にすると親子関係が循環するため禁止する。
        # 指定された親から上にたどり、自分に行き着いたら循環になる。
        if self.instance is None or value is None:
            return value
        visited = set()
        node = value
        while node is not None and node.pk not in visited:
            if node.pk == self.instance.pk:
                raise serializers.ValidationError("自分自身または子孫のカテゴリを親に指定することはできません。")
            visited.add(node.pk)
            node = node.parent_category
        return value

    def validate(self, attrs):
        # 親カテゴリは同じ企業のものに限る
        company = attrs.get("company", getattr(self.instance, "company", None))
        parent = attrs.get("parent_category")
        if parent is not None and parent.company_id != company.pk:
            raise serializers.ValidationError({"parent_category": "別の企業のカテゴリを親に指定することはできません。"})
        return attrs
