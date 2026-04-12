from rest_framework import serializers

from api.models.category import Category
from api.models.company import Company


class CategorySerializer(serializers.ModelSerializer):
    # （ここでは）ポリシーとして、Modelのエラーメッセージを出さず、Serializer側で明示的にエラーメッセージを定義することにする
    # DRF3.14以前ではextra_kwargsやModelのValidationにて拾いきれない場合があるので、フィールド定義を明示的に行う
    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(),
        error_messages={
            "required": "企業は必須です。",
            "null": "企業は必須です。",
            "does_not_exist": "指定された企業が見つかりません。",
            "incorrect_type": "指定された企業が見つかりません。"
        }
    )

    name = serializers.CharField(
        max_length=255,
        required=True, # 明示的に必須を宣言
        error_messages={
            "required": "名前は必須です。",
            "blank": "名前は必須です。",
            "max_length": "入力は255文字以内で入力してください。"
        }
    )

    parent_category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), 
        allow_null=True, 
        required=False
    )

    class Meta:
        model = Category
        fields = ["id", "company", "name", "parent_category", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        """
         バリデーション
           ・同名のカテゴリが同じ企業に存在しないこと
           ・親カテゴリが同じ企業に属していること
           ・親カテゴリに自分自身を指定していないこと
        """
        company = attrs.get("company", getattr(self.instance, "company", None))
        parent_category = attrs.get("parent_category")
        name = attrs.get("name")

        if name and company:
            # DBの制約と同じ条件で検索
            exists = Category.objects.filter(name=name, company=company)
            
            # 更新（PUT/PATCH）の場合は自分自身を除外
            if self.instance:
                exists = exists.exclude(pk=self.instance.pk)
                
            if exists.exists():
                raise serializers.ValidationError(
                    "この会社には既に同じ名前のカテゴリーが存在します。"
                )
        if parent_category is not None:
            # 親カテゴリが同じ企業に属していること
            if company is not None and parent_category.company_id != company.id:
                raise serializers.ValidationError(
                    {"parent_category": "親カテゴリーは同じ会社に所属している必要があります。"}
                )

            # 親カテゴリに自分自身を指定していないかチェック
            if self.instance and parent_category.id == self.instance.id:
                raise serializers.ValidationError(
                    {"parent_category": "自身のカテゴリーを親に指定することはできません。"}
                )

        return attrs
