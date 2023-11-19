import factory.fuzzy
from api.models import (
    category,
    company
)

factory.Faker._DEFAULT_LOCALE = 'ja_JP'


class CompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = company.Company

    id = factory.Faker('uuid4')
    name = factory.Faker('company')


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = category.Category

    id = factory.Faker('uuid4')
    name = factory.Faker('job')
    company = factory.SubFactory(CompanyFactory)
    parent_category = None

    class Params:
        with_parent_category = factory.Trait(
            parent_category=factory.SubFactory(
                'api.tests.factories.CategoryFactory'),
        )
