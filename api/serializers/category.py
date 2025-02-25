from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            'id',
            'company',
            'name',
            'parent_category',
        )

    def validate_company(self, company):
        if not self.instance:
            return company

        if company != self.instance.company and \
           Category.objects.filter(parent_category=self.instance).count() > 0:
            # サブカテゴリがある場合は企業の更新が出来ない仕様にした
            raise ValidationError(
                'The company cannot be updated because it has subcategories.',
                code='has_subcategories',
            )

        return company

    def validate(self, data):
        company = data.get('company')
        name = data.get('name')
        parent_category = data.get('parent_category')
        if self.instance:
            company = company or self.instance.company
            name = name or self.instance.name
            parent_category = parent_category or self.instance.parent_category

        categories = Category.objects.filter(
            company=company.id,
            name=name,
        )
        if self.instance:
            categories = categories.exclude(id=self.instance.id)

        if categories.count() > 0:
            raise ValidationError(
                {'name': 'The name is duplicated.'},
                code='duplicated',
            )

        if parent_category:
            # 親カテゴリの企業IDと企業IDが一致しない場合
            if parent_category.company.id != company.id:
                raise ValidationError(
                    {
                        'parent_category': (
                            'The parent category company ID and '
                            'the company ID do not match.'
                        ),
                    },
                    code='invalid',
                )

        return data
