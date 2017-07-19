# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from base.models import learning_unit_year
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0070_scoresencoding'),
    ]

    operations = [
        migrations.AddField(
            model_name='attribution',
            name='learning_unit_year',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    to='base.LearningUnitYear'),
        ),
        migrations.RemoveField(
            model_name='attribution',
            name='learning_unit',
        ),
    ]