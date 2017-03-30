from django.db import models

from base.models.student import Student
from osis_common.models.serializable_model import SerializableModel


class Cohort(SerializableModel):
    name = models.CharField(max_length=64, null=False)
    description = models.TextField(null=False)

    students = models.ManyToManyField(Student)

    def __str__(self):
        return self.name