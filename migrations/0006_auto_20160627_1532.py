# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-06-27 13:32
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0055_message_history_modifications'),
        ('internship', '0005_internshipoffer_selectable'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='internshipenrollment',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='internshipenrollment',
            name='start_date',
        ),
        migrations.AddField(
            model_name='internshipchoice',
            name='priority',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='internshipenrollment',
            name='period',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='internship.Period'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='internshipenrollment',
            name='place',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='internship.Organization'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='internshipenrollment',
            name='student',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='base.Student'),
            preserve_default=False,
        ),
    ]
