from django.contrib import admin
from .models import User, Post, Follow, Comment, LikePost, PostAccessPermission, PostAccessPermissionForeign, FollowForeign, Inbox

# Register your models here.
admin.site.register(User)
admin.site.register(Post)
admin.site.register(Follow)
admin.site.register(Comment)
admin.site.register(LikePost)
admin.site.register(PostAccessPermission)
admin.site.register(PostAccessPermissionForeign)
admin.site.register(FollowForeign)
admin.site.register(Inbox)
