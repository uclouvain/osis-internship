# Generated by Django 3.1.1 on 2021-02-12 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('internship', '0098_internshipmaster_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='period',
            name='sent_reminder_mail',
            field=models.BooleanField(default=False),
        ),
    ]
