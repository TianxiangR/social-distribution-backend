from django.contrib import admin
from .models import User, Post, Follower, Comment, LikePost, LikeComment

# Register your models here.
admin.site.register(User)
admin.site.register(Post)
admin.site.register(Follower)
admin.site.register(Comment)
admin.site.register(LikePost)
admin.site.register(LikeComment)