from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.models import Category


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
        # Meta.constraints の UniqueConstraint は ModelSerializer が自動でバリデータに
        # 変換しない(自動変換の対象は Meta.unique_together のみ)。明示しないと重複登録が
        # DBのIntegrityErrorとなり400ではなく500を返すため、ここで宣言する。
        validators = [
            UniqueTogetherValidator(
                queryset=Category.objects.all(),
                fields=["company", "name"],
                message="同一企業内に同じ名前のカテゴリは登録できません。",
            )
        ]

    def validate(self, attrs):
        # 所属企業の変更を許すと、子カテゴリが旧企業に取り残されて企業を跨いだ親子関係が
        # できてしまう。カテゴリを別企業へ移すのは子孫の付け替えを伴う操作であり、
        # 単一フィールドの更新で行うべきではないため、作成後は変更不可とする。
        if self.instance is not None and "company" in attrs and attrs["company"].pk != self.instance.company_id:
            raise serializers.ValidationError({"company": "カテゴリが属する企業は変更できません。"})

        # PATCHでは未送信の項目がattrsに含まれないため、既存値で補ってから検証する。
        company = attrs.get("company", getattr(self.instance, "company", None))
        parent_category = attrs.get("parent_category", getattr(self.instance, "parent_category", None))

        if parent_category is not None:
            self._validate_parent_category(parent_category, company)

        return attrs

    def _validate_parent_category(self, parent_category, company):
        """親カテゴリが同一企業のものであり、かつ循環参照にならないことを検証する。"""
        if company is not None and parent_category.company_id != company.pk:
            raise serializers.ValidationError(
                {"parent_category": "親カテゴリには同じ企業のカテゴリのみ指定できます。"}
            )

        if self.instance is None:
            # 新規作成時は自分自身がまだ存在しないため、循環参照は起こり得ない。
            return

        # 親を根までたどり、自分自身が現れたら循環参照となる。
        # 既存データが循環している場合に無限ループしないよう、訪問済みidを記録する。
        visited = set()
        ancestor = parent_category
        while ancestor is not None and ancestor.pk not in visited:
            if ancestor.pk == self.instance.pk:
                raise serializers.ValidationError(
                    {"parent_category": "自分自身または子孫カテゴリを親カテゴリに指定することはできません。"}
                )
            visited.add(ancestor.pk)
            ancestor = ancestor.parent_category
