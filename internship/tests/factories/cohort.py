import factory
import factory.fuzzy


class CohortFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'internship.Cohort'

    name = factory.Sequence(lambda n: str(n))
    description = factory.fuzzy.FuzzyText()

