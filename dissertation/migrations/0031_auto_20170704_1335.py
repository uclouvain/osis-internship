# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-04 11:35
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dissertation', '0030_auto_20170503_1628'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='offerproposition',
            options={'ordering': ['offer_proposition_group', 'acronym']},
        ),
    ]
