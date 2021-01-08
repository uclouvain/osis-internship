# Generated by Django 3.1.1 on 2021-01-08 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('internship', '0094_move_master_address_to_person_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='internshipmaster',
            name='user_account_status',
            field=models.CharField(choices=[('inactive', 'inactive'), ('pending', 'pending'), ('active', 'active')], default='inactive', max_length=50),
        ),
    ]
