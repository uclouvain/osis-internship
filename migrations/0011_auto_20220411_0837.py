# Generated by Django 2.2.24 on 2022-04-11 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('internship', '0010_alter_placeevaluationitem_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='placeevaluationitem',
            name='order',
            field=models.PositiveIntegerField(db_index=True, editable=False),
        ),
    ]
