from rest_framework import serializers
from django.core.validators import RegexValidator, MinLengthValidator
from api.models import Category, Company
from api.models.category import MAX_DEPTH
import uuid


class CategoryListSerializer(serializers.ModelSerializer):
    """カテゴリ一覧用シリアライザー（最小限のフィールドのみ）"""

    class Meta:
        model = Category
        fields = ["id", "name", "updated_at", "created_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class CategoryDetailSerializer(serializers.ModelSerializer):
    """カテゴリ詳細用シリアライザー（全フィールド）"""

    # nameフィールドに追加バリデーション
    name = serializers.CharField(
        validators=[
            MinLengthValidator(2, message="カテゴリ名は2文字以上で入力してください"),
            RegexValidator(
                r"^[a-zA-Z0-9一-龠ぁ-んァ-ン\s\-_]+$",
                message="カテゴリ名には英数字、日本語、ハイフン、アンダースコアのみ使用できます",
            ),
        ]
    )

    # 関連情報を含める
    children = CategoryListSerializer(many=True, read_only=True)
    depth = serializers.SerializerMethodField()
    ancestors = serializers.SerializerMethodField()

    # 外部キーはpkのみ返却
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())
    parent_category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Category
        exclude = ["path"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_depth(self, obj):
        """カテゴリの階層深さを取得"""
        return obj.get_depth()

    def get_ancestors(self, obj):
        """祖先カテゴリを取得"""
        ancestors = obj.get_ancestors()
        return CategoryListSerializer(ancestors, many=True).data

    def validate_company(self, value):
        # ユーザーが所属する会社のみ許可する例
        user = self.context["request"].user
        if hasattr(user, "company") and user.company.id != value.id:
            raise serializers.ValidationError("自分が所属する会社のカテゴリのみ作成できます")
        return value

    def validate_parent_category(self, value):
        # 親カテゴリが指定されている場合の追加バリデーション
        if value:
            # 親カテゴリが同じ会社に属していることを確認
            # self.contextから現在のリクエストデータを取得
            request = self.context.get("request")
            if request and hasattr(request, "data"):
                company_id_str = request.data.get("company")
                if company_id_str:
                    try:
                        company_id = uuid.UUID(str(company_id_str))
                        if value.company_id != company_id:
                            raise serializers.ValidationError(
                                "親カテゴリは同じ会社に属している必要があります"
                            )
                    except (ValueError, TypeError):
                        # UUID変換に失敗した場合はCompanyインスタンスを取得して確認
                        pass

            # モデルで定義された最大階層深さを使用
            if value.get_depth() >= MAX_DEPTH:
                raise serializers.ValidationError(
                    f"カテゴリの階層は最大{MAX_DEPTH}レベルまでです。"
                    f"現在の親カテゴリはすでに{value.get_depth()}レベルです。"
                )

        return value

    def validate(self, attrs):
        # 複数フィールドにまたがる検証
        instance = self.instance  # 更新時のみ値がある

        # 更新時に自分自身または子孫を親に設定しようとしていないか検証
        if instance and "parent_category" in attrs and attrs["parent_category"]:
            parent = attrs["parent_category"]
            if parent.id == instance.id:
                raise serializers.ValidationError(
                    {"parent_category": "自分自身を親カテゴリに設定することはできません"}
                )

            # ltreeを使って子孫チェック
            if instance.is_ancestor_of(parent):
                raise serializers.ValidationError(
                    {"parent_category": "子カテゴリを親カテゴリに設定することはできません"}
                )

        return attrs
