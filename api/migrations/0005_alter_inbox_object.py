# Generated by Django 4.2.6 on 2023-11-23 23:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_inbox_actor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inbox',
            name='object',
            field=models.URLField(blank=True, null=True),
        ),
    ]