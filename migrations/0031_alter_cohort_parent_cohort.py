# Generated by Django 3.2.18 on 2023-09-21 16:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('internship', '0030_auto_20230920_1519'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cohort',
            name='parent_cohort',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='subcohorts', to='internship.cohort'),
        ),
    ]