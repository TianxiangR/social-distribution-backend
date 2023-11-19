# Generated by Django 4.2.6 on 2023-11-18 04:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Inbox',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('type', models.CharField(choices=[('SHARE_POST', 'SHARE_POST'), ('COMMENT', 'COMMENT'), ('FOLLOW', 'FOLLOW'), ('LIKE_POST', 'LIKE_POST'), ('LIKE_COMMENT', 'LIKE_COMMENT')], max_length=50)),
                ('is_read', models.BooleanField(default=False)),
                ('actor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inbox_as_actor', to=settings.AUTH_USER_MODEL)),
                ('comment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='inbox', to='api.comment')),
                ('follow', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='inbox', to='api.follow')),
                ('like_comment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='inbox', to='api.likecomment')),
                ('like_post', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='inbox', to='api.likepost')),
                ('post', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='inbox', to='api.post')),
                ('target', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inbox_as_target', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
