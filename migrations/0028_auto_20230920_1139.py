# Generated by Django 3.2.18 on 2023-09-20 11:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('internship', '0027_auto_20230123_1652'),
    ]

    operations = [
        migrations.AddField(
            model_name='cohort',
            name='parent_cohort',
            field=models.ForeignKey(
                blank=True,
                null=True, on_delete=django.db.models.deletion.PROTECT, related_name='parent', to='internship.cohort'
            ),
        ),
        migrations.AlterField(
            model_name='cohort',
            name='publication_start_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='cohort',
            name='subscription_end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='cohort',
            name='subscription_start_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
