# Generated by Django 2.2.13 on 2022-02-16 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('internship', '0006_auto_20220120_1428'),
    ]

    operations = [
        migrations.AddField(
            model_name='period',
            name='remedial',
            field=models.BooleanField(default=False),
        ),
    ]
