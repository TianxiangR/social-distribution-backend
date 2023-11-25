# Generated by Django 4.2.6 on 2023-11-25 07:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_delete_sharedpost'),
    ]

    operations = [
        migrations.CreateModel(
            name='SharedPost',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('title', models.CharField(max_length=50)),
                ('content', models.TextField(blank=True)),
                ('visibility', models.CharField(choices=[('PUBLIC', 'PUBLIC'), ('FRIENDS', 'FRIENDS'), ('PRIVATE', 'PRIVATE')], default='PUBLIC', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('contentType', models.CharField(choices=[('text/plain', 'text/plain'), ('text/markdown', 'text/markdown'), ('image', 'image')], default='text/plain', max_length=50)),
                ('origin', models.URLField()),
                ('source', models.URLField()),
                ('unlisted', models.BooleanField(default=False)),
                ('image', models.ImageField(blank=True, null=True, upload_to='media/')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shared_posts', to=settings.AUTH_USER_MODEL)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_posts', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
