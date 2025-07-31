from rest_framework import serializers

from ..models.category import Category


class CategoryModelSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255, error_messages={
        "max_length": "255文字以内で入力してください"
    })
    parent_category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        required=False,
        allow_null=True
    )

    def validate_name(self, value):
        instance = self.instance or Category()
        if Category.objects.filter(name=value, company_id=self.context["company_id"]).exclude(id=instance.id).exists():
            raise serializers.ValidationError("同名のカテゴリが存在します")
        return value

    def validate_parent_category(self, value):
        parent_category = Category.objects.filter(pk=value.id).first()
        if not parent_category or parent_category.company_id != self.context["company_id"]:
            # 他社のUUIDを当てる確立は限りなく低いので、エラーメッセージはあまりひねったものでなくて良さそう
            raise serializers.ValidationError("不正なカテゴリです")
        return value

    class Meta:
        model = Category
        exclude = ("company",)