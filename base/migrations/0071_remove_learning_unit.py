# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0070_add_learning_unit_year'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='learningunityear',
            name='learning_unit',
        ),
    ]
