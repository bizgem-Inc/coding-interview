import factory.django

from api.models.company import Company


class CompanyFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("company", locale="ja_JP")

    class Meta:
        model = Company
