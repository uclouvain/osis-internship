import factory
import factory.django

from internship.tests.factories.organization import OrganizationFactory
from internship.tests.factories.speciality import SpecialityFactory
from internship.tests.factories.cohort import CohortFactory


class OfferFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'internship.InternshipOffer'

    organization = factory.SubFactory(OrganizationFactory)
    speciality = factory.SubFactory(SpecialityFactory)
    cohort = factory.SubFactory(CohortFactory)

    title = factory.Faker('sentence', nb_words=6, variable_nb_words=True)
    maximum_enrollments = factory.Faker('random_int', min=3, max=8)
    master = factory.Faker('name')
    selectable = factory.Faker('random_int')
