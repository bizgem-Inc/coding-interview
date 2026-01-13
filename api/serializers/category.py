from rest_framework import serializers

from api.models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "parent_category",
            "company",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        if instance.parent_category is not None:
            rep["parent_category"] = {
                "id": instance.parent_category.id,
                "name": instance.parent_category.name,
            }
        rep["company"] = {"id": instance.company.id, "name": instance.company.name}
        return rep

    def validate(self, data):
        company = data.get("company", getattr(self.instance, "company", None))
        parent = data.get("parent_category")

        if parent:
            if company and parent.company_id != (
                company.id if hasattr(company, "id") else company.id
            ):
                raise serializers.ValidationError(
                    {
                        "parent_category": "親Categoryと同じCompanyに属している必要があります。"
                    }
                )
            if self.instance and parent.id == self.instance.id:
                raise serializers.ValidationError(
                    {
                        "parent_category": "カテゴリは自分自身を親にすることはできません。"
                    }
                )
        return data

    def validate_company(self, value):
        if self.instance and value and self.instance.company_id != value.id:
            raise serializers.ValidationError("Companyは編集出来ません")
        return value
