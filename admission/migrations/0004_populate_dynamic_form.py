# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.core.exceptions import FieldDoesNotExist
from django.db import migrations

from admission.models.form import Form
from admission.models.option import Option
from admission.models.question import Question


def set_uuid_field(apps, schema_editor):
    """
    Set a random uuid value to all existing rows in all models containing an 'uuid' attribute in database.
    """
    model_classes = [Form, Option, Question]
    for model_class in model_classes:
        ids = model_class.objects.values_list('id', flat=True)
        if ids:
            for pk in ids:
                try:
                    model_class.objects.filter(pk=pk).update(uuid=uuid.uuid4())
                except FieldDoesNotExist:
                    break


class Migration(migrations.Migration):

    dependencies = [
        ('admission', '0003_auto_20161108_1220'),
    ]

    operations = [
        migrations.RunPython(set_uuid_field),
    ]
