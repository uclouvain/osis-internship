# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-04-05 18:48
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('internship', '0042_internshipoffer_cohort'),
    ]

    operations = [
        migrations.AlterField(
            model_name = 'internshipenrollment',
            name       = 'internship_choice',
            field      = models.IntegerField(db_column="internship_choice")
        ),
        migrations.RenameField(
            model_name = 'internshipenrollment',
            old_name   = 'internship_choice',
            new_name   = 'internship'
        ),
        migrations.AlterField(
            model_name = 'internshipenrollment',
            name       = 'internship',
            field      = models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='internship.Internship')
        )
    ]
