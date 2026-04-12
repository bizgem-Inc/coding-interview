from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from api.models.category import Category


class CategorySimpleSerializer(serializers.ModelSerializer):
    """
    IDと名前のみの簡略化されたシリアライザ。
    詳細表示時の親カテゴリや子カテゴリリストの表示に使用します。
    """
    class Meta:
        model = Category
        fields = ["id", "name"]


class CategoryListSerializer(serializers.ModelSerializer):
    """
    管理画面のテーブル表示やドリルダウンUIを想定した構成。
    children_count により、フロントエンド側で「展開可能か（子があるか）」を判定できます。
    """
    children_count = serializers.IntegerField(read_only=True)
    parent_category = CategorySimpleSerializer(read_only=True)

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "parent_category",
            "children_count",
            "created_at",
            "updated_at",
        ]


class CategoryDetailSerializer(CategoryListSerializer):
    """
    基本情報に加え、親カテゴリの情報と直下の子カテゴリリストを含めます。
    これにより、詳細画面から一階層下への遷移やパンくずリストの構築を支援します。
    """
    parent_category = CategorySimpleSerializer(read_only=True)
    children = CategorySimpleSerializer(many=True, read_only=True)

    class Meta(CategoryListSerializer.Meta):
        fields = CategoryListSerializer.Meta.fields + ["children"]


class CategoryWriteSerializer(serializers.ModelSerializer):
    """
    作成・更新用: データの不整合を防ぐためのバリデーションを実装。
    """
    company = serializers.HiddenField(default=None)

    class Meta:
        model = Category
        fields = ["id", "name", "parent_category", "company"]
        validators = [
            UniqueTogetherValidator(
                queryset=Category.objects.all(),
                fields=['company', 'name'],
                message="既に同名のカテゴリが存在します。"
            )
        ]

    def to_internal_value(self, data):
        """
        リクエストデータを内部形式（attrs）に変換する過程で company を注入します。
        これにより UniqueTogetherValidator が確実に company オブジェクトを参照できます。
        """
        ret = super().to_internal_value(data)

        # context から company を取得し、内部データにセット
        company = self.context.get('company')
        if company is None:
            raise serializers.ValidationError({"company": "企業情報が取得できませんでした。"})
        ret['company'] = company

        return ret

    def validate_parent_category(self, value):
        """親カテゴリに関する整合性チェック"""

        # 更新時は親カテゴリの変更をブロック
        # NOTE:
        # 将来的な拡張性について
        # 「既存カテゴリの親を任意に変更（移動）できる機能」を本格的に提供する場合や、多階層かつ大規模なツリーを扱う場合は、DB負荷を抑えつつ一括検知が可能なRecursive CTE 等を用いたバリデーションの追加により自己参照、循環参照の防止を検討します。
        if self.instance:
            raise serializers.ValidationError(
                "親カテゴリの変更は未サポートのため削除後に再作成してください。"
            )

        # 新規作成時のチェック
        if value is None:
            return value

        # 同一企業スコープのチェック
        # ViewSetの get_serializer_context から渡された company を使用
        company = self.context.get("company")
        if value.company != company:
            raise serializers.ValidationError(
                "指定された親カテゴリは同一企業に属していません。"
            )

        return value
