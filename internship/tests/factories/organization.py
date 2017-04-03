import factory
import factory.fuzzy

from django.utils.text import slugify

from internship.tests.factories.cohort import CohortFactory


class OrganizationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'internship.Organization'

    name = factory.Sequence(lambda n: 'Organization %d' % (n,))
    acronym = factory.LazyAttribute(lambda o: slugify(o.name)[:15])
    website = factory.Faker('url')

    cohort = factory.SubFactory(CohortFactory)