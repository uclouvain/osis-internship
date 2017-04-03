import factory
import factory.django

from base.tests.factories.learning_unit import LearningUnitFactory
from internship.tests.factories.cohort import CohortFactory


class SpecialityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'internship.InternshipSpeciality'

    name = factory.Faker('name')
    acronym = factory.Sequence(lambda n: 'SPEC-%d' % n)
    mandatory = False
    order_postion = factory.Faker('random_int', min=1, max=10)

    # cohort = factory.SubFactory(CohortFactory)
    learning_unit = factory.SubFactory(LearningUnitFactory)
