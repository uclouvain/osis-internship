# Generated by Django 3.2.16 on 2022-11-30 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('internship', '0019_internshipcertifier'),
    ]

    operations = [
        migrations.AlterField(
            model_name='internshipcertifier',
            name='signature_b64',
            field=models.TextField(blank=True, null=True),
        ),
    ]
