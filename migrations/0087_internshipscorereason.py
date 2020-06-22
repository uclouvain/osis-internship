# Generated by Django 2.2.10 on 2020-06-22 14:06

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('internship', '0086_internshipscore_excused'),
    ]

    operations = [
        migrations.CreateModel(
            name='InternshipScoreReason',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('text', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]