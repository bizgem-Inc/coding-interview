from rest_framework import serializers

from api.models.category import Category
from api.models.company import Company


class CategorySerializer(serializers.ModelSerializer):
	company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())
	parent_category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), allow_null=True, required=False)

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
