from django.db import models
from django.contrib.auth.models import AbstractUser
from backend.settings import MEDIA_URL
import uuid
from django.core.exceptions import ValidationError

# Create your models here.
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, unique=True, editable=False, default=uuid.uuid4)
    profile_image = models.ImageField(upload_to=MEDIA_URL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_foreign = models.BooleanField(default=False)
    host = models.CharField(max_length=50, null=True, blank=True)
    foreign_id = models.URLField(unique=True)
    foreign_profile_image = models.URLField(null=True, blank=True)

class Post(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, editable=False, default=uuid.uuid4)
    title = models.CharField(max_length=50)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.CharField(max_length=int(1e8), blank=True)
    visibility = models.CharField(max_length=50, choices=[('PUBLIC', 'PUBLIC'), ('FRIENDS', 'FRIENDS'), ('PRIVATE', 'PRIVATE')], default='PUBLIC')  
    created_at = models.DateTimeField(auto_now_add=True)
    contentType = models.CharField(max_length=50, choices=[('text/plain', 'text/plain'), ('text/markdown', 'text/markdown'), ('image', 'image')], default='text/plain')
    origin = models.URLField()
    source = models.URLField()
    unlisted = models.BooleanField(default=False)

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_relations')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower_relations')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Define two fields "unique" as couple
    # source: https://stackoverflow.com/questions/54806874/django-unique-together-with-foreign-keys
    class Meta:
        unique_together = ('follower', 'following')
    
class PostAccessPermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_access_permissions')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_access_permissions')
    author_follow_relation = models.ForeignKey(Follow, on_delete=models.CASCADE, related_name='granted_post_access_permissions')
    target_follow_relation = models.ForeignKey(Follow, on_delete=models.CASCADE, related_name='receceived_post_access_permissions')
    
    class Meta:
        unique_together = ('user', 'post')
    
class LikePost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'post')

class Comment(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    is_private = models.BooleanField(default=False)
    
class LikeComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_likes')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'comment')
    
class Notification(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, editable=False, default=uuid.uuid4)
    type = models.CharField(max_length=50, choices=[('LIKE_POST', 'LIKE_POST'), ('LIKE_COMMENT', 'LIKE_COMMENT'), ('COMMENT_POST', 'COMMENT_POST'), ('SHARE_POST', 'SHARE_POST')])
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'notifications')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'notifications_sent')
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Inbox(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, editable=False, default=uuid.uuid4)
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inbox_as_actor')
    target = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inbox_as_target')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='inbox', null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='inbox', null=True, blank=True)
    follow = models.ForeignKey(Follow, on_delete=models.CASCADE, related_name='inbox', null=True, blank=True)
    like_post = models.ForeignKey(LikePost, on_delete=models.CASCADE, related_name='inbox', null=True, blank=True)
    like_comment = models.ForeignKey(LikeComment, on_delete=models.CASCADE, related_name='inbox', null=True, blank=True)
    type = models.CharField(max_length=50, choices=[('SHARE_POST', 'SHARE_POST'), ('COMMENT', 'COMMENT'), ('FOLLOW', 'FOLLOW'), ('LIKE_POST', 'LIKE_POST'), ('LIKE_COMMENT', 'LIKE_COMMENT')])
    is_read = models.BooleanField(default=False)
