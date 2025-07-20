from rest_framework import serializers

from api.models.category import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "company",
            "name",
            "parent_category",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, data):
        parent_category = data.get('parent_category')
        company = data.get('company')
        name = data.get('name')

        # 既存インスタンスがある場合（更新時）、不足データを補完
        if self.instance:
            if company is None:
                company = self.instance.company
            if name is None:
                name = self.instance.name

        # 自己参照ループの防止
        if parent_category and self.instance:
            if parent_category.id == self.instance.id:
                raise serializers.ValidationError({
                    "parent_category": "カテゴリは自分自身を親カテゴリにすることはできません"
                })

            # 循環参照の防止（親の親...が自分自身を指していないかチェック）
            # 訪問済みIDセットで循環検出（無限ループ防止）
            visited_ids = set()
            current_parent = parent_category
            while current_parent:
                if current_parent.id in visited_ids:
                    # 既存の循環参照を検出（自分以外での循環）
                    break
                if current_parent.id == self.instance.id:
                    raise serializers.ValidationError({
                        "parent_category": "循環参照は許可されていません"
                    })
                visited_ids.add(current_parent.id)
                current_parent = current_parent.parent_category

        # 親カテゴリが同じ企業に属していることをチェック
        if parent_category and company:
            if parent_category.company != company:
                raise serializers.ValidationError({
                    "parent_category": "親カテゴリは同じ企業に属している必要があります"
                })

        if name and company:
            existing_query = Category.objects.select_related('company').filter(company=company, name=name)
            if self.instance:
                existing_query = existing_query.exclude(id=self.instance.id)
            if existing_query.exists():
                raise serializers.ValidationError({
                    "name": "同じ企業内に同じ名前のカテゴリが既に存在します"
                })

        return data