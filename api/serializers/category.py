from rest_framework import serializers

from api.models.category import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

    def validate_name(self, value):
        """名前の空白のみの登録を防ぐ"""
        if not value or not value.strip():
            raise serializers.ValidationError("名前を空白にすることはできません。")
        return value.strip()

    def validate(self, attrs):
        instance = self.instance
        # PATCHなどで送信されていないフィールドは既存の値を参照する
        company = attrs.get("company", instance.company if instance else None)
        parent_category = attrs.get("parent_category", instance.parent_category if instance else None)

        if parent_category:
            # 1. 親カテゴリが別企業に属している場合はエラー
            if parent_category.company != company:
                raise serializers.ValidationError({"parent_category": "親カテゴリは同じ企業に属している必要があります。"})

            # 2. 自分自身を親カテゴリに設定することは不可
            if instance and parent_category == instance:
                raise serializers.ValidationError({"parent_category": "自身を親カテゴリに設定することはできません。"})

            # 3. 循環参照の防止（親の親...をたどって自分がいないかチェック）
            if instance:
                current = parent_category
                while current:
                    if current == instance:
                        raise serializers.ValidationError({"parent_category": "子孫カテゴリを親に設定することはできません（循環参照）。"})
                    current = current.parent_category

        # 4. 子が存在する場合の企業(Company)変更を禁止
        if instance and company != instance.company:
            # related_name="+" のため逆参照は明示的にクエリを発行する
            if Category.objects.filter(parent_category=instance).exists():
                raise serializers.ValidationError({"company": "子カテゴリが存在するため、企業を変更できません。"})

        # 5. 同一企業内でのカテゴリ名の重複チェック (PATCH対応用)
        name = attrs.get("name", instance.name if instance else None)
        if company and name:
            query = Category.objects.filter(company=company, name=name)
            if instance:
                query = query.exclude(pk=instance.pk)
            if query.exists():
                raise serializers.ValidationError({"name": "同じ企業内に同名のカテゴリが既に存在します。"})

        return attrs
