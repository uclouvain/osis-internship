# Generated by Django 3.2.12 on 2022-04-12 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('internship', '0012_alter_placeevaluationitem_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='internshipmaster',
            name='user_account_expiration_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
