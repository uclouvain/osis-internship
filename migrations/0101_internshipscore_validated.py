# Generated by Django 3.1.1 on 2021-03-04 09:45
import operator
from functools import reduce

from django.db import migrations, models
from django.db.migrations import RunPython
from django.db.models import Q

APD_NUMBER = 15


def validate_existing_filled_scores(apps, schema_editor):
    InternshipScore = apps.get_model('internship', 'InternshipScore')

    has_at_least_one_apd_evaluated = reduce(
        operator.or_, [Q(**{'APD_{}__isnull'.format(index): False}) for index in range(1, APD_NUMBER + 1)]
    )
    # validate existing APD if has at least one apd evaluated
    InternshipScore.objects.filter(has_at_least_one_apd_evaluated).update(validated=True)


class Migration(migrations.Migration):

    dependencies = [
        ('internship', '0100_auto_20210224_1542'),
    ]

    operations = [
        migrations.AddField(
            model_name='internshipscore',
            name='validated',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(validate_existing_filled_scores, RunPython.noop,elidable=True),
    ]
