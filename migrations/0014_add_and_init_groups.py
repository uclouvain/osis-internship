# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-07-02 16:58
from __future__ import unicode_literals

from django.db import migrations

from internship.migrations.utils.groups import add_init_internship_manager_group


class Migration(migrations.Migration):

    dependencies = [
        ('internship', '0013_create_internship_access_perm'),
        ('contenttypes', '__latest__'),
    ]

    operations = [
        migrations.RunPython(add_init_internship_manager_group, elidable=True),
    ]
