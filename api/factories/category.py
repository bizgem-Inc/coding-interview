import factory.django

from api.factories.company import CompanyFactory
from api.models.category import Category


class CategoryFactory(factory.django.DjangoModelFactory):
    company = factory.SubFactory(CompanyFactory)
    name = factory.Sequence(lambda n: "カテゴリ名_%s" % n)
    parent_category = factory.SubFactory('api.factories.category.CategoryFactory')

    class Meta:
        model = Category
