# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-08-01 15:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('internship', '0081_auto_20190724_1107'),
    ]

    operations = [
        migrations.AddField(
            model_name='internshipstudentaffectationstat',
            name='internship_evaluated',
            field=models.BooleanField(default=False),
        ),
    ]
