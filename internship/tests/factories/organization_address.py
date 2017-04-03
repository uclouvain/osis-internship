import factory
import factory.fuzzy
from django.utils.text import slugify

from internship.tests.factories.organization import OrganizationFactory


class OrganizationAddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'internship.OrganizationAddress'

    label = factory.Faker('company')
    location = factory.Faker('street_address')
    postal_code = factory.Faker('postalcode')
    city = factory.Faker('city')
    latitude = factory.Faker('latitude')
    longitude = factory.Faker('longitude')
    country = factory.Faker('country')

    organization = factory.SubFactory(OrganizationFactory)