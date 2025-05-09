# Generated by Django 4.2.16 on 2024-12-03 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('internship', '0003_internshipmodalityapd'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='organization',
            name='report_gender',
        ),
        migrations.AlterField(
            model_name='organization',
            name='report_address',
            field=models.IntegerField(blank=True, default=11, null=True),
        ),
        migrations.AlterField(
            model_name='organization',
            name='report_birthdate',
            field=models.IntegerField(blank=True, default=7, null=True),
        ),
        migrations.AlterField(
            model_name='organization',
            name='report_city',
            field=models.IntegerField(blank=True, default=13, null=True),
        ),
        migrations.AlterField(
            model_name='organization',
            name='report_email',
            field=models.IntegerField(blank=True, default=8, null=True),
        ),
        migrations.AlterField(
            model_name='organization',
            name='report_master',
            field=models.IntegerField(blank=True, default=14, null=True),
        ),
        migrations.AlterField(
            model_name='organization',
            name='report_noma',
            field=models.IntegerField(blank=True, default=9, null=True),
        ),
        migrations.AlterField(
            model_name='organization',
            name='report_phone',
            field=models.IntegerField(blank=True, default=10, null=True),
        ),
        migrations.AlterField(
            model_name='organization',
            name='report_postal_code',
            field=models.IntegerField(blank=True, default=12, null=True),
        ),
        migrations.AlterField(
            model_name='organization',
            name='report_specialty',
            field=models.IntegerField(blank=True, default=6, null=True),
        ),
    ]
