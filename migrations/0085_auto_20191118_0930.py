# Generated by Django 2.2.5 on 2019-11-18 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('internship', '0084_auto_20190821_1427'),
    ]

    operations = [
        migrations.AlterField(
            model_name='internshipscore',
            name='score',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='internshipstudentinformation',
            name='evolution_score',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
