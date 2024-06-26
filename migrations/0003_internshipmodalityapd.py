# Generated by Django 3.2.25 on 2024-04-15 16:32

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('internship', '0002_organization_report_master'),
    ]

    operations = [
        migrations.CreateModel(
            name='InternshipModalityApd',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('apd', models.IntegerField()),
                ('internship', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='internship.internship'
                                                 )),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
