import factory
import factory.fuzzy


class CohortFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'internship.Cohort'

    name = factory.Sequence(lambda n: 'Cohort %d' % (n,))
    description = factory.fuzzy.FuzzyText()

