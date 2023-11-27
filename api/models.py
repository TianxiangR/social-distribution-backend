from django.db import models
from django.contrib.auth.models import AbstractUser
from backend.settings import MEDIA_URL
import uuid

# Create your models here.
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, unique=True, editable=False, default=uuid.uuid4)
    profile_image = models.ImageField(upload_to=MEDIA_URL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_server = models.BooleanField(default=False)
    github = models.URLField(null=True, blank=True)
    host = models.URLField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    is_foreign = models.BooleanField(default=False)
    image_url = models.URLField(null=True, blank=True)


class Post(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, editable=False, default=uuid.uuid4)
    title = models.CharField(max_length=50)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(blank=True)
    visibility = models.CharField(max_length=50, choices=[('PUBLIC', 'PUBLIC'), ('FRIENDS', 'FRIENDS'), ('PRIVATE', 'PRIVATE')], default='PUBLIC')  
    created_at = models.DateTimeField(auto_now_add=True)
    contentType = models.CharField(max_length=50, choices=[('text/plain', 'text/plain'), ('text/markdown', 'text/markdown'), ('image', 'image')], default='text/plain')
    origin = models.URLField()
    source = models.URLField()
    unlisted = models.BooleanField(default=False)
    image = models.ImageField(upload_to=MEDIA_URL, null=True, blank=True)
    is_foreign = models.BooleanField(default=False)


class PostAccess(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_access')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_access')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('post', 'user')


class Follow(models.Model):
    target = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followed_relations')
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_relations')
    
    class Meta:
        unique_together = ('target', 'follower')
        
        
class FriendRequest(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, editable=False, default=uuid.uuid4)
    target = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_requests')
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requested_friends')
    status = models.CharField(max_length=50, choices=[('ACCEPTED', 'ACCEPTED'), ('REJECTED', 'REJECTED'), ('PENDING', 'PENDING')], default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)


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
    
    
class LikeComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_likes')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'comment')
        

class InboxItem(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, editable=False, default=uuid.uuid4)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inbox_items')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_items')
    item = models.TextField()
    type = models.CharField(max_length=50, choices=[('Follow', 'Follow'), ('comment', 'comment'), ('post', 'post'), ('Like', 'Like')])



