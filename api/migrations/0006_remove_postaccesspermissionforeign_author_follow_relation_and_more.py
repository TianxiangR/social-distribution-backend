# Generated by Django 4.2.6 on 2023-11-23 23:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_alter_inbox_object'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='postaccesspermissionforeign',
            name='author_follow_relation',
        ),
        migrations.RemoveField(
            model_name='postaccesspermissionforeign',
            name='target_follow_relation',
        ),
    ]