import factory
import factory.django
import pendulum

from internship.tests.factories.organization import OrganizationFactory


class MasterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'internship.InternshipMaster'

    organization = factory.SubFactory(OrganizationFactory)
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')

    reference = factory.Sequence(lambda n: 'Master %s %d' % (pendulum.now().format('%H:%M:%S'), n))
    civility = factory.Faker('prefix')
    type_mastery = 'Nothing'
    speciality = 'Nothing'