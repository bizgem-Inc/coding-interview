import uuid

from factory import LazyAttribute, SubFactory
from factory.django import DjangoModelFactory

from api.models import (
    Category,
    Company,
)


def create_unique_id():
    return str(uuid.uuid4())


class CompanyFactory(DjangoModelFactory):
    class Meta:
        model = Company

    id = LazyAttribute(lambda _: create_unique_id())
    name = LazyAttribute(lambda n: f'name_{n.id}')


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    id = LazyAttribute(lambda _: create_unique_id())
    company = SubFactory(CompanyFactory)
    name = LazyAttribute(lambda n: f'name_{n.id}')
    parent_category = None
