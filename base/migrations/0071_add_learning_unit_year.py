# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from base.models import attribution, learning_unit_year
import django.db.models.deletion


def copy_learning_unit_to_learning_unit_year(apps, schema_editor):
    attributions = attribution.Attribution.objects.all()

    for attrib in attributions:
        attrib.learning_unit_year = learning_unit_year.search(learning_unit=attrib.learning_unit)\
            .order_by("academic_year").last()
        attrib.save()


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0069_auto_20160831_1551'),
    ]

    operations = [
        migrations.AddField(
            model_name='attribution',
            name='learning_unit_year',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    to='base.LearningUnitYear'),
        ),
        migrations.RunPython(copy_learning_unit_to_learning_unit_year),
        migrations.RemoveField(
            model_name='attribution',
            name='learning_unit',
        ),
    ]