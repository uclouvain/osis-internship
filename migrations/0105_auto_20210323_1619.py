# Generated by Django 3.1.1 on 2021-03-23 16:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('internship', '0104_auto_20210323_1549'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='internshipscore',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='internshipscore',
            name='cohort',
        ),
        migrations.RemoveField(
            model_name='internshipscore',
            name='period',
        ),
        migrations.RemoveField(
            model_name='internshipscore',
            name='student',
        ),
    ]
