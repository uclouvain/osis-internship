# Generated by Django 3.2.12 on 2022-04-12 16:34
from datetime import datetime

import requests
from django.conf import settings
from django.db import migrations, models
from django.db.migrations import RunPython

from internship.models.enums.user_account_status import UserAccountStatus


def retrieve_master_user_account_expiration_date(apps, schema_editor):
    InternshipMaster = apps.get_model('internship', 'InternshipMaster')
    for master in InternshipMaster.objects.exclude(
            user_account_status=UserAccountStatus.INACTIVE.name,
            user_account_expiration_date__isnull=True
    ):
        response = requests.get(
            headers={'Content-Type': 'application/json'},
            url=settings.LDAP_ACCOUNT_DESCRIPTION_URL + str(master.person.uuid)
        )
        if response.json()['id'] == str(master.person.uuid) and 'status' not in response.json().keys():
            input_validity = datetime.strptime(response.json()['validite'], '%Y%m%d')
            master.user_account_expiration_date = input_validity.strftime('%Y-%m-%d')
            master.save()


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
        migrations.RunPython(retrieve_master_user_account_expiration_date, RunPython.noop, elidable=True),
    ]
