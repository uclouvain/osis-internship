from django.db import models

from osis_common.models.serializable_model import SerializableModel


class Cohort(SerializableModel):
    name = models.CharField(max_length=255, null=False)
    description = models.TextField(null=False)
    free_internships_number = models.IntegerField(blank=False)
    publication_start_date = models.DateField(blank=False)
    subscription_start_date = models.DateField(blank=False)
    subscription_end_date = models.DateField(blank=False)

    def __str__(self):
        return self.name
