# Generated by Django 3.2.18 on 2023-09-21 16:14

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('internship', '0031_alter_cohort_parent_cohort'),
    ]

    operations = [
        migrations.CreateModel(
            name='InternshipModalityPeriod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('internship', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='internship.internship')),
                ('period', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='internship.period')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]