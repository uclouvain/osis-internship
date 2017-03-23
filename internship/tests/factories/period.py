import factory
import factory.fuzzy
import pendulum

from internship.tests.factories.cohort import CohortFactory


class PeriodFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'internship.Period'

    name = factory.Sequence(lambda n: str(n))

    date_start = factory.LazyAttribute(lambda obj: pendulum.today().start_of('month')._datetime)
    date_end = factory.LazyAttribute(lambda obj: pendulum.instance(obj.date_start).end_of('month')._datetime)
    cohort = factory.SubFactory(CohortFactory)
