import factory
import factory.django

from base.tests.factories.learning_unit import LearningUnitFactory


class SpecialityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'internship.InternshipSpeciality'

    name = factory.Faker('name')
    acronym = 'QWERTY'
    mandatory = False
    order_postion = factory.Faker('random_int', min=1, max=10)

    learning_unit = factory.SubFactory(LearningUnitFactory)
