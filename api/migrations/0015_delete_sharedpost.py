# Generated by Django 4.2.6 on 2023-11-25 07:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_sharedpost_receiver'),
    ]

    operations = [
        migrations.DeleteModel(
            name='SharedPost',
        ),
    ]