# Generated by Django 3.2.16 on 2023-01-09 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('internship', '0025_placeevaluationitem_required'),
    ]

    operations = [
        migrations.AddField(
            model_name='period',
            name='place_evaluation_active',
            field=models.BooleanField(default=False),
        ),
    ]
