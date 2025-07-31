from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField, ValidationError

from ..models.category import Category


class CategoryModelSerializer(ModelSerializer):
    parent_category = PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        required=False,
        allow_null=True
    )

    def validate_parent_category(self, value):
        parent_category = Category.objects.filter(pk=value.id).first()
        if not parent_category or parent_category.company_id != self.context["company_id"]:
            # 他社のUUIDを当てる確立は限りなく低いので、エラーメッセージはあまりひねったものでなくて良さそう
            raise ValidationError("不正なカテゴリです")
        return value

    class Meta:
        model = Category
        exclude = ("company",)