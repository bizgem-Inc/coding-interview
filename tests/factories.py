import factory
from factory.django import DjangoModelFactory
from api.models import Category, Company


class CompanyFactory(DjangoModelFactory):
    class Meta:
        model = Company

    name = factory.Sequence(lambda n: f"Company {n}")


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Category {n}")
    company = factory.SubFactory(CompanyFactory)
    parent_category = None
