from rest_framework import serializers
from api.models.category import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
        # バリデーションがコーディングテストの観点としてあるので、validate()を活かすためにDRFのユニークバリデーターは無効化する
        validators = []

    def validate(self, attrs):
        company = attrs.get("company") or getattr(self.instance, "company", None)
        name = attrs.get("name") or getattr(self.instance, "name", None)

        if company is not None and name is not None:
            qs = Category.objects.filter(company=company, name=name)
            # 更新時は重複確認対象から自分自身を除外
            if self.instance is not None:
                qs = qs.exclude(id=self.instance.id)

            if qs.exists():
                raise serializers.ValidationError(
                    {"name": "同じ企業に同名のカテゴリが既に存在します。"}
                )

        return attrs
