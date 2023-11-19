from rest_framework import serializers

from ..models.company import Company


class CompanyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ("id",
                  "name")


class CompanyRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"


class CompanyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ("id",
                  "name")
        read_only_fields = ("id",)
