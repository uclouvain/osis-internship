# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-05 09:13
from __future__ import unicode_literals

import uuid

from django.db import migrations, models

from internship.migrations.utils.uuid import set_uuid_field_2


class Migration(migrations.Migration):
    dependencies = [
        ('internship', '0031_add_uuid_field_period_places'),
    ]

    operations = [
        migrations.RunPython(set_uuid_field_2, elidable=True),

        migrations.AlterField(
            model_name='periodinternshipplaces',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
