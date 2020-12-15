# Generated by Django 3.1.1 on 2020-12-14 16:37

from django.db import migrations
from django.db.migrations import RunPython


def move_master_address_to_person_address(apps, schema_editor):
    InternshipMaster = apps.get_model('internship', 'InternshipMaster')
    PersonAddress = apps.get_model('base', 'PersonAddress')

    for master in InternshipMaster.objects.all():
        if master.person and not PersonAddress.objects.filter(person=master.person).exists():
            PersonAddress.objects.create(
                person=master.person,
                location=master.location,
                postal_code=master.postal_code,
                city=master.city,
                country=master.country
            )


class Migration(migrations.Migration):

    dependencies = [
        ('internship', '0093_internshipmaster_person'),
    ]

    operations = [
        migrations.RunPython(move_master_address_to_person_address, RunPython.noop),
        migrations.RemoveField(
            model_name='internshipmaster',
            name='city',
        ),
        migrations.RemoveField(
            model_name='internshipmaster',
            name='country',
        ),
        migrations.RemoveField(
            model_name='internshipmaster',
            name='location',
        ),
        migrations.RemoveField(
            model_name='internshipmaster',
            name='postal_code',
        ),
    ]
