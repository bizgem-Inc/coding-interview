from django.db import IntegrityError, transaction
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.validators import UniqueTogetherValidator

from api.models import Category, Company


class CategorySerializer(serializers.ModelSerializer):
    """CategoryモデルとAPIで送受信するデータを相互変換する。"""

    class Meta:
        model = Category
        fields = (
            "id",
            "company",
            "name",
            "parent_category",
            "created_at",
            "updated_at",
        )
        # UUIDと日時はDjangoが自動設定するため、APIからは変更させない。
        read_only_fields = ("id", "created_at", "updated_at")
        # DB制約違反になる前に、同一企業内のカテゴリ名重複を400で返す。
        validators = [
            UniqueTogetherValidator(
                queryset=Category.objects.all(),
                fields=("company", "name"),
            )
        ]

    def validate(self, attrs):
        # 作成・部分更新のどちらでも、更新後に有効になる企業と親を使って検証する。
        company = attrs.get("company", getattr(self.instance, "company", None))
        parent = attrs.get(
            "parent_category",
            getattr(self.instance, "parent_category", None),
        )
        self._validate_hierarchy(company, parent, self.instance)
        return attrs

    def _validate_hierarchy(self, company, parent, instance):
        # 親子関係が同一企業内にあり、自己参照や循環参照を含まないことを確認する。
        if parent is not None:
            if parent.company_id != company.id:
                raise serializers.ValidationError(
                    {"parent_category": "親カテゴリは同じ企業に所属している必要があります。"}
                )

            # 親を順にたどり、自分自身への参照と既存の循環参照を防ぐ。
            visited_ids = set()
            ancestor = parent
            while ancestor is not None:
                if instance is not None and ancestor.id == instance.id:
                    raise serializers.ValidationError(
                        {"parent_category": "カテゴリを循環参照させることはできません。"}
                    )
                if ancestor.id in visited_ids:
                    raise serializers.ValidationError(
                        {"parent_category": "カテゴリを循環参照させることはできません。"}
                    )
                visited_ids.add(ancestor.id)
                ancestor = ancestor.parent_category

        if (
            instance is not None
            and company.id != instance.company_id
            and Category.objects.filter(parent_category=instance)
            .exclude(company=company)
            .exists()
        ):
            raise serializers.ValidationError(
                {"company": "子カテゴリと異なる企業へ変更することはできません。"}
            )

    def create(self, validated_data):
        # 親を設定する場合だけ階層変更を直列化し、保存直前の状態で再検証する。
        try:
            with transaction.atomic():
                company = validated_data["company"]
                parent = validated_data.get("parent_category")
                if parent is not None:
                    locked_companies = self._lock_companies(
                        {company.id, parent.company_id}
                    )
                    company = locked_companies.get(company.id)
                    if company is None:
                        raise serializers.ValidationError(
                            {"company": "指定された企業は存在しません。"}
                        )

                    parent = (
                        Category.objects.select_for_update()
                        .filter(id=parent.id)
                        .first()
                    )
                    if parent is None:
                        raise serializers.ValidationError(
                            {"parent_category": "指定された親カテゴリは存在しません。"}
                        )

                    self._validate_hierarchy(company, parent, instance=None)
                    validated_data = dict(validated_data)
                    validated_data["company"] = company
                    validated_data["parent_category"] = parent
                return super().create(validated_data)
        except IntegrityError as error:
            validation_error = self._integrity_validation_error(error)
            if validation_error is not None:
                raise validation_error from error
            raise

    def update(self, instance, validated_data):
        # 通常更新は対象行だけをロックし、階層変更時だけ企業単位で直列化する。
        try:
            with transaction.atomic():
                requested_company = validated_data.get("company")
                hierarchy_change = "parent_category" in validated_data or (
                    requested_company is not None
                    and requested_company.id != instance.company_id
                )

                if hierarchy_change:
                    company_ids = {instance.company_id}
                    if requested_company is not None:
                        company_ids.add(requested_company.id)
                    requested_parent = validated_data.get("parent_category")
                    if requested_parent is not None:
                        company_ids.add(requested_parent.company_id)
                    locked_companies = self._lock_companies(company_ids)

                parent = None
                if hierarchy_change and requested_parent is not None:
                    # 親を先にロックし、親の同時削除とのデッドロックを避ける。
                    parent = (
                        Category.objects.select_for_update()
                        .filter(id=requested_parent.id)
                        .first()
                    )
                    if parent is None:
                        raise serializers.ValidationError(
                            {
                                "parent_category": (
                                    "指定された親カテゴリは存在しません。"
                                )
                            }
                        )

                locked_instance = (
                    Category.objects.select_for_update()
                    .filter(id=instance.id)
                    .first()
                )

                if locked_instance is None:
                    raise NotFound("更新対象のカテゴリは存在しません。")

                if hierarchy_change:
                    company_id = (
                        requested_company.id
                        if requested_company is not None
                        else locked_instance.company_id
                    )
                    company = locked_companies.get(company_id)
                    if company is None:
                        raise serializers.ValidationError(
                            {"company": "指定された企業は存在しません。"}
                        )

                    if "parent_category" in validated_data:
                        parent = parent if requested_parent is not None else None
                    else:
                        parent = locked_instance.parent_category

                    self._validate_hierarchy(company, parent, locked_instance)
                    validated_data = dict(validated_data)
                    if requested_company is not None:
                        validated_data["company"] = company
                    if "parent_category" in validated_data:
                        validated_data["parent_category"] = parent
                return super().update(locked_instance, validated_data)
        except IntegrityError as error:
            validation_error = self._integrity_validation_error(error)
            if validation_error is not None:
                raise validation_error from error
            raise

    @staticmethod
    def _lock_companies(company_ids):
        # 階層変更だけを企業単位で直列化し、通常の作成・名前更新は妨げない。
        return {
            company.id: company
            for company in Company.objects.select_for_update(no_key=True)
            .filter(id__in=company_ids)
            .order_by("id")
        }

    @staticmethod
    def _integrity_validation_error(error):
        # PostgreSQLの制約名とSQLSTATEから、競合した項目に対応する400を生成する。
        database_error = error.__cause__
        diagnostic = getattr(database_error, "diag", None)
        constraint_name = getattr(diagnostic, "constraint_name", None) or ""
        sqlstate = getattr(database_error, "pgcode", None)

        if constraint_name == "unique_company_category_combination":
            return serializers.ValidationError(
                {"non_field_errors": ["同じ企業に同名のカテゴリが既に存在します。"]}
            )
        if sqlstate == "23503":
            if "parent_category_id" in constraint_name:
                return serializers.ValidationError(
                    {"parent_category": "指定された親カテゴリは存在しません。"}
                )
            if "company_id" in constraint_name:
                return serializers.ValidationError(
                    {"company": "指定された企業は存在しません。"}
                )
            return serializers.ValidationError(
                {"non_field_errors": ["指定された参照先は存在しません。"]}
            )
        return None
